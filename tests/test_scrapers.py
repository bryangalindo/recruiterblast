from unittest import TestCase, mock

from constants import (
    MOCK_COMPANY_API_RESPONSE,
    MOCK_COMPANY_ENTITY_API_RESPONSE,
    MOCK_BING_SEARCH_API_RESPONSE,
    MOCK_GOOGLE_SEARCH_API_RESPONSE,
)
from recruiterblast.models import Company
from recruiterblast.scrapers import (
    LinkedInScraper,
    BingSearchScraper,
    GoogleSearchScraper,
)


class LinkedInScraperTest(TestCase):
    @mock.patch.object(LinkedInScraper, "_fetch_company_from_job_post")
    @mock.patch.object(LinkedInScraper, "_fetch_company_entity_data")
    def test_fetch_company_from_job_post(self, mock_fetch_1, mock_fetch_2):
        scraper = LinkedInScraper("https://www.linkedin.com/jobs/view/4133961406")
        mock_fetch_1.return_value = MOCK_COMPANY_ENTITY_API_RESPONSE
        mock_fetch_2.return_value = MOCK_COMPANY_API_RESPONSE
        expected = Company(
            id=69318116,
            name="Sphinx Defense",
            industry="Defense & Space",
            description="Sphinx builds software",
            employee_count=19,
            domain="sphinxdefense.com",
        )

        actual = scraper.fetch_company_from_job_post()

        self.assertEqual(expected, actual)


class BingSearchScraperTest(TestCase):
    @mock.patch.object(BingSearchScraper, "_search_bing")
    def test_bing_scraper_returns_valid_emails(self, mock_search):
        mock_search.return_value = MOCK_BING_SEARCH_API_RESPONSE
        scraper = BingSearchScraper()

        emails = scraper.scrape_emails_from_company_domain("bar.com")

        self.assertEqual("foo@bar.com", emails[0])

    @mock.patch.object(BingSearchScraper, "_search_bing")
    def test_bing_scraper_returns_empty_list_if_response_empty(self, mock_search):
        mock_search.return_value = {}
        scraper = BingSearchScraper()

        emails = scraper.scrape_emails_from_company_domain("bar.com")

        self.assertEqual([], emails)


class GoogleSearchScraperTest(TestCase):
    @mock.patch.object(GoogleSearchScraper, "_search_google")
    def test_google_scraper_returns_valid_emails(self, mock_search):
        mock_search.return_value = MOCK_GOOGLE_SEARCH_API_RESPONSE
        scraper = GoogleSearchScraper()

        emails = scraper.scrape_emails_from_company_domain("bar.com")

        self.assertEqual("foo@bar.com", emails[0])

    @mock.patch.object(GoogleSearchScraper, "_search_google")
    def test_google_scraper_returns_empty_list_if_response_empty(self, mock_search):
        mock_search.return_value = {}
        scraper = GoogleSearchScraper()

        emails = scraper.scrape_emails_from_company_domain("bar.com")

        self.assertEqual([], emails)
