import datetime


def generate_email_permutations(
    first_name: str, last_name: str, domain: str
) -> set[str]:
    separators = ["", "."]
    emails = set()

    emails.add(f"{first_name}@{domain}")
    emails.add(f"{last_name}@{domain}")

    for sep in separators:
        emails.add(f"{first_name}{sep}{last_name}@{domain}")
        emails.add(f"{last_name}{sep}{first_name}@{domain}")
        emails.add(f"{first_name[0]}{sep}{last_name}@{domain}")
        emails.add(f"{first_name}{sep}{last_name[0]}@{domain}")
        emails.add(f"{first_name[0]}{sep}{last_name[0]}@{domain}")
        emails.add(f"{last_name}{sep}{first_name[0]}@{domain}")
        emails.add(f"{last_name[0]}{sep}{first_name}@{domain}")
        emails.add(f"{last_name[0]}{sep}{first_name[0]}@{domain}")

    return emails


def get_current_iso_timestamp():
    return datetime.datetime.now(datetime.UTC)
