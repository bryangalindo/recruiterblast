import requests

import recruiterblast.config as cfg
from recruiterblast.constants import GOOGLE_GEMINI_API_URL
from recruiterblast.logger import setup_logger
from recruiterblast.parsers import (
    GoogleGeminiAPIResponseParser,
    safe_parse_dict_from_json_str,
)
from recruiterblast.prompts import LLM_JOB_DESCRIPTION_SUMMARY_PROMPT
from recruiterblast.utils import retry

log = setup_logger(__name__)


class GoogleGeminiAPIClient:
    BASE_URL = GOOGLE_GEMINI_API_URL.format(llm_model=cfg.GOOGLE_GEMINI_LLM_MODEL)

    def __init__(self):
        self.api_key = cfg.GOOGLE_GEMINI_API_KEY
        self.headers = {"Content-Type": "application/json"}

    def parse_relevant_job_description_info(self, job_description: str) -> dict:
        prompt = LLM_JOB_DESCRIPTION_SUMMARY_PROMPT
        prompt += f"Job description: {job_description}"

        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        log.debug(f"Starting to submit {prompt=}...")
        response = self._make_request(payload)

        parser = GoogleGeminiAPIResponseParser(response)
        text = parser.get_response_text()

        return safe_parse_dict_from_json_str(text)

    @retry(log)
    def _make_request(self, payload: dict) -> dict:
        url = f"{self.BASE_URL}?key={self.api_key}"
        response = requests.post(url, headers=self.headers, json=payload)
        data = response.json()
        log.info(f"Successfully received response from {url=}, {data=}")
        return data


if __name__ == "__main__":
    # pass
    description = """
    About the job
    Strong interest in development platforms, Data Engineering, MLOps, AI, CI/CD, infrastructure or making products for technical teams
    Able to make effective trade-offs in regards to both engineering and product requirements, while balancing short term and long term needs
    5+ years relevant industry experience in a fast-paced, high growth tech environment building UI component libraries, design systems, and tools using TypeScript
    Demonstrated design and UX sensibilities
    Knowledge of API standards including REST or GraphQL
    """
    client = GoogleGeminiAPIClient()
    info = client.parse_relevant_job_description_info(description)
    print(info)
