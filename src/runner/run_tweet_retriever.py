from src.analysis.tweet_retriever import TweetRetriever
from src.util.callback import update_one_as_default_schema
from src.util.query import create_query_regex_pattern_location


def run(key: int) -> None:
    tweet_retriever: TweetRetriever
    if key == 1:
        pass
    if key == 2:
        tweet_retriever = TweetRetriever(
            "tweets",
            "_test_202107_tweets"
        )
        tweet_retriever.copy_to_another_collection_by_monthly_date(
            "202107"
        )
    elif key == 4:
        tweet_retriever = TweetRetriever(
            "202107_tweets", "_test_202107_tweets_distinct_tweet_by_user"
        )
        tweet_retriever.retrieve_and_save_distinct_tweet()
    elif key == 6:
        # retrieve and save some location tweets
        tweet_retriever = TweetRetriever(
            "tweets", "_test_retrieve_some_location_tweets"
        )
        tweet_retriever.retrieve_and_save_by_location(
            update_one_as_default_schema,
            create_query_regex_pattern_location(
                "東京都渋谷区"
            )
        )
    elif key == 7:
        # copy tweets include some keywords
        # from default schema to default schema
        tweet_retriever = TweetRetriever(
            "tweets", "_test_retrieve_and_save_some_tweet_include_some_keyword"
        )
        tweet_retriever.check_and_create_single_index(
            "tweet_data.text",
            retrieve=True,
            save=False
        )
        tweet_retriever.retrieve_and_save_include_some_keyword(
            update_one_as_default_schema,
            {"tweet_data.text": {"$regex": "好き"}}
        )
    elif key == 8:
        # run copy document method for mock
        tweet_retriever = TweetRetriever(
            "202107_tweets", "_test_retrieve_tweet_copy_document"
        )
        tweet_retriever.copy_document(
            {"tweet_data.text": {"$regex": "おはようございます"}}
        )


run(7)
