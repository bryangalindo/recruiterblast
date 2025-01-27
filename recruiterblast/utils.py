import datetime
import random
import functools
import time


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

def sleep_for_random_n_seconds(log, min_seconds: int = 15, max_seconds: int = 30) -> None:
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
                            f"Max retries reached. Function failed with error: {e}"
                        )
                        raise

                    jitter = random.uniform(0, delay)
                    total_delay = min(delay + jitter, max_delay)

                    log.info(
                        f"Retrying in {total_delay:.2f} seconds... (Attempt {retries}/{max_retries}) due to error: {e}"
                    )
                    time.sleep(total_delay)

                    delay = min(delay * 2, max_delay)

        return wrapper

    return decorator_retry
