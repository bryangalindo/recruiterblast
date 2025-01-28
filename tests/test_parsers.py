from unittest import TestCase

from parameterized import parameterized

from recruiterblast.parsers import parse_linkedin_job_url, parse_emails_from_text


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
