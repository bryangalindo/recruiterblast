from unittest import TestCase, mock

from constants import (
    MOCK_COMPANY_API_RESPONSE,
    MOCK_COMPANY_ENTITY_API_RESPONSE,
    MOCK_GOOGLE_SEARCH_API_LEADIQ_EMAIL_FORMAT_RESPONSE,
    MOCK_GOOGLE_SEARCH_API_RESPONSE,
    MOCK_GOOGLE_SEARCH_API_ROCKETREACH_EMAIL_FORMAT_RESPONSE,
)

from recruiterblast.models import Company
from recruiterblast.scrapers import GoogleSearchScraper, LinkedInScraper


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

    @mock.patch.object(GoogleSearchScraper, "_search_google")
    def test_scraped_leadiq_suggested_email_format(self, mock_search):
        mock_search.return_value = MOCK_GOOGLE_SEARCH_API_LEADIQ_EMAIL_FORMAT_RESPONSE
        scraper = GoogleSearchScraper()

        suggested_email_format = scraper.scrape_leadiq_suggested_email_format(
            "foobar.com"
        )

        self.assertEqual(
            (
                "The FooBar's email format typically follows "
                "the pattern of First_Last@foobar.com; "
                "this email format is used 95% of the time. Other contacts within ..."
            ),
            suggested_email_format,
        )

    @mock.patch.object(GoogleSearchScraper, "_search_google")
    def test_scraped_rocketreach_suggested_email_format(self, mock_search):
        mock_search.return_value = (
            MOCK_GOOGLE_SEARCH_API_ROCKETREACH_EMAIL_FORMAT_RESPONSE
        )
        scraper = GoogleSearchScraper()

        suggested_email_format = scraper.scrape_rocketreach_suggested_email_format(
            "foobar.com"
        )

        self.assertEqual(
            (
                "The most common ASRC Federal email format is [first].[last] (ex. jane.doe@foobar.com), "
                "which is being used by 89.8% of ASRC Federal work email addresses"
            ),
            suggested_email_format,
        )
