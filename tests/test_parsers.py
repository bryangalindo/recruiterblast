from unittest import TestCase

from parameterized import parameterized

from recruiterblast.parsers import LinkedInURLParser


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
        actual = LinkedInURLParser.parse_linkedin_job_url(input_str)
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
        actual = LinkedInURLParser.parse_linkedin_job_url(input_str)
        self.assertEqual("", actual)
