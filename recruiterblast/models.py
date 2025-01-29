from dataclasses import asdict, dataclass

import pandas as pd

from recruiterblast.utils import generate_email_permutations


@dataclass
class Company:
    id: int = None
    name: str = None
    industry: str = None
    domain: str = None
    employee_count: int = None
    description: str = None

    def as_df(self):
        data = {
            "Field": list(asdict(self).keys()),
            "Details": list(asdict(self).values()),
        }
        return pd.DataFrame(data)


@dataclass
class Employee:
    id: int = None
    first_name: str = None
    last_name: str = None
    full_name: str = None
    headline: str = None
    locale: str = None
    profile_url: str = None

    def generate_email_permutations(self, domain: str) -> set[str]:
        return generate_email_permutations(self.first_name, self.last_name, domain)


@dataclass
class JobPost:
    id: int = None
    title: str = None
    description: str = None
    post_date: str = None
    apply_url: str = None
