import traceback

import streamlit as st
from urllib.parse import quote_plus

import recruiterblast.config as cfg
from recruiterblast.api import GoogleGeminiAPIClient
from recruiterblast.logger import setup_logger
from recruiterblast.models import Company, JobPost
from recruiterblast.parsers import (
    parse_emails_from_text,
    parse_linkedin_job_url,
    parse_rocket_reach_email_format,
)
from recruiterblast.scrapers import GoogleSearchScraper, LinkedInScraper
from recruiterblast.utils import (
    generate_formatted_employee_email,
    generate_rocketreach_formatted_username,
    generate_email_subject_and_body,
)

from streamlit_feedback import streamlit_feedback

log = setup_logger(__name__)


def display_company_email_search_button(domain: str):
    url = f"https://www.google.com/search?q=site:{domain}+%22@{domain}%22"
    st.markdown(
        f'<a href="{url}" target="_blank"><button style="background-color: #F63366; color: white; padding: 10px 20px; border: none; border-radius: 5px;">Search {domain} Emails</button></a>',
        unsafe_allow_html=True,
    )


def display_job_post_section(scraper: LinkedInScraper) -> JobPost:
    job_post = (
        scraper.fetch_job_post_details()
        if cfg.ENV == "prod"
        else JobPost(
            id=1,
            title="SWE",
            description="You will work for money. Python.",
            post_date="2024-01-01T12:12:12",
            apply_url="foobar.com",
            is_remote=True,
            location="Houston",
        )
    )
    client = GoogleGeminiAPIClient()
    description_attrs = (
        client.parse_relevant_job_description_info(job_post.description)
        if cfg.IS_PROD
        else {
            "core_responsibilities": ["code"],
            "technical_requirements": ["python"],
            "soft_skills": ["learn"],
            "highlights": ["money"],
        }
    )

    job_post.responsibilities = description_attrs.get("core_responsibilities", "")
    job_post.technical_requirements = description_attrs.get(
        "technical_requirements", ""
    )
    job_post.soft_skills = description_attrs.get("soft_skills", "")
    job_post.highlights = description_attrs.get("highlights", "")
    job_post.job_url = scraper.job_post_url
    job_post.description = ""

    st.subheader("Job Post Information")
    st.table(job_post.as_df())

    return job_post


def display_company_section(scraper: LinkedInScraper) -> Company:
    company = (
        scraper.fetch_company_from_job_post()
        if cfg.IS_PROD
        else scraper.generate_mock_company()
    )

    st.subheader("Company Information")
    st.table(company.as_df())

    return company


def display_suggested_email_format_section(company: Company):
    leadiq_snippet = "The Company ABC's email format is First.Last@companyabc.com;"
    rocket_snippet = "The Company ABC's email format is [first].[last] (test)."

    if cfg.IS_PROD:
        google_scraper = GoogleSearchScraper()
        leadiq_snippet = google_scraper.scrape_leadiq_suggested_email_format(
            company.domain
        )
        rocket_snippet = google_scraper.scrape_rocketreach_suggested_email_format(
            company.domain
        )

    email_format = None

    if any([leadiq_snippet, rocket_snippet]):
        st.subheader("Email Format")

        if leadiq_snippet:
            st.write(f"Per LeadIQ.com: {leadiq_snippet}")
            email_format = parse_emails_from_text(leadiq_snippet)
            email_format = email_format[0] if email_format else None

        if rocket_snippet:
            st.write(f"Per RocketReach.co: {rocket_snippet}")
            email_format = parse_rocket_reach_email_format(rocket_snippet)

    return email_format


def display_recruiters_section(
    scraper, company, job_post, email_format, subject_override="", body_override=""
):
    recruiters = (
        scraper.fetch_recruiters_from_company(company)
        if cfg.IS_PROD
        else scraper.generate_mock_recruiters()
    )

    st.subheader("Recruiters")

    for recruiter in recruiters:
        subject, body = generate_email_subject_and_body(company, recruiter, job_post)
        if subject_override:
            subject = quote_plus(subject_override).replace("+", "%20")
        if body_override:
            body = quote_plus(body_override).replace("+", "%20")
        if email_format and email_format.startswith("["):
            username = generate_rocketreach_formatted_username(recruiter, email_format)
            email = f"{username}@{company.domain}"
            emails = [email]
        elif email_format:
            emails = [generate_formatted_employee_email(recruiter, email_format)]
        else:
            emails = recruiter.generate_email_permutations(company.domain)

        with st.container():
            st.markdown(
                f"<div style='border: 1px solid #ddd; padding: 10px; border-radius: 8px; margin-bottom: 15px;'>"
                f"<strong>{recruiter.full_name}</strong> | {recruiter.locale} | "
                f"<a href='{recruiter.profile_url}' target='_blank'>Profile</a> | "
                f"<a href='https://mail.google.com/mail/?view=cm&fs=1&to={','.join(emails)}&su={subject}&body={body}' target='_blank'>Send Email</a>"
                f"<br><em>{recruiter.headline}</em>"
                f"</div>",
                unsafe_allow_html=True,
            )


def display_feedback_section():
    st.subheader("Feedback")
    st.write(f"Your feedback is appreciated!")
    streamlit_feedback(
        feedback_type="thumbs",
        optional_text_label="[Optional] Please provide an explanation",
        align="flex-start",
    )


def main():
    st.set_page_config(page_title="DeepRecruiter.io", page_icon="🌑")

    st.title("🌑 DeepRecruiter.io")

    st.subheader("Find recruiters from job posts, prepare your pitch, and send emails.")

    job_url = st.text_input(
        "Job URL", placeholder="https://www.linkedin.com/jobs/view/4133654166"
    )

    subject_override = st.text_input(
        "Email subject", placeholder="I am a fit for this role."
    )
    body_override = st.text_area("Email body", placeholder="This is why.")

    st.markdown(
        "<p style='color: gray;'>No worries, we don’t store your data. "
        "All information is only used during your session and isn’t saved anywhere.</p>",
        unsafe_allow_html=True,
    )

    if st.button("Find Recruiters", type="primary"):

        if job_url:
            job_url = parse_linkedin_job_url(job_url)
            if not job_url:
                st.error(
                    "Please enter a valid LinkedIn URL (e.g., 'https://www.linkedin.com/jobs/view/4133654166')"
                )
            else:
                try:
                    scraper = LinkedInScraper(job_url)

                    job_post = display_job_post_section(scraper)
                    company = display_company_section(scraper)
                    email_format = display_suggested_email_format_section(company)
                    display_recruiters_section(
                        scraper,
                        company,
                        job_post,
                        email_format,
                        subject_override,
                        body_override,
                    )
                    display_feedback_section()

                except Exception as e:
                    message = "Failed to fetch company and recruiter data"
                    st.error(message)
                    log.error(f"{message}, {e}, {traceback.format_exc()}")
        else:
            st.error("Job URL is required!")


if __name__ == "__main__":
    main()
