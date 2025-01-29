import requests

import recruiterblast.config as cfg
from recruiterblast.constants import GOOGLE_GEMINI_API_URL
from recruiterblast.logger import setup_logger
from recruiterblast.parsers import (
    GoogleGeminiAPIResponseParser,
    safe_parse_dict_from_json_str,
)

log = setup_logger(__name__)


class GoogleGeminiAPIClient:
    BASE_URL = GOOGLE_GEMINI_API_URL.format(llm_model=cfg.GOOGLE_GEMINI_LLM_MODEL)

    def __init__(self):
        self.api_key = cfg.GOOGLE_GEMINI_API_KEY
        self.headers = {"Content-Type": "application/json"}

    def parse_skills_from_job_description(self, job_description: str) -> dict:
        prompt = (
            "Parse this job description for technology keywords and soft skill keywords. "
            "Return only a JSON dictionary in the exact format shown below. No explanations, no extra text, and no context beyond the JSON output.\n\n"
            '{\n  "Technologies": [\n    "SQL", "Python", "Typescript", "dbt", "AWS", "GCP", "Snowflake",\n'
            '    "QuickBase", "Google Analytics", "API", "data orchestration"\n  ]\n}\n\n'
            f"Job description:\n{job_description}"
        )
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = self._make_request(payload)
        parser = GoogleGeminiAPIResponseParser(response)
        text = parser.get_response_text()
        return safe_parse_dict_from_json_str(text)

    def _make_request(self, payload: dict) -> dict:
        """
        Send a POST request to the Gemini API with the given payload.
        """
        url = f"{self.BASE_URL}?key={self.api_key}"
        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            log.info(f"Failed to get response from ")
            return {}
