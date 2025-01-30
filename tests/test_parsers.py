from unittest import TestCase

from constants import MOCK_GOOGLE_GEMINI_API_RESPONSE
from parameterized import parameterized

from recruiterblast.parsers import (
    GoogleGeminiAPIResponseParser,
    LinkedinCompanyAPIResponseParser,
    LinkedInJobPostAPIResponseParser,
    parse_emails_from_text,
    parse_linkedin_job_url,
    parse_rocket_reach_email_format,
)
from recruiterblast.utils import iso_to_utc_timestamp


class ParserTest(TestCase):
    @parameterized.expand(
        [
            ("See job post: https://www.linkedin.com/jobs/view/4133654166/test",),
            ("https://www.linkedin.com/jobs/view/4133654166/",),
            ("https://www.linkedin.com/jobs/view/4133654166",),
            ("\nhttps://www.linkedin.com/jobs/view/4133654166\n",),
            ("https://www.linkedin.com/jobs/view/4133654166?refId=12345",),
            ("https://www.linkedin.com/jobs/view/4133654166?utm_source=google",),
            ("https://www.linkedin.com/jobs/view/4133654166#section",),
            ("Check this: https://www.linkedin.com/jobs/view/4133654166#details",),
            (
                "Apply now at https://www.linkedin.com/jobs/view/4133654166 before it's too late!",
            ),
            (
                "Multiple links https://www.linkedin.com/jobs/view/4133654166 and https://www.google.com.",
            ),
        ]
    )
    def test_parser_returns_match_for_valid_linkedn_urls(self, input_str: str):
        actual = parse_linkedin_job_url(input_str)
        self.assertEqual("https://www.linkedin.com/jobs/view/4133654166", actual)

    @parameterized.expand(
        [
            ("https://www.linkedin.com/jobs/view/",),
            ("https://linkedin.com/jobs/view/4133654166",),
            ("https://www.linkedin.com/jobs/4133654166",),
            ("http://www.linkedin.com/jobs/view/4133654166",),
            ("https://www.linkedin.com/view/4133654166",),
            ("Not a job link: https://www.linkedin.com/",),
            ("Random text with no URL",),
            ("",),
        ]
    )
    def test_parser_returns_empty_str_for_invalid_linkedin_urls(self, input_str: str):
        actual = parse_linkedin_job_url(input_str)
        self.assertEqual("", actual)

    @parameterized.expand(
        [
            (
                "first_initial_last",
                "Email format is [first_initial][last] (ex. jdoe@gitlab.com)",
                "[first_initial][last]",
            ),
            (
                "first_dot_last",
                "Email format is [first].[last] (ex. jdoe@gitlab.com)",
                "[first].[last]",
            ),
            (
                "first_underscore_last_initial",
                "Email format is [first]_[last_initial] (ex. jdoe@gitlab.com)",
                "[first]_[last_initial]",
            ),
            (
                "no_format_found",
                "This text does not contain any email format information.",
                None,
            ),
        ]
    )
    def test_extract_email_format(self, name, text, expected):
        actual = parse_rocket_reach_email_format(text)
        self.assertEqual(expected, actual)


class EmailParserTest(TestCase):

    @parameterized.expand(
        [
            # Valid email addresses
            ("simple email", "test@example.com", ["test@example.com"]),
            (
                "email with subdomain",
                "user.name@sub.domain.com",
                ["user.name@sub.domain.com"],
            ),
            (
                "email with special characters",
                "user+name@example.co.uk",
                ["user+name@example.co.uk"],
            ),
            (
                "email with digits",
                "user1234@example1234.com",
                ["user1234@example1234.com"],
            ),
            (
                "email with underscores",
                "user_name@domain_name.com",
                ["user_name@domain_name.com"],
            ),
            (
                "email with hyphen",
                "user-name@domain-name.com",
                ["user-name@domain-name.com"],
            ),
            # Invalid email addresses
            ("email without @", "username.domain.com", []),
            ("email without domain", "username@.com", []),
            ("email with invalid character", "username@domain!com", []),
            ("email with double @", "username@@domain.com", []),
            ("email with missing TLD", "username@domain", []),
            # Multiple emails
            (
                "multiple valid emails",
                "test@example.com and user+name@example.co.uk",
                ["test@example.com", "user+name@example.co.uk"],
            ),
            # Email with newline and extra spaces
            ("email with newline", "   test@example.com \n", ["test@example.com"]),
            # Emails embedded in sentences
            (
                "email in sentence",
                "Contact us at support@company.com for more info.",
                ["support@company.com"],
            ),
            # Edge case: email with top-level domain of length 2
            ("email with 2 letter TLD", "email@example.ae", ["email@example.ae"]),
        ]
    )
    def test_parse_emails(self, name, text, expected_emails):
        result = parse_emails_from_text(text)
        self.assertEqual(
            expected_emails,
            result,
        )


class TestLinkedinCompanyAPIResponseParser(TestCase):
    def test_domain_parser_omits_subdomains(self):
        data = {"data": {"websiteUrl": "https://www.about.gitlab.com"}}
        expected = "gitlab.com"
        actual = LinkedinCompanyAPIResponseParser.get_domain(data)
        self.assertEqual(expected, actual)


class TestLinkedInJobPostAPIResponseParser(TestCase):

    def setUp(self):
        """Create mock responses for testing."""
        self.mock_response = {
            "data": {
                "formattedLocation": "New York, NY",
                "originalListedAt": 1737739491000,  # Sample timestamp
                "workRemoteAllowed": True,
                "applyMethod": {
                    "easyApplyUrl": "https://www.linkedin.com/jobs/easy-apply/123456",
                    "companyApplyUrl": "https://www.company.com/apply",
                },
                "title": "Software Engineer 2",
                "description": {
                    "text": "We are looking for a talented software engineer."
                },
            }
        }
        self.parser = LinkedInJobPostAPIResponseParser(self.mock_response)

    def test_get_location(self):
        location = self.parser.get_location()
        self.assertEqual("New York, NY", location)

    def test_get_post_date(self):
        expected_utc_date = iso_to_utc_timestamp(1737739491000)
        post_date = self.parser.get_post_date()
        self.assertEqual(expected_utc_date, post_date)

    def test_get_is_remote(self):
        self.assertTrue(self.parser.get_is_remote())

    def test_get_apply_url_easy_apply(self):
        apply_url = self.parser.get_apply_url()
        self.assertEqual("https://www.linkedin.com/jobs/easy-apply/123456", apply_url)

    def test_get_apply_url_company_apply(self):
        self.mock_response["data"]["applyMethod"] = {
            "companyApplyUrl": "https://www.company.com/apply"
        }
        apply_url = self.parser.get_apply_url()
        self.assertEqual("https://www.company.com/apply", apply_url)

    def test_get_title(self):
        title = self.parser.get_title()
        self.assertEqual("Software Engineer 2", title)

    def test_get_description(self):
        description = self.parser.get_description()
        self.assertEqual(
            "We are looking for a talented software engineer.", description
        )

    def test_get_apply_url_no_url(self):
        self.mock_response["data"]["applyMethod"] = {}
        self.assertEqual(self.parser.get_apply_url(), "")


class TestGoogleGeminiAPIResponseParser(TestCase):
    def test_get_response_text(self):
        expected = (
            '{"core_responsibilities": ["foo"],'
            '"technical_requirements": ["bar"],'
            '"soft_skills": ["baz"],'
            '"highlights": ["qux"]}'
        )
        parser = GoogleGeminiAPIResponseParser(MOCK_GOOGLE_GEMINI_API_RESPONSE)
        actual = parser.get_response_text()
        self.assertEqual(expected, actual)
