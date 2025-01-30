from unittest import TestCase, mock

from constants import MOCK_GOOGLE_GEMINI_API_RESPONSE

from recruiterblast.api import GoogleGeminiAPIClient


class TestGoogleGeminiAPIClient(TestCase):
    @mock.patch.object(GoogleGeminiAPIClient, "_make_request")
    def test_parse_skills_from_job_description(self, mock_request):
        mock_request.return_value = MOCK_GOOGLE_GEMINI_API_RESPONSE
        client = GoogleGeminiAPIClient()
        expected = {
            "core_responsibilities": ["foo"],
            "technical_requirements": ["bar"],
            "soft_skills": ["baz"],
            "highlights": ["qux"],
        }
        actual = client.parse_relevant_job_description_info("foobar")
        self.assertEqual(expected, actual)
