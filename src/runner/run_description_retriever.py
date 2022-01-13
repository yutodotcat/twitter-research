from src.analysis.description_retriever import DescriptionRetriever
from src.util.callback import update_one_as_description_schema


def run(pattern: int):
    description_retriever: DescriptionRetriever
    if pattern == 1:
        description_retriever = DescriptionRetriever(
            "tweets",
            "_________desctiption_test_run"
        )
        description_retriever.check_and_create_single_index(
            "tweet_id",
            retrieve=False,
            save=True
        )
        description_retriever.retrieve_and_save(
            update_one_as_description_schema
        )


run(1)
