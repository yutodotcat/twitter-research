from src.analysis.model_creator import ModelCreator
from src.util.callback import retrieve_tweet_description_as_default


def run(key: int) -> None:
    model_create: ModelCreator
    if key == 1:
        model_create = ModelCreator(
            "202107_tweets"
        )
        model_create.create_model_from_twitter(
            "2021_tweets_description.model",
            retrieve_tweet_description_as_default
        )


run(1)
