from typing import Any, Callable, Dict, List, Optional

from CaboCha import Chunk, Parser, Tree
from MeCab import Tagger
from pymongo.cursor import Cursor
from src.annotation.type import OptionalQuery, PartOfSpeach, RetrieveCallback
from src.util.nlp import ADJECTIVE, EOS_LENGTH, NOUN, PROPER_NOUN
from tqdm import tqdm

from .text_analyze_service import TextAnalyzeService
from .tweet_analysis_core import TweetAnalysisCore


class TweetDependencyStructureAnalyzer(TweetAnalysisCore):

    LIMIT: int = 100

    cabocha: Parser = TextAnalyzeService.get_cabocha_instance()
    mecab: Tagger = TextAnalyzeService.get_mecab_instance()

    def generate_chunks(self, tree) -> Dict[int, Chunk]:
        """
            * create chunk dict from Tree
        """
        chunks: Dict[int, Chunk] = {}
        key: int = 0

        for loop in range(tree.size()):
            token = tree.token(loop)
            if token.chunk:
                chunks[key] = token.chunk
                key += 1

        return chunks

    def get_surface(self, tree, chunk) -> str:
        """
            * get surface by getting token of tree from chunk
        """
        surface: str = ""
        begin = chunk.token_pos
        end = chunk.token_pos + chunk.token_size

        for loop in range(begin, end):
            token = tree.token(loop)
            surface += token.surface

        return surface

    @TweetAnalysisCore.unrequired_save_mongo
    def display_as_dependency_format(
        self,
        callback_retrieve: RetrieveCallback,
        callback_should_show: Optional[Callable[[str, str], bool]] = None,
        optional_query: OptionalQuery = None,
        max_loop: int = 500
    ) -> None:
        """
            * display format like AAA -> BBB
            * such as
            * 駆け出しエンジニア。 -> ブロックします
        """
        cursor: Cursor

        cursor, _ = self.get_cursor_and_count_from_retrieve(
            optional_query
        )

        for loop, document in enumerate(cursor):
            if loop == max_loop:
                self.logger.info(
                    "looop achieved max_loop"
                )
                break

            target_text: str = callback_retrieve(document)

            if target_text is None:
                continue

            tree: Tree = self.cabocha.parse(target_text)
            chunks: Dict[int, Any] = self.generate_chunks(tree)

            for from_chunk in chunks.values():
                if from_chunk.link < 0:
                    continue

                from_surface: str = self.get_surface(tree, from_chunk)
                to_chunk: Chunk = chunks[from_chunk.link]
                to_surface: str = self.get_surface(tree, to_chunk)

                if callback_should_show is None:
                    self.logger.info(
                        "{} -> {}".format(
                            from_surface, to_surface
                        )
                    )
                else:
                    if callback_should_show(from_surface, to_surface):
                        self.logger.info(
                            "{} -> {}".format(
                                from_surface, to_surface
                            )
                        )

    @TweetAnalysisCore.require_save_mongo
    def save_morpheme(
        self,
        callback_should_save: Callable[[str, str], bool],
        callback_select_surface: Callable[[str, str], str],
        callback_retrieve: Callable[[Dict[str, Any]], str],
        part_of_speech: PartOfSpeach = "名詞",
        optional_query: OptionalQuery = None
    ) -> None:
        """
            * save morpheme has some dependency
            * like {"word": 5, "word2": 6 ...}
            Args:
                * callback_should_save:
                    Args:
                        from_surface, to_surface
                    Returns:
                        bool
                * callback_select_surface:
                    select from or to surface
        """

        cursor: Cursor = self.retrieve_mongo.collection.find(
            {} if optional_query is None else optional_query,
            no_cursor_timeout=True
        )
        total: int = cursor.count()

        save_words: Dict[str, int] = {}

        for document in tqdm(cursor, total=total):

            target_text: str = callback_retrieve(document)

            if target_text is None:
                continue

            tree: Tree = self.cabocha.parse(target_text)
            chunks: Dict[int, Any] = self.generate_chunks(tree)

            for from_chunk in chunks.values():
                if from_chunk.link < 0:
                    continue

                from_surface: str = self.get_surface(tree, from_chunk)
                to_chunk: Chunk = chunks[from_chunk.link]
                to_surface: str = self.get_surface(tree, to_chunk)

                if callback_should_save(from_surface, to_surface):
                    for one_line_morpheme in self.mecab.parse(
                        callback_select_surface(
                            from_surface,
                            to_surface
                        )
                    ).splitlines():
                        morpheme_list: List[str] = (
                            one_line_morpheme.split("\t")
                        )
                        if len(morpheme_list) == EOS_LENGTH:
                            continue
                        self.add_count_by_word_destructively(
                            part_of_speech,
                            morpheme_list,
                            save_words
                        )
            if len(save_words) >= self.LIMIT:
                self.upsert_count_by_key(save_words)
                self.logger.info(
                    self.create_logger_message(
                        len(save_words),
                        document["_id"]
                    )
                )
                save_words = {}

        if len(save_words) > 0:
            self.upsert_count_by_key(save_words)
            self.logger.info(
                self.create_logger_message(
                    len(save_words),
                    document["_id"]
                )
            )

        cursor.close()

    def add_count_by_word_destructively(
        self,
        part_of_speech: str,
        morpheme_list: List[str],
        save_words: Dict[str, int]
    ) -> None:
        """
        Comment:
            * attention: destructively dectionary operations
            * save_words is changed destructively
        """
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
            self.logger.debug("error list: {}".format(morpheme_list))
