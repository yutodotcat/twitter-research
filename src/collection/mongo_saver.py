
from typing import Any, Dict, List

from src.core.mongo_connection import MongoConnection


class MongoSaver:
    """
        * this class depends on MongoConnection class
    """
    @classmethod
    def save_as_insert_many(
        cls,
        save_mongo: MongoConnection,
        tweet_list: List[Dict[str, Any]]
    ) -> None:
        """
        Args:
            * tweet_list is like
                [
                    {"_id": <str>, "tweet_data", <dict>},
                    {"_id": <str>, "tweet_data", <dict>},
                    ...
                ]
        """
        save_mongo.collection.insert_many(tweet_list)
