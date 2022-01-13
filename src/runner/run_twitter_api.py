from src.collection.twitter_api import TwitterStreamApi


def run(pattern: int) -> None:
    if pattern == 1:
        twitter_stream_api: TwitterStreamApi = TwitterStreamApi()
        twitter_stream_api.get_and_save()


run(1)
