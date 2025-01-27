import re
from abc import ABC, abstractmethod

import requests
from nameparser import HumanName

import recruiterblast.config as cfg
from recruiterblast.constants import (
    LINKEDIN_API_HEADERS,
    LINKEDIN_COMPANY_API_URL,
    LINKEDIN_COMPANY_ENTITY_API_URL,
    LINKEDIN_EMPLOYEE_API_URL,
)
from recruiterblast.logger import setup_logger
from recruiterblast.models import Company, Employee
from recruiterblast.parsers import (
    LinkedinCompanyAPIResponseParser,
    LinkedinEmployeeAPIResponseParser,
)
from recruiterblast.utils import retry, sleep_for_random_n_seconds

log = setup_logger(__name__)


class BaseScraper(ABC):
    @abstractmethod
    def fetch_company_from_job_post(self) -> Company: ...

    @abstractmethod
    def fetch_recruiters_from_company(self, company: Company) -> list[Employee]: ...


class LinkedInScraper(BaseScraper):
    def __init__(self, job_post_url: str):
        self.job_post_url = job_post_url
        self.headers = LINKEDIN_API_HEADERS
        self._update_auth_headers()

    def fetch_company_from_job_post(self) -> Company:
        company = Company()
        parser = LinkedinCompanyAPIResponseParser()

        job_id = self._parse_job_id_from_job_post_url(self.job_post_url)
        data = self._fetch_company_from_job_post(job_id)

        company.name = parser.get_company_name(data)
        company.id = parser.get_company_id(data)
        company.industry = parser.get_industry(data)
        company.description = parser.get_company_description(data)
        company.employee_count = parser.get_company_description(data)

        company_data = self._fetch_company_entity_data(company)
        company.domain = parser.get_domain(company_data)

        log.info(f"Successfully fetched {company}")

        return company

    def fetch_recruiters_from_company(self, company: Company) -> list[Employee]:
        employees = {}
        keywords = ["recruiter", "talent%20acquisition"]
        parser = LinkedinEmployeeAPIResponseParser()

        for keyword in keywords:
            data = self._fetch_recruiters_from_company(company, keyword)

            for result in data["included"]:
                if not self._is_valid_public_employee(result):
                    continue

                employee = Employee()
                employee.id = parser.get_employee_id(result)

                if employee.id in employees:
                    log.debug(f"Skipping duplicate {employee=}...")
                    continue

                employee.headline = parser.get_employee_headline(result)
                employee.profile_url = parser.get_employee_profile_url(result)

                employee.full_name = parser.get_employee_name(result)
                parsed_name = HumanName(employee.full_name)
                employee.first_name = parsed_name.first
                employee.last_name = parsed_name.last

                employees[employee.id] = employee

                log.info(f"Successfully fetched i={len(employees)}, {employee}")

        return list(employees.values())

    @retry(log)
    def _fetch_company_from_job_post(self, job_id: int) -> dict:
        url = LINKEDIN_COMPANY_API_URL.format(job_id=job_id)
        log.info(f"Starting to fetch data for {job_id=}, {url=}...")
        response = requests.get(url, headers=LINKEDIN_API_HEADERS)
        sleep_for_random_n_seconds(log, min_seconds=1, max_seconds=5)
        return response.json()

    @retry(log)
    def _fetch_company_entity_data(self, company: Company) -> dict:
        url = LINKEDIN_COMPANY_ENTITY_API_URL.format(company_id=company.id)
        log.info(f"Starting to fetch domain for {company.name=}, {url=}...")
        response = requests.get(url, headers=LINKEDIN_API_HEADERS)
        sleep_for_random_n_seconds(log, min_seconds=1, max_seconds=5)
        return response.json()

    @retry(log)
    def _fetch_recruiters_from_company(self, company: Company, keyword: str) -> str:
        url = LINKEDIN_EMPLOYEE_API_URL.format(company_id=company.id, keyword=keyword)
        log.info(
            f"Starting to fetch recruiters from {company.name}, {keyword=}, {url=}..."
        )
        response = requests.get(url, headers=LINKEDIN_API_HEADERS)
        sleep_for_random_n_seconds(log, min_seconds=1, max_seconds=5)
        return response.json()

    def _is_valid_public_employee(self, result: dict) -> bool:
        return (
            "bserpEntityNavigationalUrl" in result
            and "headless" not in result["trackingUrn"]
        )

    def _parse_job_id_from_job_post_url(self, url: str):
        match = re.search(r"view/(\d+)", url)
        return match.group(1)

    def _update_auth_headers(self):
        self.headers["cookie"] = cfg.LINKEDIN_COOKIE
        self.headers["csrf-token"] = cfg.LINKEDIN_CSRF_TOKEN


if __name__ == "__main__":
    # pass
    scraper = LinkedInScraper("https://www.linkedin.com/jobs/view/4133961406")
    company = scraper.fetch_company_from_job_post()
    recruiters = scraper.fetch_recruiters_from_company(company)
    print(recruiters)
