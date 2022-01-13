
import re
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Pattern, Set

import emoji
import MeCab
from pymongo import UpdateOne
from pymongo.cursor import Cursor
from src.analysis.tweet_analysis_core import TweetAnalysisCore
from src.annotation.type import OptionalQuery, PartOfSpeach, RetrieveCallback
from src.util.emoji_me import UNNESESSARY_EMOJI
from src.util.nlp import ADJECTIVE, EOS, EOS_LENGTH, NOUN, PROPER_NOUN
from src.util.prefecture import PREFECTURES
from tqdm import tqdm
from typing_extensions import Final, Literal, TypedDict

from .text_analyze_service import TextAnalyzeService


class TweetMorphologicalAnalysis(TweetAnalysisCore):

    mecab: MeCab.Tagger = TextAnalyzeService.get_mecab_instance()

    @TweetAnalysisCore.unrequired_save_mongo
    def display_all_as_morpheme(
        self,
        retrieve_callback: Callable[[Dict[str, Any]], str],
        part_of_speech: Optional[PartOfSpeach] = None,
        optional_query: OptionalQuery = None
    ) -> None:
        """
        Comments:
            * to see text as morpheme
        """
        cursor: Cursor
        total_count: int

        cursor, total_count = self.get_cursor_and_count_from_retrieve(
            optional_query
        )

        for document in tqdm(
            cursor,
            total=total_count
        ):
            retrieved_text: str = retrieve_callback(document)
            if retrieved_text is None:
                # when null
                continue
            parsed_tweet_text: str = self.mecab.parse(
                retrieved_text
            )
            for one_line_morpheme in parsed_tweet_text.splitlines():
                morpheme_list: List[str] = one_line_morpheme.split("\t")
                if part_of_speech is None:
                    self.logger.debug(morpheme_list)
                else:
                    if len(morpheme_list) == EOS_LENGTH:
                        continue
                    morpheme_information_list: List[str] = (
                        morpheme_list[1].split(",")
                    )
                    if morpheme_information_list[0] == part_of_speech:
                        self.logger.debug(morpheme_list)

    @TweetAnalysisCore.require_save_mongo
    def count_word_and_save(
        self,
        retrieve_callback: RetrieveCallback,
        part_of_speech: PartOfSpeach = "名詞",
        optional_query: OptionalQuery = None,
    ) -> None:
        """
        Comments:
            * count and save word of tweet or description
            * noun as second element of parsed text
            * such as [youtube 名詞,固有名詞,一般]
        Args:
            * parse_field: target to be parsed
            * optional_query:
                mongodb query
                this is used
                when gt id or include some specific keyword is necessary
        """
        LIMIT: Final[int] = 200000

        self.check_and_create_single_index(
            "word",
            retrieve=False,
            save=True
        )

        save_words: Dict[str, int] = {}
        cursor, total_count = self.get_cursor_and_count_from_retrieve(
            optional_query
        )

        for document in tqdm(cursor, total=total_count):
            parse_target_text: str = ""

            parse_target_text = retrieve_callback(document)

            if parse_target_text is None:
                # is null
                # in description
                continue

            parsed_text: str = self.mecab.parse(parse_target_text)

            for one_line_morpheme in parsed_text.splitlines():
                morpheme_list: List[str] = one_line_morpheme.split("\t")

                if len(
                    morpheme_list
                ) == EOS_LENGTH and morpheme_list[0] == EOS:
                    break

                try:
                    # like: ['名詞', '一般', '*', '*', '*', '*', '霧', 'キリ', 'キリ']
                    splited_morpheme_explanation: List[str] = (
                        morpheme_list[1].split(",")
                    )
                    word: str
                    if part_of_speech == NOUN:
                        if splited_morpheme_explanation[0] == NOUN:
                            word = morpheme_list[0]
                            if not (word in save_words.keys()):
                                save_words[word] = 1
                            else:
                                save_words[word] = save_words[word] + 1
                    elif part_of_speech == PROPER_NOUN:
                        if splited_morpheme_explanation[1] == PROPER_NOUN:
                            word = morpheme_list[0]
                            if not (word in save_words.keys()):
                                save_words[word] = 1
                            else:
                                save_words[word] = save_words[word] + 1
                    elif part_of_speech == ADJECTIVE:
                        if splited_morpheme_explanation[0] == ADJECTIVE:
                            word = morpheme_list[0]
                            if not (word in save_words.keys()):
                                save_words[word] = 1
                            else:
                                save_words[word] = save_words[word] + 1
                    else:
                        raise ValueError("part of speech is invalid")

                except IndexError:
                    # when string is ''
                    self.logger.info("error list: {}".format(morpheme_list))

            if len(save_words) >= LIMIT:
                self.logger.info((
                    "{}: {} save operations until id: {} (is included) "
                    "have been performed"
                ).format(datetime.now(), len(save_words), document["_id"]))
                self.upsert_count_by_word(save_words)
                save_words = {}

        if len(save_words) > 0:
            self.upsert_count_by_word(save_words)
            self.logger.info((
                "{}: {} save operation until id: {} (is included) "
                "have been performed as last operation"
            ).format(datetime.now(), len(save_words), document["_id"]))

    def upsert_count_by_word(
        self,
        save_words: Dict[str, int]
    ) -> None:
        """
        Comments:
            * update count and insert document not to be saved
        Args:
            * save_words: {"word": 5, "word2": 9 ...}
        """

        I_WORD_COUNT = TypedDict(
            "I_WORD_COUNT", {"count": int, "word": str}
        )

        class IWordCountHasId(I_WORD_COUNT, total=True):
            _id: str

        bulk_op_saved_word: List = []
        keys_save_words: List[str] = list(save_words.keys())
        already_saved_words: List[IWordCountHasId] = list(
            self.save_mongo.collection.find({"word": {"$in": keys_save_words}})
        )

        for word_document in already_saved_words:
            saved_word: str = word_document["word"]
            word_document["count"] = (
                word_document["count"] + save_words[saved_word]
            )
            bulk_op_saved_word.append(
                UpdateOne(
                    {"word": saved_word},
                    {"$set": {
                        "word": saved_word,
                        "count": word_document["count"]
                    }}
                )
            )
            del save_words[saved_word]

        insert_words: List[I_WORD_COUNT] = [
            {"word": word, "count": count}
            for word, count in save_words.items()
        ]

        if bulk_op_saved_word:
            self.save_mongo.collection.bulk_write(bulk_op_saved_word)
        self.save_mongo.collection.insert_many(insert_words)
        self.logger.info(
            "bulk and insert operations have been done successfully"
        )

    def count_emoji(
        self,
        cursor: Cursor,
        target_of_analysis: Literal["tweet", "description"] = "tweet"
    ) -> List[Dict[str, int]]:
        """
        Comments:
            * create emoji count list from cursor
        Returns:
            * like: [{":sob:", 5} , {":joy:", 10} ...]
        """
        emoji_set: Set[str] = set(
            emoji for emoji in emoji.UNICODE_EMOJI["en"].keys() if not (
                emoji in UNNESESSARY_EMOJI
            )
        )
        emoji_counter: Dict[str, int] = {emoji: 0 for emoji in emoji_set}

        total_coumt: int = cursor.count()
        for tweet in tqdm(cursor, total=total_coumt):
            parsed_tweet_text: str = ""

            if target_of_analysis == "tweet":
                parsed_tweet_text = self.mecab.parse(
                    tweet["tweet_data"]["text"]
                )
            elif target_of_analysis == "description":
                parsed_tweet_text = self.mecab.parse(tweet["description"])
            else:
                raise ValueError("target_of_analysis value is invalid")

            if isinstance(parsed_tweet_text, bool):
                # when target field is null
                # this occurs when target is description
                continue

            for one_line_morpheme in parsed_tweet_text.splitlines():
                morpheme_list: List[str] = one_line_morpheme.split("\t")
                if morpheme_list[0] in emoji_set:
                    emoji_counter[
                        morpheme_list[0]
                    ] = emoji_counter[morpheme_list[0]] + 1
        # the following lines are workaround
        emoji_counter_list: List[Dict[str, int]] = [{
            "emoji": emoji_count[0],  # type: ignore
            "count": emoji_count[1]
        } for emoji_count in sorted(
            emoji_counter.items(), key=lambda x: x[1], reverse=True
        )]

        return emoji_counter_list

    @TweetAnalysisCore.require_save_mongo
    def count_and_save_emoji(
        self,
        target_of_analysis: Literal["tweet", "description"] = "tweet"
    ) -> None:
        """
        Comments:
            * parse text is changed by retrieve collection
            * to create index is not needed
            * because target documents are a little
        Args:
            target_of_analysis:
                * depend on schema
        """
        cursor: Cursor = self.retrieve_mongo.collection.find({})
        emoji_counter_list: List[Dict[str, int]] = self.count_emoji(
            cursor, target_of_analysis
        )

        self.save_mongo.collection.update_one(
            {"collection_name": self.retrieve_mongo.collection.name},
            {
                "$set": {
                    "collection_name": self.retrieve_mongo.collection.name,
                    "emoji_count": emoji_counter_list
                }
            },
            upsert=True
        )
        self.logger.info(
            ("emoji count and save operation"
             "has been completed successfully"
             )
        )

    def count_and_save_by_prefecture(
        self,
        target_of_analysis: Literal["tweet", "description"] = "tweet"
    ) -> None:
        """
        Comments:
            * if operation fails on loop there is no problem
        Args:
            * target_of_analysis: tweet content or description in tweet
        """

        prefecture_length: int = len(PREFECTURES)

        self.check_and_create_single_index(
            "location_name", retrieve=True, save=False)

        for prefecture in tqdm(PREFECTURES, total=prefecture_length):

            if not(self.save_mongo.collection.find_one(
                {"prefecture": prefecture}
            ) is None):
                self.logger.debug("{} is already saved".format(prefecture))
                continue

            regex_prefecture: Pattern[str] = re.compile(
                "^{}(.)*".format(prefecture)
            )
            cursor: Cursor = self.retrieve_mongo.collection.find(
                {"location_name": {"$regex": regex_prefecture}}
            )

            emoji_counter_list: List[Dict[str, int]] = self.count_emoji(
                cursor, target_of_analysis
            )

            self.save_mongo.collection.update_one(
                {"prefecture": prefecture},
                {
                    "$set": {
                        "prefecture": prefecture,
                        "emoji_count": emoji_counter_list
                    }
                },
                upsert=True
            )
            self.logger.info(
                ("emoji count and save operation by prefecture {}"
                 "has been perfomed successfully".format(prefecture)
                 )
            )
