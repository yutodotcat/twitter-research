from datetime import datetime
from typing import Callable, List

from pytz import timezone


def convert_utc_str_to_jst_date(utc_str: str) -> datetime:
    utc_date = datetime.strptime(utc_str, "%a %b %d %H:%M:%S %z %Y")
    return utc_date.astimezone(timezone("Asia/Tokyo"))


def is_include_list_element_string_in_target_string(
    target_list: List[str],
    target_str: str
) -> bool:
    for list_element in target_list:
        if list_element in target_str:
            return True
    return False


is_include_like_or_really_like: Callable[[str, str], bool] = (
    lambda target1, target2: (
        ("好き" in target1 or "大好き" in target1) or (
            "好き" in target2 or "大好き" in target2
        )
    )
)
