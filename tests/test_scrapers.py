from unittest import TestCase, mock

from recruiterblast.models import Company
from recruiterblast.scrapers import LinkedInScraper, BingScraper

MOCK_COMPANY_API_RESPONSE = {
    "data": {},
    "included": [
        {
            "entityUrn": "urn:li:fsd_followingState:urn:li:fsd_company:69318116",
        },
        {
            "name": "Defense & Space",
            "entityUrn": "urn:li:fsd_industryV2:3187",
        },
        {
            "description": "Sphinx builds software",
            "*industryV2Taxonomy": ["urn:li:fsd_industryV2:3187"],
            "employeeCount": 19,
            "name": "Sphinx Defense",
        },
    ],
}

MOCK_COMPANY_ENTITY_API_RESPONSE = {
    "data": {
        "websiteUrl": "https://www.sphinxdefense.com",
    },
    "included": [],
}

MOCK_BING_SEARCH_API_RESPONSE = {
    "webPages": {
        "value": [
            {
                "snippet": "Reach out at foo@bar.com",
            }
        ]
    }
}


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


class BingScraperTest(TestCase):
    @mock.patch.object(BingScraper, "_search_bing")
    def test_bing_scraper_returns_valid_emails(self, mock_search):
        mock_search.return_value = MOCK_BING_SEARCH_API_RESPONSE
        scraper = BingScraper()

        emails = scraper.scrape_company_emails_from_domain("bar.com")

        self.assertEqual("foo@bar.com", emails[0])

    @mock.patch.object(BingScraper, "_search_bing")
    def test_bing_scraper_returns_empty_list_if_response_empty(self, mock_search):
        mock_search.return_value = {}
        scraper = BingScraper()

        emails = scraper.scrape_company_emails_from_domain("bar.com")

        self.assertEqual([], emails)
