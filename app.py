import traceback

import pandas as pd
import streamlit as st

from recruiterblast.models import Company, Employee
from recruiterblast.scrapers import LinkedInScraper
from recruiterblast.utils import generate_email_permutations


def get_company_and_recruiter_data(job_url: str) -> tuple[Company, list[Employee]]:
    scraper = LinkedInScraper(job_url)
    company = scraper.fetch_company_from_job_post()
    recruiters = scraper.fetch_recruiters_from_company(company)
    return company, recruiters


def main():
    st.title("Recruiter Blast 🚀")
    st.write("Automate your recruiter outreach by submitting a job post url below.")

    # Input for the job URL
    job_url = st.text_input(
        "Job URL", placeholder="https://www.linkedin.com/jobs/view/4133654166"
    )

    if st.button("Submit"):
        if job_url:
            try:
                company, recruiters = get_company_and_recruiter_data(job_url)

                st.subheader("Company Information")
                company_data = {
                    "Field": [
                        "Name",
                        "Industry",
                        "Domain",
                        "Description",
                        "Employee Count",
                    ],
                    "Details": [
                        company.name,
                        company.industry,
                        company.domain,
                        company.description,
                        company.employee_count,
                    ],
                }
                company_df = pd.DataFrame(company_data)
                st.table(company_df)

                st.subheader("Recruiters")
                for recruiter in recruiters:
                    emails = generate_email_permutations(
                        recruiter.first_name, recruiter.last_name, company.domain
                    )
                    st.markdown(
                        f"**{recruiter.full_name}** - *{recruiter.headline}* "
                        f"[Profile Link]({recruiter.profile_url}) | "
                        f"[Send Email](mailto:{','.join(emails)})"
                    )

            except Exception as e:
                st.error(
                    f"Failed to fetch company and recruiter data, {traceback.format_exc()}"
                )
        else:
            st.error("Job URL is required!")


if __name__ == "__main__":
    main()
