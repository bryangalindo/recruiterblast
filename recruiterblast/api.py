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
            "Parse this job description for technology keywords. "
            "Return only a JSON dictionary string in the exact format shown below. "
            "No explanations, no extra text, no formatting (e.g., 'json\n...\n\n',), "
            ", no new line characters (e.g., '\n'), and no context beyond the JSON output. "
            "This is an example of what the output should be: "
            '"{"technologies": ["SQL", "Python", "Typescript", "Snowflake", "API", "dbt", "AWS", "GCP", "Snowflake",'
            '"QuickBase", "Google Analytics", "API", "data orchestration"]}"'
            f"Job description: {job_description}"
        )
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        log.debug(f"Starting to submit {prompt=}...")
        response = self._make_request(payload)
        parser = GoogleGeminiAPIResponseParser(response)
        text = parser.get_response_text()
        return safe_parse_dict_from_json_str(text)

    def _make_request(self, payload: dict) -> dict:
        url = f"{self.BASE_URL}?key={self.api_key}"
        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code == 200:
            log.info(f"Successfully received response from {url=}")
            return response.json()
        else:
            log.warning(
                f"Failed to get response from {url=}, {response.status_code}, "
                f"{response.reason}, {payload=}"
            )
            return {}


if __name__ == "__main__":
    pass
    # description = ""
    # client = GoogleGeminiAPIClient()
    # skills = client.parse_skills_from_job_description(description)
    # print(skills)
