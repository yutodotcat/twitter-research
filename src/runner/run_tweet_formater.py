from src.collection.twitter_api import TweetFormater


def run(pattern: int) -> None:
    if pattern == 1:
        tweet_formater: TweetFormater = TweetFormater(
            "tweets",
            "tweets",
            is_same_collection_accepted=True
        )
        tweet_formater.convert_string_datetime()


run(1)
