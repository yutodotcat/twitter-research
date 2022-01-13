from typing import List

from gensim.models import word2vec
from gensim.models.word2vec import Word2Vec
from MeCab import Tagger
from pymongo.cursor import Cursor
from src.annotation.type import OptionalQuery, RetrieveCallback
from src.core.mongo_connection import MongoConnection
from src.util.logger import LoggerFactory
from tqdm import tqdm

from .text_analyze_service import TextAnalyzeService


class ModelCreator:

    def __init__(self, retrieve_collection: str) -> None:
        self.retrieve_mongo: MongoConnection = (
            MongoConnection.create_one_instance(
                retrieve_collection
            )
        )
        self.mecab: Tagger = TextAnalyzeService.get_wakati_mecab_instance()
        self.logger = LoggerFactory.create_save_info_or_more()

    def create_model_from_twitter(
        self,
        model_file_name: str,
        retrieve_callback: RetrieveCallback,
        optional_query: OptionalQuery = None
    ) -> None:
        """
        Args:
            * model_file_name: include . such as warota.model
        """
        cursor: Cursor = self.retrieve_mongo.collection.find(
            {} if optional_query is None else optional_query
        )
        total_count: int = cursor.count()
        token_list: List[List[str]] = []
        is_first_train: bool = True

        for document in tqdm(cursor, total=total_count):
            sentence: str = retrieve_callback(
                document
            )
            if sentence is None:
                # when null
                continue
            node: str = self.mecab.parse(
                sentence
            )
            splited_node: List[str] = node.split(" ")

            # temporary stop word remove
            while True:
                if "\n" in splited_node:
                    splited_node.remove("\n")
                else:
                    break

            token_list.append(splited_node)

            if len(token_list) == 100000:
                if is_first_train:
                    new_model = Word2Vec(
                        token_list,
                        size=100,
                        min_count=5,
                        window=5,
                        iter=3
                    )
                    new_model.save(
                        model_file_name
                    )
                    is_first_train = False
                    token_list.clear()
                else:
                    train_model = word2vec.Word2Vec.load(
                        model_file_name
                    )
                    train_model.train(
                        sentences=token_list,
                        total_examples=sum(
                            [len(tokens)
                             for tokens in token_list]),
                        epochs=train_model.iter
                    )
                    train_model.save(
                        model_file_name
                    )
                    token_list.clear()

        if len(token_list) > 0:
            train_model = word2vec.Word2Vec.load(
                model_file_name
            )
            train_model.train(
                sentences=token_list,
                total_examples=sum(
                    [len(tokens)
                        for tokens in token_list]),
                epochs=train_model.iter
            )
            train_model.save(
                model_file_name
            )
