from src.analysis.tweet_dependency_structure_analyzer import \
    TweetDependencyStructureAnalyzer
from src.util.callback import (is_include_like_or_really_like_and_yoro,
                               retrieve_tweet_description_as_default,
                               retrieve_tweet_text_as_default,
                               select_surface_include_like_or_really_like)
from src.util.query import create_query_like_or_really_like


def run(key) -> None:
    dependency_analysis: TweetDependencyStructureAnalyzer
    if key == 1:
        # display format as dependency
        dependency_analysis = TweetDependencyStructureAnalyzer(
            "tweets"
        )
        dependency_analysis.display_as_dependency_format(
            retrieve_tweet_description_as_default
        )
    elif key == 2:
        # save morpheme on condition of callbacks
        dependency_analysis = TweetDependencyStructureAnalyzer(
            "202104_tweets",
            "_test_dependency_tweets"
        )
        dependency_analysis.save_morpheme(
            is_include_like_or_really_like_and_yoro,
            select_surface_include_like_or_really_like,
            retrieve_tweet_text_as_default,
            "名詞",
            create_query_like_or_really_like("tweet_data.text")
        )


run(2)
