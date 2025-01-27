from dataclasses import dataclass


@dataclass
class Company:
    id: int = None
    name: str = None
    industry: str = None
    description: str = None
    employee_count: int = None
    domain: str = None


@dataclass
class Employee:
    id: int = None
    first_name: str = None
    last_name: str = None
    full_name: str = None
    headline: str = None
    profile_url: str = None
