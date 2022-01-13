import json
from typing import Any, Dict, List, Optional

import requests
import requests_oauthlib
from requests import Response
from requests_oauthlib.oauth1_session import OAuth1Session
from src.annotation.interface import ITweetSaveSchema, ITwitterApiTokens
from src.collection.mongo_saver import MongoSaver
from src.core.loader import CollectionConfigLoader
from src.core.mongo_connection import MongoConnection
from src.util.logger import LoggerFactory
from typing_extensions import Final


class TwitterApi:

    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_tokens: Optional[ITwitterApiTokens] = None,
        params: Optional[Dict[str, str]] = None,
    ):
        self.endpoint = endpoint if not(
            endpoint is None
        ) else CollectionConfigLoader.get_twitter_api_endpoint()
        self.api_tokens: ITwitterApiTokens = (
            api_tokens if not(
                api_tokens is None
            ) else CollectionConfigLoader.get_twitter_api_tokens()
        )
        self.params: Dict[str, str] = (
            params if not(
                params is None
            ) else CollectionConfigLoader.get_twitter_api_request_params()
        )
        self.logger = LoggerFactory.create_save_info_or_more()

    def set_config_mongo(
        self
    ) -> None:
        self.save_mongo: MongoConnection = (
            MongoConnection.create_twitter_api_mongo_instance_from_config()
        )

    def set_session(self) -> None:
        self.session: OAuth1Session = requests_oauthlib.OAuth1Session(
            self.api_tokens["consumer_key"],
            self.api_tokens["consumer_secret"],
            self.api_tokens["access_token"],
            self.api_tokens["access_token_secret"]
        )


class TwitterStreamApi(TwitterApi):
    def get_and_save(self) -> None:

        LIMIT: Final[str] = 100
        save_tweets: List[ITweetSaveSchema] = []

        self.set_config_mongo()
        self.set_session()
        response: Response = self.session.post(
            self.endpoint,
            data=self.params,
            stream=True
        )

        try:
            for line in response.iter_lines():
                tweet: Dict[str, Any] = json.loads(line.decode("utf-8"))
                formated_tweet: ITweetSaveSchema = self.format_tweet(
                    tweet
                )
                save_tweets.append(formated_tweet)
                if len(save_tweets) == LIMIT:
                    MongoSaver.save_as_insert_many(
                        self.save_mongo,
                        save_tweets
                    )
                    save_tweets.clear()
                    self.logger.info("{} saved".format(LIMIT))

        # the following exceptions sometimes happen
        except json.decoder.JSONDecodeError:
            pass
        except requests.exceptions.ChunkedEncodingError:
            pass

    def format_tweet(
        self,
        tweet: Dict[str, Any]
    ) -> ITweetSaveSchema:
        formated_tweet: Dict[str, Any] = {}
        formated_tweet["_id"] = tweet["id_str"]
        del tweet["id_str"]
        formated_tweet["tweet_data"] = tweet
        return formated_tweet
