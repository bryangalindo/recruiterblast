import traceback
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st

import recruiterblast.config as cfg
from recruiterblast.logger import setup_logger
from recruiterblast.parsers import LinkedInURLParser
from recruiterblast.scrapers import (
    BingSearchScraper,
    GoogleSearchScraper,
    LinkedInScraper,
)

log = setup_logger(__name__)


def main():
    st.title("Recruiter Blast 🚀")
    st.subheader("Mass send your pitch to recruiters from job posts!")

    job_url = st.text_input(
        "Job URL", placeholder="https://www.linkedin.com/jobs/view/4133654166"
    )
    email_subject = st.text_input(
        "Email subject", placeholder="I am a fit for this role."
    )
    email_body = st.text_input("Email body", placeholder="This is why.")

    st.markdown(
        "<p style='color: gray;'>No worries, we don’t store your data. "
        "All information is only used during your session and isn’t saved anywhere.</p>",
        unsafe_allow_html=True,
    )

    if st.button("Generate Email Links", type="primary"):

        if job_url:
            job_url = LinkedInURLParser.parse_linkedin_job_url(job_url)
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

                    if emails:
                        st.subheader("Company Emails")
                        st.write(
                            f"We scraped these emails from {company.domain}. "
                            f"Hopefully they help you identify the correct email format."
                        )
                        st.table(pd.DataFrame(emails, columns=["email"]))

                    st.subheader("Recruiters")

                    for recruiter in recruiters:
                        emails = recruiter.generate_email_permutations(company.domain)
                        subject_encoded = quote_plus(email_subject)
                        body_encoded = quote_plus(email_body)

                        with st.container():
                            st.markdown(
                                f"<div style='border: 1px solid #ddd; padding: 10px; border-radius: 8px; margin-bottom: 15px;'>"
                                f"<strong>{recruiter.full_name}</strong> | {recruiter.locale} | "
                                f"<a href='{recruiter.profile_url}' target='_blank'>Profile</a> | "
                                f"<a href='mailto:{','.join(emails)}?subject={subject_encoded}&body={body_encoded}'>Send Email</a>"
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
