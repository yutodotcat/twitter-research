import re

from src.analysis.tweet_morphological_analysis import \
    TweetMorphologicalAnalysis
from src.util.callback import retrieve_tweet_description_as_default
from src.util.prefecture import PREFECTURES
from tqdm import tqdm


def run(key: int) -> None:
    tweet_morphological_analysis: TweetMorphologicalAnalysis
    if key == 0:
        tweet_morphological_analysis = TweetMorphologicalAnalysis(
            "tweets"
        )
        tweet_morphological_analysis.display_all_as_morpheme(
            retrieve_tweet_description_as_default
        )
    elif key == 1:
        # count some adjuctive count
        tweet_morphological_analysis = TweetMorphologicalAnalysis(
            "202104_tweets",
            "_test_202107_tweets_like_or_really_like_adjuctive"
        )
        tweet_morphological_analysis.check_and_create_single_index(
            "tweet_data.user.description",
            retrieve=True,
            save=False
        )
        tweet_morphological_analysis.count_word_and_save(
            retrieve_tweet_description_as_default,
            "形容詞",
            {"$or": [
                {"tweet_data.user.description": re.compile("好き")},
                {"tweet_data.user.description": re.compile("大好き")}
            ]}
        )
    if key == 2:
        # run morphological analysis
        # by prefectures
        for prefecture in tqdm(PREFECTURES.keys()):
            tweet_morphological_analysis = TweetMorphologicalAnalysis(
                "202107_tweets_distinct_by_user",
                ("proper_noun_include_like_or_really_"
                 "like_202107_tweets_distinct_by_user_{}".format(
                     prefecture
                 ))
            )
            analysis_alias = tweet_morphological_analysis
            analysis_alias.retrieve_mongo.collection.create_index(
                [
                    ("tweet_data.user.description", 1),
                    ("location_name", 1)
                ]
            )

            tweet_morphological_analysis.count_word_and_save(
                retrieve_tweet_description_as_default,
                "固有名詞",
                {"$and": [
                    {"location_name": re.compile("^{}(.)*".format(
                        prefecture
                    ))},
                    {"$or": [
                        {"tweet_data.user.description": re.compile("好き")},
                        {"tweet_data.user.description": re.compile("大好き")}
                    ]}
                ]}
            )


run(1)
