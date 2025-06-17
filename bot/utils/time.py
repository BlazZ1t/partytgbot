import re

def is_valid_datetime_string(s: str) -> bool:
    pattern = r"^(0[1-9]|[12][0-9]|3[01])-" \
              r"(0[1-9]|1[0-2])-" \
              r"(\d{4})-" \
              r"(0[0-9]|1[0-9]|2[0-3])-" \
              r"([0-5][0-9])$"
    return bool(re.match(pattern, s))