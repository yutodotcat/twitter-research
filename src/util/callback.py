import re
from datetime import datetime
from typing import Any, Callable, Dict, Pattern, Union

from pymongo import UpdateOne
from src.util.method import (convert_utc_str_to_jst_date,
                             is_include_like_or_really_like,
                             is_include_list_element_string_in_target_string)
from src.util.nlp import OPPOSITE_WORDS_FOR_LIKE

retrieve_tweet_text_as_default: Callable[[Dict[str, Any]], str] = (
    lambda document: document["tweet_data"]["text"]
)

retrieve_tweet_text_as_content: Callable[[Dict[str, Any]], str] = (
    lambda document: document["tweet_content"]
)

retrieve_tweet_description_as_default: Callable[[Dict[str, Any]], str] = (
    lambda document: document["tweet_data"]["user"]["description"]
)

update_one_as_default: Callable[
    [Dict[str, Any]], UpdateOne
] = (
    lambda document: UpdateOne(
        {"_id": document["_id"]},
        {"$set": document},
        upsert=True
    )
)

update_one_as_default_schema: Callable[
    [Dict[str, Any]], UpdateOne
] = (
    lambda document: UpdateOne(
        {"_id": document["_id"]},
        {"$set": {
            "_id": document["_id"],
            "tweet_data": document["tweet_data"],
            "location_name": document["location_name"]
        }},
        upsert=True
    )
)

update_one_as_distinct_tweet_by_user: Callable[
    [Dict[str, Any]], UpdateOne
] = (
    lambda document: UpdateOne(
        {
            "user_id_str":
                document["tweet_data"]["user"]["id_str"],
            "tweet_content":
                document["tweet_data"]["text"]
        },
        {"$set": {
            # unordered save
            "tweet_id": document["_id"],
            "user_id_str":
                document["tweet_data"]["user"]["id_str"],
            "tweet_content":
                document["tweet_data"]["text"]
        }},
        upsert=True
    )
)

update_one_as_description_schema: Callable[[Dict[str, Any]], UpdateOne] = (
    # retrieve default tweet schema and save it as description schema
    # location_name is required
    lambda document: UpdateOne(
        {"tweet_id": document["_id"]},
        {"$set": {
            "user_id_str": document["tweet_data"]["user"]["id_str"],
            "description": document["tweet_data"]["user"]["description"],
            "location_name": document["location_name"]
        }},
        upsert=True
    )
)

update_one_from_description_scheme: Callable[[Dict[str, Any]], bool] = (
    lambda document: UpdateOne(
        {"tweet_id": document["tweet_id"]},
        {"$set": {
            "user_id_str": document["user_id_str"],
            "description": document["description"],
            "location_name": document["location_name"]
        }},
        upsert=True
    )
)

create_update_one_as_description_by_distinct_user: Callable[
    [Dict[str, Any]], UpdateOne] = (
    lambda document: UpdateOne(
        {"user_id_str": document["tweet_data"]["user"]["id_str"]},
        {
            "$set": {
                "tweet_id": document["_id"],
                "user_id_str": document["tweet_data"]["user"]["id_str"],
                "description":
                    document["tweet_data"]["user"]["description"],
                "location_name": document["location_name"]
            }
        },
        upsert=True
    )
)

retrieve_word_from_count_by_word: Callable[[Dict[str, Any]], str] = (
    lambda document: document["word"]
)


def is_liked_or_really_liked_surface(
    from_surface: str,
    to_surface: str
) -> bool:
    if (is_include_like_or_really_like(from_surface, to_surface)
        ) and not(
        is_include_list_element_string_in_target_string(
            OPPOSITE_WORDS_FOR_LIKE,
            to_surface
        )
    ):
        return True
    if (is_include_like_or_really_like(from_surface, to_surface)
        ) and not(
        is_include_list_element_string_in_target_string(
            OPPOSITE_WORDS_FOR_LIKE,
            from_surface
        )
    ):
        return True

    return False


def is_include_ga_like_or_really_like(
    from_surface: str,
    to_surface: str
) -> bool:
    return is_include_pattern(
        re.compile("(.)+が$"),
        re.compile("(.)*[(好き)|(大好き)](.)*"),
        from_surface,
        to_surface
    )


def is_include_pattern(
    pattern_from_surface: Pattern,
    pattern_to_surface: Pattern,
    from_surface: str,
    to_surface: str
) -> bool:
    if pattern_from_surface.search(from_surface) and (
            pattern_to_surface.search(to_surface)
    ):
        return True
    return False


def is_include_like_or_really_like_and_yoro(
    from_surface: str,
    to_surface: str
) -> bool:
    if "好き" in from_surface or "大好き" in from_surface:
        if "よろしくお願いします" in to_surface:
            return True
    if "好き" in to_surface or "大好き" in to_surface:
        if "よろしくお願いします" in from_surface:
            return True
    return False


def select_surface_include_like_or_really_like(
    from_surface: str,
    to_surface: str
) -> str:
    """
        * return surface not include like or really like
    """
    if "好き" in to_surface or "大好き" in to_surface:
        return from_surface
    if "好き" in from_surface or "大好き" in from_surface:
        return to_surface

    print("{}, {}".format(from_surface, to_surface))
    raise Exception("like or really like is not included")


select_from_surface: Callable[[str, str], str] = (
    # return from_surface regardless of to_surface
    lambda from_surface, _: from_surface
)


def create_update_one_as_format_created_at(
    document: Dict[str, Any]
) -> UpdateOne:
    document["tweet_data"]["created_at"] = (
        convert_utc_str_to_jst_date(
            document["tweet_data"]["created_at"]
        )
    )
    UpdateOne(
        {"_id": document["_id"]},
        {"$set": document},
        upsert=True
    )


def create_update_one_by_distinct_user(
    document: Dict[str, Any]
) -> UpdateOne:
    return (
        UpdateOne(
            {"tweet_data.user.id_str":
                document["tweet_data"]["user"]["id_str"]},
            {"$set": {
                "tweet_id": document["_id"],
                "tweet_data": document["tweet_data"],
                "location_name": document["location_name"]
            }},
            upsert=True
        )
    )


skip_loop_when_created_at_is_datetime: Callable[
    [Union[str, datetime]], bool] = (
    lambda created_at: isinstance(created_at, datetime)
)

is_beginning_specific_location: Callable[[Dict[str, Any], str], bool] = (
    lambda document, location_name: re.search("^{}(.)+".format(
        location_name
    ), document["location_name"])
)

is_not_beginning_specific_location: Callable[[Dict[str, Any], str], bool] = (
    lambda document, location_name: not is_beginning_specific_location(
        document, location_name
    )
)
