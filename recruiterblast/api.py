import requests

import recruiterblast.config as cfg
from recruiterblast.constants import GOOGLE_GEMINI_API_URL
from recruiterblast.logger import setup_logger
from recruiterblast.parsers import (
    GoogleGeminiAPIResponseParser,
    safe_parse_dict_from_json_str,
)
from recruiterblast.prompts import LLM_JOB_DESCRIPTION_SKILLS_PARSER_PROMPT
from recruiterblast.utils import retry

log = setup_logger(__name__)


class GoogleGeminiAPIClient:
    BASE_URL = GOOGLE_GEMINI_API_URL.format(llm_model=cfg.GOOGLE_GEMINI_LLM_MODEL)

    def __init__(self):
        self.api_key = cfg.GOOGLE_GEMINI_API_KEY
        self.headers = {"Content-Type": "application/json"}

    def parse_skills_from_job_description(self, job_description: str) -> dict:
        prompt = LLM_JOB_DESCRIPTION_SKILLS_PARSER_PROMPT
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
    pass
    # description = """
    # 2+ years of professional experience in software development, with a strong emphasis on development of large-scale and performant applications.
    # Knowledge in at least one server-side language such as Java, C++, C#, Go, Python, Kotlin, or Ruby.
    # Ability towards building resilient and operationally efficient backend systems exemplifying industry standards (HTTP REST, GraphQL, Serverless, SOA, etc).
    # A desire to ship world class code daily.
    # Good attention to detail, as well as a passion for delivering high-quality software solutions and compelling customer experiences
    # Good problem-solving skills, possessing the ability to work independently or collaboratively to analyze and address complex technical challenges
    # Excellent communication skills with the ability to collaborate effectively with cross-functional teams and those in non-technical roles, such as marketing, finance, and legal
    # Knowledge of modern software development practices, version control systems, and agile methodologies
    # """
    # client = GoogleGeminiAPIClient()
    # skills = client.parse_skills_from_job_description(description)
    # print(skills)
