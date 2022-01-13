import re
from typing import Dict, List, Pattern


def create_query_like_or_really_like(
    target_field: str
) -> Dict[str, List[Dict["str", Pattern[str]]]]:
    q_like_or_really_like: Dict[
        str, List[
            Dict["str", Pattern[str]]
        ]] = {
        "$or": [
            {target_field: re.compile("好き")},
            {target_field: re.compile("大好き")}
        ]
    }
    return q_like_or_really_like


def create_query_regex_pattern_location(
    location_name: str
) -> Dict[str, Dict[str, str]]:
    """
        * beginning of some location pattern
    """
    return {"location_name": {
        "$regex": "^{}(.)*".format(
            location_name
        )
    }}
