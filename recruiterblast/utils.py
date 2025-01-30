import datetime
import functools
import random
import time
import traceback

from recruiterblast.constants import USER_AGENTS


def iso_to_utc_timestamp(iso_timestamp_ms: int) -> str:
    utc_timestamp = datetime.datetime.fromtimestamp(
        iso_timestamp_ms / 1000, tz=datetime.timezone.utc
    )
    return utc_timestamp.isoformat()


def generate_rocketreach_formatted_username(employee, format: str) -> str:
    first_initial = employee.first_name[0] if employee.first_name else ""
    last_inital = employee.last_name[0] if employee.last_name else ""

    username = format.replace("[first]", employee.first_name)
    username = username.replace("[last]", employee.last_name)
    username = username.replace("[first_initial]", first_initial)
    username = username.replace("[last_initial]", last_inital)

    return username


def generate_formatted_employee_email(employee, format: str) -> str:
    email_parts = format.split("@")

    domain = email_parts[1].lower()
    username = email_parts[0].lower()

    username = username.replace("first", "%")
    username = username.replace("last", "#")
    username = username.replace("f", "^")
    username = username.replace("l", ">")

    username = username.replace("%", employee.first_name)
    username = username.replace("#", employee.last_name)
    username = username.replace(
        "^", employee.first_name[0] if employee.first_name else ""
    )
    username = username.replace(
        ">", employee.last_name[0] if employee.last_name else ""
    )

    return f"{username}@{domain}"


def generate_email_permutations(
    first_name: str, last_name: str, domain: str
) -> set[str]:
    separators = ["", ".", "_"]
    emails = set()

    emails.add(f"{first_name}@{domain}")
    emails.add(f"{last_name}@{domain}")

    first_initial = first_name[0] if first_name else ""
    last_initial = last_name[0] if last_name else ""

    for sep in separators:
        emails.add(f"{first_name}{sep}{last_name}@{domain}")
        emails.add(f"{last_name}{sep}{first_name}@{domain}")
        emails.add(f"{first_initial}{sep}{last_name}@{domain}")
        emails.add(f"{first_name}{sep}{last_initial}@{domain}")
        emails.add(f"{first_initial}{sep}{last_initial}@{domain}")
        emails.add(f"{last_name}{sep}{first_initial}@{domain}")
        emails.add(f"{last_initial}{sep}{first_name}@{domain}")
        emails.add(f"{last_initial}{sep}{first_initial}@{domain}")

    return emails


def get_current_iso_timestamp():
    return datetime.datetime.now(datetime.UTC)


def sleep_for_random_n_seconds(
    log, min_seconds: int = 15, max_seconds: int = 30
) -> None:
    sleep_time = random.uniform(min_seconds, max_seconds)
    log.info(f"Sleeping for {sleep_time=} seconds...")
    time.sleep(sleep_time)


def retry(log, max_retries=3, initial_delay=1, max_delay=32):
    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            delay = initial_delay

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        log.info(
                            f"Max retries reached. Function failed with error: {e}, "
                            f"{traceback.format_exc()}"
                        )
                        raise

                    jitter = random.uniform(0, delay)
                    total_delay = min(delay + jitter, max_delay)

                    log.info(
                        f"Retrying in {total_delay:.2f} seconds... "
                        f"(Attempt {retries}/{max_retries}) due to error: {e}, "
                        f"{traceback.format_exc()}"
                    )
                    time.sleep(total_delay)

                    delay = min(delay * 2, max_delay)

        return wrapper

    return decorator_retry


class Timer:
    def __init__(self, log, message="Elapsed time", unit="seconds"):
        self.log = log
        self.unit = unit.lower()
        self.message = message
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        elapsed_time = time.time() - self.start_time

        if self.unit == "milliseconds":
            elapsed_time *= 1000
            unit_str = "ms"
        else:
            unit_str = "seconds"

        self.log.info(f"{self.message} time_elapsed_{unit_str}={elapsed_time:.2f}")


def get_random_user_agent() -> str:
    return random.choice(USER_AGENTS)
