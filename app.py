import traceback
from urllib.parse import quote_plus

import streamlit as st

import recruiterblast.config as cfg
from recruiterblast.logger import setup_logger
from recruiterblast.models import Company, Employee, JobPost
from recruiterblast.parsers import parse_emails_from_text, parse_linkedin_job_url
from recruiterblast.scrapers import GoogleSearchScraper, LinkedInScraper
from recruiterblast.utils import generate_formatted_employee_email

log = setup_logger(__name__)


def generate_email_subject_and_body(
    company: Company, recruiter: Employee, job_post: JobPost
) -> tuple[str, str]:
    subject = f"👋 I'm 92.5% Fit for Your {job_post.title} Role!"
    body = (
        f"Hi {recruiter.first_name},\n\n"
        f"I value your time, so I’ll keep this brief! My name is Bryan, and "
        f"I recently applied for the {job_post.job_url} role at {company.name} [1]. "
        f"I noticed you're on the recruiting team, so I thought I’d reach out in case my "
        f"application gets lost in the shuffle.\n\n"
        f"Here’s a high-level overview of my experience:\n\n"
        f"   ➡️ 4+ years as a backend software engineer\n"
        f"   ➡️ Previously at Bank of America (BofA)\n"
        f"   ➡️ Saved BofA $221K by resolving a memory leak\n"
        f"   ➡️ Boosted a vintage store's sales by 31% with BigBagData.com\n"
        f"   ➡️ Relevant tech I've worked with: Python, Flask, SQL, DBT, Airflow, AWS\n\n"
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


def main():
    st.set_page_config(page_title="RecruiterBlast.dev", page_icon="🚀")

    st.title("Recruiter Blast 🚀")
    st.subheader("Find recruiters from job posts to send your pitch!")

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

                    job_post = (
                        scraper.fetch_job_post_details()
                        if cfg.ENV == "prod"
                        else JobPost(
                            id=1,
                            title="SWE",
                            description="You will work for money",
                            post_date="2024-01-01T12:12:12",
                            apply_url="foobar.com",
                            is_remote=True,
                            location="Houston",
                        )
                    )
                    job_post.job_url = job_url
                    st.subheader("Job Post Information")
                    st.table(job_post.as_df())

                    company, recruiters = (
                        scraper.generate_mock_company_recruiter_data()
                        if cfg.ENV != "prod"
                        else scraper.fetch_company_and_recruiter_data()
                    )

                    st.subheader("Company Information")
                    st.table(company.as_df())

                    if cfg.ENV != "prod":
                        suggested_email_format = (
                            "The Company ABC's email format usually follows "
                            "the pattern of First_Last@companyabc.com; "
                            "this email format is used 95% of the time."
                        )
                    else:
                        google_scraper = GoogleSearchScraper()
                        suggested_email_format = (
                            google_scraper.scrape_suggested_email_format(company.domain)
                        )

                    email_format = None

                    if suggested_email_format:
                        st.subheader("Email Format")
                        st.write(f"Per LeadIQ.com: {suggested_email_format}")
                        email_format = parse_emails_from_text(suggested_email_format)

                    st.subheader("Recruiters")

                    for recruiter in recruiters:
                        subject, body = generate_email_subject_and_body(
                            company, recruiter, job_post
                        )
                        if email_format:
                            emails = [
                                generate_formatted_employee_email(
                                    recruiter, email_format[0]
                                )
                            ]
                        else:
                            emails = recruiter.generate_email_permutations(
                                company.domain
                            )

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

                except Exception as e:
                    message = "Failed to fetch company and recruiter data"
                    st.error(message)
                    log.error(f"{message}, {e}, {traceback.format_exc()}")
        else:
            st.error("Job URL is required!")


if __name__ == "__main__":
    main()
