import traceback
from urllib.parse import quote_plus

import streamlit as st

import recruiterblast.config as cfg
from recruiterblast.api import GoogleGeminiAPIClient
from recruiterblast.logger import setup_logger
from recruiterblast.models import Company, Employee, JobPost
from recruiterblast.parsers import (
    parse_emails_from_text,
    parse_linkedin_job_url,
    parse_rocket_reach_email_format,
)
from recruiterblast.scrapers import GoogleSearchScraper, LinkedInScraper
from recruiterblast.utils import (
    generate_formatted_employee_email,
    generate_rocketreach_formatted_username,
)

log = setup_logger(__name__)


def generate_email_subject_and_body(
    company: Company, recruiter: Employee, job_post: JobPost
) -> tuple[str, str]:
    subject = f"👋 I'm 92.5% Fit for Your {job_post.title} Role!"
    body = (
        f"Hi {recruiter.first_name},\n\n"
        f"I value your time, so I’ll keep this brief! My name is Bryan, and "
        f"I recently applied for the {job_post.title} role at {company.name} [1]. "
        f"I noticed you're on the recruiting team, so I thought I’d reach out in case my "
        f"application gets lost in the shuffle.\n\n"
        f"Here’s a high-level overview of my experience:\n\n"
        f"   ➡️ 4+ years as a backend software engineer\n"
        f"   ➡️ Previously at Bank of America (BofA)\n"
        f"   ➡️ Saved BofA $221K by fixing a memory leak in pipeline processing 10M+ trades.\n"
        f"   ➡️ Launched BigBagData.com, an analytics platform for vintage bags (boosted a store's sales by 31%!)\n"
        f"   ➡️ Relevant tech I've worked with: Python, Flask, SQL, DBT, Airflow, AWS, Apache Iceberg\n\n"
        f"Lastly, I completed Zach Wilson's data engineering bootcamp in Q4 2024 where I was awarded the "
        f"‘Superbness Certificate’ and ‘Outstanding Capstone,’ honors presented to top 1% of class. The "
        f"coursework included conceptual data modeling, slowly changing dimensions (SCDs), cumulative table design, "
        f"write-audit-publish framework.\n\n"
        f"I’ve attached and included a link to my resume below if you’re interested in chatting [2]. "
        f"I look forward to hearing from you. Thanks!\n\n"
        f"[1]: {job_post.job_url}\n"
        f"[2]: bryangalindo.com/resume"
    )
    subject_encoded = quote_plus(subject).replace("+", "%20")
    body_encoded = quote_plus(body).replace("+", "%20")
    return subject_encoded, body_encoded


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

    job_post.responsibilities = "\n".join(
        description_attrs.get("core_responsibilities", "")
    )
    job_post.technical_requirements = "\n".join(
        description_attrs.get("technical_requirements", "")
    )
    job_post.soft_skills = "\n".join(description_attrs.get("soft_skills", ""))
    job_post.highlights = "\n".join(description_attrs.get("highlights", ""))
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


def display_recruiters_section(scraper, company, job_post, email_format):
    recruiters = (
        scraper.fetch_recruiters_from_company(company)
        if cfg.IS_PROD
        else scraper.generate_mock_recruiters()
    )

    st.subheader("Recruiters")

    for recruiter in recruiters:
        subject, body = generate_email_subject_and_body(company, recruiter, job_post)
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


def main():
    st.set_page_config(page_title="RecruiterBlast.dev", page_icon="🚀")

    st.title("Recruiter Blast 🚀")
    st.subheader("Find recruiters from job posts, prepare your pitch, and send emails!")

    job_url = st.text_input(
        "Job URL", placeholder="https://www.linkedin.com/jobs/view/4133654166"
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
                    display_recruiters_section(scraper, company, job_post, email_format)

                except Exception as e:
                    message = "Failed to fetch company and recruiter data"
                    st.error(message)
                    log.error(f"{message}, {e}, {traceback.format_exc()}")
        else:
            st.error("Job URL is required!")


if __name__ == "__main__":
    main()
