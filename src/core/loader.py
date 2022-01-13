import ast
import json
import os
from typing import Any, Dict, List

from src.annotation.interface import IMongoConfigKeys, ITwitterApiTokens


class Loader:
    """
        * read json file or other files that store static information
    """
    @classmethod
    def load_json(cls, file_path: str) -> Dict[str, Any]:
        with open(file_path, "r") as loaded_json:
            return json.load(loaded_json)


class StaticInfoLoader(Loader):
    pass


class ConfigLoader(Loader):
    """
        * role: access config information of
        * json, enviroment variable and so on
    """

    @classmethod
    def get_app_root_directory(cls) -> str:
        # this includes last slash like /worker/~~/
        return os.environ["PYTHONPATH"]

    @classmethod
    def get_config_file_path(cls) -> str:
        # this is string operation
        # . or ../ can't be used
        return "{}src/config/config.json".format(
            cls.get_app_root_directory()
        )


class CollectionConfigLoader(ConfigLoader):
    @classmethod
    def load_mongo_config(cls) -> IMongoConfigKeys:
        mongo_config: IMongoConfigKeys = cls.load_json(
            cls.get_config_file_path()
        )["collection"]["mongodb"]
        return mongo_config

    @classmethod
    def get_mongo_config_keys(cls) -> List[str]:
        mongo_config: IMongoConfigKeys = cls.load_mongo_config()
        return list(mongo_config.keys())

    @classmethod
    def get_twitter_api_tokens(cls) -> ITwitterApiTokens:
        twitter_api_token: ITwitterApiTokens = ast.literal_eval(
            os.environ["TWITTER_API_TOKEN"]
        )
        return twitter_api_token

    @classmethod
    def get_twitter_api_endpoint(cls) -> str:
        return cls.load_json(
            cls.get_config_file_path()
        )["collection"]["twitter_api"]["endpoint"]

    @classmethod
    def get_twitter_api_request_params(cls) -> str:
        return cls.load_json(
            cls.get_config_file_path()
        )["collection"]["twitter_api"]["request_params"]


class AnalysisConfigLoader(ConfigLoader):

    @classmethod
    def load_mongo_config(cls) -> IMongoConfigKeys:
        mongo_config: Dict[str, str] = cls.load_json(
            cls.get_config_file_path()
        )["analysis"]["mongodb"]
        return mongo_config

    @classmethod
    def get_mongo_config_keys(cls) -> List[str]:
        mongo_config: IMongoConfigKeys = cls.load_mongo_config()
        return list(mongo_config.keys())

    @classmethod
    def get_nlp_dict_path(cls) -> str:
        return cls.load_json(
            cls.get_config_file_path()
        )["analysis"]["mongodb"]["dict_dir"]
