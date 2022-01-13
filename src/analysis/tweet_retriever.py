from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from src.annotation.type import OptionalQuery, RetrieveCallback
from src.util.callback import (update_one_as_default,
                               update_one_as_distinct_tweet_by_user)
from typing_extensions import Final

from .tweet_analysis_core import TweetAnalysisCore


class TweetRetriever(TweetAnalysisCore):
    """
        * this class is used when tweet data is retrieved
        * move tweet data
    """

    @TweetAnalysisCore.require_save_mongo
    def retrieve_and_save_include_some_keyword(
        self,
        update_callback: RetrieveCallback,
        optional_query: OptionalQuery = None,
        callback_skip_loop: Optional[Callable[[Any], bool]] = None
    ):
        """
            * keyword is included in tweet such as "わろた"
            * this method depends on optional_query
        """
        self.retrieve_and_save(
            update_callback,
            optional_query,
            callback_skip_loop,
        )

    @TweetAnalysisCore.require_save_mongo
    def retrieve_and_save_by_location(
        self,
        update_callback: RetrieveCallback,
        optional_query: OptionalQuery = None,
        callback_skip_loop: Optional[Callable[[Any], bool]] = None,
    ) -> None:
        """
            * summary:
                retrieve and save tweet to another collection by location
            * schema: from default schema to default schema
        Args:
            * update_callback:
                copy tweet_data itself
            * optional_query:
                must include regex pattern such as
                begining strings of location name like "東京都渋谷区" or "東京"
        """
        self.check_and_create_single_index(
            "location_name",
            retrieve=True,
            save=False
        )
        self.retrieve_and_save(
            update_callback,
            optional_query,
            callback_skip_loop
        )

    @TweetAnalysisCore.require_save_mongo
    def copy_to_another_collection_by_monthly_date(
        self,
        year_month: str,
        gt_id: Optional[str] = None
    ) -> None:
        """
            * summary: copy collection by monthly date
            * schema: from default schema to default schema
        Args:
            * year_month:
                like: "202104"
                prefix 0 is required
                4 is expressed as 04
            * gt_id:
                greater than id
        """

        START_DAY: Final[int] = 1
        year: int = int(year_month[0:4])
        month: int = int(year_month[4:6])

        ID: Final[str] = "_id"
        TWEET_DATE_CREATED_AT: Final[str] = "tweet_data.created_at"

        self.save_mongo.collection.create_index(
            [
                (ID, 1),
                (TWEET_DATE_CREATED_AT, 1)
            ]
        )

        and_queries: List[Dict[str, Dict[str, Any]]] = [
            {TWEET_DATE_CREATED_AT:
                {
                    "$gte":
                    datetime(year, month, START_DAY) - timedelta(hours=9),
                    "$lt":
                    datetime(
                        year, month + 1, START_DAY
                    ) - timedelta(hours=9)
                }
             }
        ]
        if not(gt_id is None):
            and_queries.insert(0, {ID: {"$gt": gt_id}})

        self.retrieve_and_save(
            update_one_as_default,
            {
                "$and": and_queries
            }
        )

    @TweetAnalysisCore.require_save_mongo
    def retrieve_and_save_distinct_tweet(
        self,
        gt_id: Optional[str] = None,
    ) -> None:
        """
            * schema:
                from default schema to distinct tweet by user schema
            * when user_id and tweet_data.text is equal to db tweet_data
            * tweet save not occurs
            * example: AAA by userA, AAA by userA
            * the above count is 1
            * example: AAB by userA, AAA by userA
            * the above count is 2
        """
        query: Optional[Dict[str, Any]] = None if gt_id is None else {
            "_id": {"gt": gt_id}
        }
        self.save_mongo.collection.create_index(
            [
                ("user_id_str", 1),
                ("tweet_content", 1)
            ]
        )
        self.retrieve_and_save(
            update_one_as_distinct_tweet_by_user,
            query
        )

    @TweetAnalysisCore.require_save_mongo
    def copy_document(
        self,
        optional_query: OptionalQuery,
        loop: int = 500
    ) -> None:
        """
            * for creating mock data
        """
        for count, document in enumerate(
            self.retrieve_mongo.collection.find(
                {} if optional_query is None else optional_query
            ), 1
        ):
            self.save_mongo.collection.insert_one(document)
            if count == loop:
                break
        self.logger.info("copy operation has been performed")
