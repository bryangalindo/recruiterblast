import re
from abc import ABC, abstractmethod

import requests

import recruiterblast.config as cfg
from recruiterblast.constants import (
    GOOGLE_SEARCH_API_URL,
    LINKEDIN_API_HEADERS,
    LINKEDIN_COMPANY_API_URL,
    LINKEDIN_COMPANY_ENTITY_API_URL,
    LINKEDIN_EMPLOYEE_API_URL,
    LINKEDIN_JOB_POST_API_URL,
)
from recruiterblast.logger import setup_logger
from recruiterblast.models import Company, Employee, JobPost
from recruiterblast.parsers import (
    LinkedinCompanyAPIResponseParser,
    LinkedinEmployeeAPIResponseParser,
    LinkedInJobPostAPIResponseParser,
    parse_emails_from_text,
)
from recruiterblast.utils import (
    Timer,
    get_random_user_agent,
    retry,
    sleep_for_random_n_seconds,
)

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
        self.job_id = self._parse_job_id_from_job_post_url(job_post_url)

    def fetch_job_post_details(self) -> JobPost:
        log.info(f"Starting to fetch job post details...")
        job_post = JobPost()

        response = self._fetch_job_post_details()
        parser = LinkedInJobPostAPIResponseParser(response)

        job_post.id = self.job_id
        job_post.title = parser.get_title()
        job_post.description = parser.get_description()
        job_post.post_date = parser.get_post_date()
        job_post.location = parser.get_location()
        job_post.is_remote = parser.get_is_remote()
        job_post.apply_url = parser.get_apply_url()

        log.info(f"Successfully fetched {job_post=}")

        return job_post

    def fetch_company_from_job_post(self) -> Company:
        log.info(f"Starting to fetch company details from {self.job_post_url=}...")

        company = Company()
        parser = LinkedinCompanyAPIResponseParser()

        data = self._fetch_company_from_job_post(self.job_id)

        company.name = parser.get_company_name(data)
        company.id = parser.get_company_id(data)
        company.industry = parser.get_industry(data)
        company.description = parser.get_company_description(data)
        company.employee_count = parser.get_employee_count(data)

        company_data = self._fetch_company_entity_data(company)
        company.domain = parser.get_domain(company_data)

        log.info(f"Successfully added {company}")

        return company

    def fetch_recruiters_from_company(self, company: Company) -> list[Employee]:
        log.info(f"Starting to fetch recruiters from {company=}...")

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
                employee.locale = parser.get_employee_locale(result)

                employee.full_name = parser.get_employee_name(result)
                employee.first_name = parser.get_employee_first_name(employee.full_name)
                employee.last_name = parser.get_employee_last_name(employee.full_name)

                employees[employee.id] = employee

                log.info(f"Successfully added i={len(employees)}, {employee}")

        return list(employees.values())

    def fetch_company_and_recruiter_data(self) -> tuple[Company, list[Employee]]:
        company = self.fetch_company_from_job_post()
        recruiters = self.fetch_recruiters_from_company(company)
        return company, recruiters

    @retry(log)
    def _fetch_job_post_details(self) -> dict:
        self._update_user_agent_header()
        url = LINKEDIN_JOB_POST_API_URL.format(job_id=self.job_id)
        with Timer(
            log,
            message=f"Time taken to fetch job post from {url=}",
            unit="milliseconds",
        ):
            response = requests.get(url, headers=LINKEDIN_API_HEADERS)
        sleep_for_random_n_seconds(log, min_seconds=1, max_seconds=5)
        return response.json()

    @retry(log)
    def _fetch_company_from_job_post(self, job_id: int) -> dict:
        self._update_user_agent_header()
        url = LINKEDIN_COMPANY_API_URL.format(job_id=job_id)
        with Timer(
            log,
            message=f"Time taken to fetch company data from {url=}",
            unit="milliseconds",
        ):
            response = requests.get(url, headers=LINKEDIN_API_HEADERS)
        sleep_for_random_n_seconds(log, min_seconds=1, max_seconds=5)
        return response.json()

    @retry(log)
    def _fetch_company_entity_data(self, company: Company) -> dict:
        self._update_user_agent_header()
        url = LINKEDIN_COMPANY_ENTITY_API_URL.format(company_id=company.id)
        with Timer(
            log,
            message=f"Time taken to fetch company domain from {url=}",
            unit="milliseconds",
        ):
            response = requests.get(url, headers=LINKEDIN_API_HEADERS)
        sleep_for_random_n_seconds(log, min_seconds=1, max_seconds=5)
        return response.json()

    @retry(log)
    def _fetch_recruiters_from_company(self, company: Company, keyword: str) -> str:
        self._update_user_agent_header()
        url = LINKEDIN_EMPLOYEE_API_URL.format(company_id=company.id, keyword=keyword)
        with Timer(
            log,
            message=f"Time taken to fetch recruiters from {url=}",
            unit="milliseconds",
        ):
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

    def _update_auth_headers(self) -> None:
        self.headers["cookie"] = cfg.LINKEDIN_COOKIE
        self.headers["csrf-token"] = cfg.LINKEDIN_CSRF_TOKEN

    def _update_user_agent_header(self) -> None:
        self.headers["user-agent"] = get_random_user_agent()

    @staticmethod
    def generate_mock_company():
        return Company(
            name="Company ABC",
            industry="Technology",
            description="A leading technology company specializing in AI.",
            employee_count=500,
            domain="companyabc.com",
        )

    @staticmethod
    def generate_mock_recruiters():
        return [
            Employee(
                first_name="Jane",
                last_name="Doe",
                full_name="Jane Doe",
                headline="HR Manager",
                profile_url="https://linkedin.com/in/jane",
                locale="Los Angeles",
            ),
            Employee(
                first_name="John",
                last_name="Smith",
                full_name="John Smith",
                headline="Senior Recruiter",
                profile_url="https://linkedin.com/in/john",
                locale="New York",
            ),
        ]

    def generate_mock_company_recruiter_data(self):
        return (self.generate_mock_company(), self.generate_mock_recruiters())


class GoogleSearchScraper:
    def scrape_emails_from_company_domain(self, domain: str) -> list[str]:
        scraped_emails = set()
        results = self._search_google(
            f'site:{domain} "@{domain}"',
        )
        search_results = results.get("items", [])
        log.info(f"Starting to parse {len(search_results)} search results...")
        for i, item in enumerate(search_results):
            snippet = str(item["snippet"])
            log.debug(f"Parsing emails from {i=} {snippet=}...")
            emails = parse_emails_from_text(snippet)
            for email in emails:
                scraped_emails.add(email)
                log.info(f"Successfully scraped {i=}, {email=}...")
        return list(scraped_emails)

    def scrape_suggested_email_format(self, domain: str) -> str:
        results = self._search_google(
            f'site:leadiq.com "@{domain}"',
        )
        search_results = results.get("items", [])
        log.info(f"Starting to parse {len(search_results)} search results...")
        for i, item in enumerate(search_results):
            snippet = str(item.get("snippet", ""))
            log.debug(f"Parsing formats from {i=} {snippet=}...")
            if "email format typically follows" in snippet.lower():
                return snippet.split("Other contacts")[0].strip()

    @retry(log)
    def _search_google(self, query: str) -> dict:
        with Timer(
            log,
            message=f"Time taken to process Google {query=}",
            unit="milliseconds",
        ):
            params = {
                "key": cfg.GOOGLE_SEARCH_API_KEY,
                "cx": cfg.GOOGLE_SEARCH_CUSTOM_SEARCH_ENGINE_ID,
                "q": query,
            }
            response = requests.get(GOOGLE_SEARCH_API_URL, params=params)
            data = response.json()
            log.debug(
                f"Successfully received response {response.status_code} from {response.url} with {data=}"
            )
            return data or {}


if __name__ == "__main__":
    pass
    # job_url = "https://www.linkedin.com/jobs/view/4133654166"
    # scraper = LinkedInScraper(job_url)
    # scraper.fetch_job_post_details()
    # company = scraper.fetch_company_from_job_post()
    # google_scraper = GoogleSearchScraper()
    # google_emails = (
    #     google_scraper.scrape_emails_from_company_domain(
    #         company.domain
    #     )
    # )
    # print(google_emails)
