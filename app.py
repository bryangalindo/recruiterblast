import traceback
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st

import recruiterblast.config as cfg
from recruiterblast.logger import setup_logger
from recruiterblast.models import Company, Employee
from recruiterblast.parsers import parse_linkedin_job_url
from recruiterblast.scrapers import (
    BingSearchScraper,
    GoogleSearchScraper,
    LinkedInScraper,
)

log = setup_logger(__name__)


def generate_email_subject_and_body(
    company: Company, recruiter: Employee, job_url: str
) -> tuple[str, str]:
    subject = f"I am interested in {company.name}'s Software Engineer Role."
    body = f"Hello {recruiter.first_name},\nI just applied to {job_url}, and I think we're a fit."
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

                    company, recruiters = (
                        scraper.generate_mock_company_recruiter_data()
                        if cfg.ENV != "prod"
                        else scraper.fetch_company_and_recruiter_data()
                    )

                    st.subheader("Company Information")
                    st.table(company.as_df())

                    if cfg.ENV != "prod":
                        emails = ["email1@example.com", "email2@example.com"]
                    else:
                        bing_scraper = BingSearchScraper()
                        bing_emails = bing_scraper.scrape_emails_from_company_domain(
                            company.domain
                        )
                        google_scraper = GoogleSearchScraper()
                        google_emails = (
                            google_scraper.scrape_emails_from_company_domain(
                                company.domain
                            )
                        )
                        emails = set(bing_emails + google_emails)

                    st.subheader("Company Emails")
                    if emails:
                        st.write(
                            f"We scraped these emails from {company.domain}. "
                            f"Hopefully they help you identify the correct email format."
                        )
                        st.table(pd.DataFrame(emails, columns=["email"]))
                    st.write(
                        f"Sometimes you can see more employee emails in a search engine's results snippet, try it out!"
                    )
                    display_company_email_search_button(company.domain)

                    st.subheader("Recruiters")

                    for recruiter in recruiters:
                        subject, body = generate_email_subject_and_body(
                            company, recruiter, job_url
                        )
                        emails = recruiter.generate_email_permutations(company.domain)

                        with st.container():
                            st.markdown(
                                f"<div style='border: 1px solid #ddd; padding: 10px; border-radius: 8px; margin-bottom: 15px;'>"
                                f"<strong>{recruiter.full_name}</strong> | {recruiter.locale} | "
                                f"<a href='{recruiter.profile_url}' target='_blank'>Profile</a> | "
                                f"<a href='mailto:{','.join(emails)}?subject={subject}&body={body}'>Send Email</a>"
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
