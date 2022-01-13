from src.annotation.type import OptionalQuery, RetrieveCallback

from .tweet_analysis_core import TweetAnalysisCore


class DescriptionRetriever(TweetAnalysisCore):

    @TweetAnalysisCore.require_save_mongo
    def retrieve_and_save(
        self,
        update_callback: RetrieveCallback,
        optional_query: OptionalQuery = None,
    ) -> None:
        """
        Comments:
            * depends on update_callback and optional_query
        """
        super().retrieve_and_save(update_callback, optional_query)
