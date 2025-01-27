from unittest import TestCase, mock

from recruiterblast.models import Company
from recruiterblast.scrapers import LinkedInScraper

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
