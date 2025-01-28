import re
from urllib.parse import urlparse

from nameparser import HumanName


class LinkedInURLParser:
    @staticmethod
    def parse_linkedin_job_url(input_str):
        pattern = r"https://www\.linkedin\.com/jobs/view/\d+"
        matches = re.findall(pattern, input_str)
        return matches[0] if matches else ""


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
        parsed_url = urlparse(url)
        return parsed_url.netloc.replace("www.", "")
