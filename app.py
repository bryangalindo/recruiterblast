import traceback

import streamlit as st

import recruiterblast.config as cfg
from recruiterblast.logger import setup_logger
from recruiterblast.scrapers import LinkedInScraper

log = setup_logger(__name__)


def main():
    st.title("Recruiter Blast 🚀")
    st.subheader("Automate your recruiter outreach by entering a job post url below.")

    job_url = st.text_input(
        "Job URL", placeholder="https://www.linkedin.com/jobs/view/4133654166"
    )

    if st.button("Submit"):
        if job_url:
            try:
                scraper = LinkedInScraper(job_url)

                company, recruiters = (
                    scraper.generate_mock_company_recruiter_data()
                    if cfg.ENV != 'prod'
                    else scraper.fetch_company_and_recruiter_data()
                )

                st.subheader("Company Information")
                st.table(company.as_df())

                st.subheader("Recruiters")
                for recruiter in recruiters:
                    emails = recruiter.generate_email_permutations(company.domain)
                    st.markdown(
                        f"**{recruiter.full_name}** - *{recruiter.headline}* "
                        f"[Profile Link]({recruiter.profile_url}) | "
                        f"[Send Email](mailto:{','.join(emails)})"
                    )

            except Exception as e:
                message = "Failed to fetch company and recruiter data"
                st.error(message)
                log.error(f"{message}, {e}, {traceback.format_exc()}")
        else:
            st.error("Job URL is required!")


if __name__ == "__main__":
    main()
