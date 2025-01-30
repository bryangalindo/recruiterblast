import json
import re

import tldextract
from nameparser import HumanName

from recruiterblast.logger import setup_logger
from recruiterblast.utils import iso_to_utc_timestamp

log = setup_logger(__name__)


def parse_emails_from_text(text: str) -> list[str]:
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9._%-]+\.[a-zA-Z]{2,}"
    return re.findall(email_pattern, text)


def parse_linkedin_job_url(input_str: str) -> str:
    pattern = r"https://www\.linkedin\.com/jobs/view/\d+"
    matches = re.findall(pattern, input_str)
    return matches[0] if matches else ""


def safe_parse_dict_from_json_str(json_str: str) -> dict:
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        return {}


class GoogleGeminiAPIResponseParser:
    def __init__(self, response: dict):
        self.response = response

    def get_response_text(self):
        log.debug(f"Parsing {self.response=}...")
        candidates = self.response.get("candidates", [])
        if not candidates:
            return ""
        content_parts = candidates[0].get("content", {}).get("parts", [])
        if not content_parts:
            return ""
        return content_parts[0].get("text", "")


class LinkedInJobPostAPIResponseParser:
    def __init__(self, response: dict):
        self.response = response

    def get_location(self) -> str:
        return self.response.get("data", {}).get("formattedLocation", "")

    def get_post_date(self) -> str:
        timestamp = self.response.get("data", {}).get("originalListedAt", 0)
        return iso_to_utc_timestamp(timestamp)

    def get_is_remote(self) -> bool:
        return self.response.get("data", {}).get("workRemoteAllowed", False)

    def get_apply_url(self) -> str:
        apply_method = self.response.get("data", {}).get("applyMethod", {})
        url = apply_method.get("easyApplyUrl") or apply_method.get("companyApplyUrl")
        return url or ""

    def get_title(self) -> str:
        return self.response.get("data", {}).get("title", "")

    def get_description(self) -> str:
        return self.response.get("data", {}).get("description", {}).get("text", "")


class LinkedinEmployeeAPIResponseParser:
    @staticmethod
    def get_employee_id(data: dict) -> int:
        urn = data["trackingUrn"]
        return int(urn.split(":")[-1])

    @staticmethod
    def get_employee_headline(data: dict) -> int:
        return data["primarySubtitle"]["text"]

    @staticmethod
    def get_employee_name(data: dict) -> str:
        name = str(data["title"]["text"])
        return name.split(",")[0]

    @staticmethod
    def get_employee_profile_url(data: dict) -> str:
        return data["navigationUrl"].split("?")[0]

    @staticmethod
    def get_employee_first_name(full_name: str) -> str:
        parsed_name = HumanName(full_name)
        return parsed_name.first.replace(" ", "").replace(".", "")

    @staticmethod
    def get_employee_last_name(full_name: str) -> str:
        parsed_name = HumanName(full_name)
        return parsed_name.last.replace(" ", "").replace(".", "")

    @staticmethod
    def get_employee_locale(data: dict) -> str:
        return data["secondarySubtitle"]["text"]


class LinkedinCompanyAPIResponseParser:
    @staticmethod
    def get_company_id(data: dict) -> int:
        for result in data["included"]:
            if "entityUrn" in result:
                entity_urn = result["entityUrn"]
                if "company" in entity_urn or "fsd_company" in entity_urn:
                    return int(entity_urn.split(":")[-1])

    @staticmethod
    def get_industry(data: dict) -> int:
        for result in data["included"]:
            if "entityUrn" in result:
                entity_urn = result["entityUrn"]
                if "fsd_industry" in entity_urn:
                    return result["name"]

    @staticmethod
    def get_employee_count(data: dict) -> int:
        for result in data["included"]:
            if "employeeCount" in result:
                return result["employeeCount"]

    @staticmethod
    def get_company_description(data: dict) -> str:
        for result in data["included"]:
            if "employeeCount" in result:
                return result["description"]

    @staticmethod
    def get_company_name(data: dict) -> str:
        for result in data["included"]:
            if "employeeCount" in result:
                return result["name"]

    @staticmethod
    def get_domain(data: dict) -> str:
        url = data["data"]["websiteUrl"]
        extracted = tldextract.extract(url)
        return f"{extracted.domain}.{extracted.suffix}"
