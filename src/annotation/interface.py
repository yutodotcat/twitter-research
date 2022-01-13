from typing import Any, Dict

from typing_extensions import TypedDict

IMongoConfigKeys = TypedDict(
    "IMongoConfigKeys", {
        "auth": str,
        "database_name": str,
        "collection_name": str,
        "host": str,
        "port": str,
        "username": str,
        "password": str,
        "authSource": str,
        "authMechanism": str
    }
)

ICountPercentBySource = TypedDict(
    "ICountPercentBySource", {
        "id": str,  # is source such as iphone
        "count": int,
        "percent": float
    }
)

IEmojiCount = TypedDict(
    "IEmojiCount", {
        "emoji": str,
        "count": int
    }
)

ITwitterApiTokens = TypedDict(
    "ITwitterApiTokens", {
        "consumer_key": str,
        "consumer_secret": str,
        "access_token": str,
        "access_token_secret": str
    }
)

ITweetSaveSchema = TypedDict(
    "IDefaultTweetSaveSchema", {
        "_id": str,
        "tweet_data": Dict[str, Any]
    }
)

ITweetSaveSchemaHasLocation = TypedDict(
    "ITweetSaveSchemaHasLocation", {
        "_id": str,
        "tweet_data": Dict[str, Any],
        "location_name": str
    }
)
