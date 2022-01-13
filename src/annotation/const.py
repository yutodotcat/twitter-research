from typing import Dict, List

from typing_extensions import Final

from .interface import IMongoConfigKeys

MONGO_CONFIG_KEYS: IMongoConfigKeys = {
    key: key for key in [
        "auth",
        "database_name",
        "collection_name",
        "host",
        "port",
        "username",
        "password",
        "authSource",
        "authMechanism",
    ]
}

COUNT_BY_SOURCE_WITH_PERCENT: Final[str] = (
    "count_by_source_with_percent"
)

TABLE_HEADER: Final[List[str]] = [
    "都道府県", "Iphone", "Android",
    "Foursquare", "instagram", "Foursquare Swarm",
    "Twitter for iPad"
]

TABLE_BODY: Final[List[str]] = [
    "prefecture",
    "iphone",
    "android",
    "foursquare",
    "instagram",
    "foursquare_swarm",
    "twitter_for_ipad"
]

TARGET_SOURCE: Final[Dict[str, str]] = {
    "iphone":
    (
        '<a href=\"http://twitter.com/download/iphone\"'
        ' rel=\"nofollow\">'
        'Twitter for iPhone</a>'
    ),
    "android":
    (
        '<a href=\"http://twitter.com/download/android\"'
        ' rel=\"nofollow\">Twitter for Android</a>'
    ),
    "foursquare":
    (
        '<a href=\"http://foursquare.com\"'
        ' rel=\"nofollow\">Foursquare</a>'
    ),
    "instagram":
    (
        '<a href=\"http://instagram.com\"'
        ' rel=\"nofollow\">Instagram</a>'
    ),
    "foursquare_swarm":
    (
        '<a href=\"https://www.swarmapp.com\"'
        ' rel=\"nofollow\">Foursquare Swarm</a>'
    ),
    "twitter_for_ipad":
    (
        '<a href=\"http://twitter.com/#!/download/ipad\"'
        ' rel=\"nofollow\">Twitter for iPad</a>'
    )
}
