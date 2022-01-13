import CaboCha
import MeCab
from src.core.loader import AnalysisConfigLoader


class TextAnalyzeService:

    @classmethod
    def get_wakati_mecab_instance(cls) -> MeCab.Tagger:
        dict_dir: str = cls.get_dict_dir()
        return MeCab.Tagger(
            "-O wakati -d {}".format(dict_dir)
        ) if dict_dir else MeCab.Tagger()

    @classmethod
    def get_mecab_instance(cls) -> MeCab.Tagger:
        dict_dir: str = cls.get_dict_dir()
        return MeCab.Tagger(
            "-d {}".format(dict_dir)
        ) if dict_dir else MeCab.Tagger()

    @classmethod
    def get_cabocha_instance(cls) -> CaboCha.Parser:
        dict_dir: str = cls.get_dict_dir()
        return CaboCha.Parser(
            "-d {}".format(dict_dir)
        ) if dict_dir else CaboCha.Parser("")

    @classmethod
    def get_dict_dir(cls) -> str:
        return AnalysisConfigLoader.get_nlp_dict_path()
