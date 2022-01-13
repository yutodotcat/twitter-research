from src.annotation.type import OptionalQuery
from util.callback import (create_update_one_as_format_created_at,
                           skip_loop_when_created_at_is_datetime)

from tweet_analysis_core import TweetAnalysisCore


class TweetFormater(TweetAnalysisCore):

    @TweetAnalysisCore.require_save_mongo
    def convert_string_datetime(
        self,
        optional_query: OptionalQuery = None
    ) -> None:
        """
            * convert string datetime format to datetime object
        """
        self.retrieve_and_save(
            create_update_one_as_format_created_at,
            optional_query,
            skip_loop_when_created_at_is_datetime
        )
