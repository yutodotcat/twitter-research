from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from pymongo import UpdateOne
from pymongo.cursor import Cursor
from src.annotation.type import OptionalQuery, RetrieveCallback
from src.core.mongo_connection import MongoConnection
from src.util.logger import LoggerFactory
from tqdm import tqdm
from typing_extensions import Final


class TweetAnalysisCore:

    logger = LoggerFactory.create_save_info_or_more()

    def __init__(
        self,
        retrieve_collection_name: str = "",
        save_collection_name: Optional[str] = None,
        **options: bool,
    ) -> None:
        """
        Comments:
            * prepare instance for analysis
            * validation runs here
        Args:
            * **opttions: Literal[
                "is_config_mongo_only",
                "is_same_collection_accepted"
                ]
        """
        IS_CONFIG_MONGO_ONLY: Final[str] = "is_config_mongo_only"
        IS_SAME_COLLECTION_ACCEPTED: Final[str] = "is_same_collection_accepted"

        if IS_CONFIG_MONGO_ONLY in options:
            # retrieve and save mongo are based on config mongo
            self.retrieve_mongo = MongoConnection.create_instance_from_config()
            self.save_mongo = MongoConnection.create_instance_from_config()
        elif IS_SAME_COLLECTION_ACCEPTED in options:
            # retrieve and save mongo are same collection
            self.retrieve_mongo, self.save_mongo = (
                MongoConnection.create_two_instance_for_analysis(
                    retrieve_collection_name,
                    save_collection_name
                )
            )
        else:
            # retrieve mongo and save mongo are different
            # and two instances are not config mongo
            if retrieve_collection_name == save_collection_name:
                raise ValueError(
                    "retrieve and save collection must be different"
                )
            self.retrieve_mongo, self.save_mongo = (
                MongoConnection.create_two_instance_for_analysis(
                    retrieve_collection_name,
                    save_collection_name
                )
            )

    def check_and_create_single_index(
        self,
        field_name: str,
        **options: bool
    ) -> None:
        """
        Args:
            * field_name:
                * target field is checked and create index
            * **options:
                * optional variable
                * Dict[Literal["save", "retrieve"],bool]
        Comments:
            * retrieve_mongo is necessary(not None)
            * save_mongo is optional(may be None)
            * filed_name is like "location_name" or "tweet_data.source"
            * 1 or -1 prefix is not required
            * **options: bool is workaround
        """
        is_retrieve_required: bool = True
        is_save_required: bool = True

        if "retrieve" in options:
            is_retrieve_required = options["retrieve"]
        if "save" in options:
            is_save_required = options["save"]

        index_information: Dict[str, Any] = {}

        index_name_with_one: str = field_name + "_1"
        index_name_with_minus_one: str = field_name + "_-1"

        index_information = self.retrieve_mongo.collection.index_information()
        if (index_name_with_one in index_information or
                index_name_with_minus_one in index_information):
            self.logger.info(
                "target: {} index in {} has already been created".format(
                    field_name,
                    self.retrieve_mongo.collection.name
                )
            )
        else:
            if is_retrieve_required:
                self.retrieve_mongo.collection.create_index([(field_name, 1)])
                self.logger.info((
                    "Creating {} index in {} "
                    "has been completed successufully"
                ).format(field_name, self.retrieve_mongo.collection.name))

        if not(self.save_mongo is None):
            index_information = self.save_mongo.collection.index_information()
            if (index_name_with_one in index_information or
                    index_name_with_minus_one in index_information):
                self.logger.info(
                    "target: {} index in {} has already been created".format(
                        field_name,
                        self.save_mongo.collection.name
                    )
                )
            else:
                if is_save_required:
                    self.save_mongo.collection.create_index([(field_name, 1)])
                    self.logger.info(
                        (
                            "Creating {} index in {} "
                            "has been completed successufully"
                        ).format(
                            field_name,
                            self.save_mongo.collection.name
                        )
                    )

    def retrieve_and_save(
        self,
        update_callback: RetrieveCallback,
        optional_query: OptionalQuery = None,
        callback_skip_loop: Optional[Callable[[Any], bool]] = None,
    ) -> None:
        """
        Comments:
            * depends on update_callback and optional_query
        """
        LIMIT: Final[int] = 50000
        bulk_op_documents: List[Dict[str, str]] = []

        cursor: Cursor
        total_count: int

        cursor, total_count = self.get_cursor_and_count_from_retrieve(
            optional_query
        )

        for document in tqdm(cursor, total=total_count):
            if not (callback_skip_loop is None) and callback_skip_loop(
                document
            ):
                continue
            bulk_op_documents.append(
                update_callback(document)
            )
            if len(bulk_op_documents) == LIMIT:
                self.save_mongo.collection.bulk_write(
                    bulk_op_documents
                )
                bulk_op_documents = []
                self.logger.info(
                    self.create_logger_message(
                        LIMIT,
                        document["_id"]
                    )
                )
        if len(bulk_op_documents) > 0:
            self.save_mongo.collection.bulk_write(
                bulk_op_documents
            )
            self.logger.info(
                self.create_logger_message(
                    len(bulk_op_documents),
                    document["_id"]
                )
            )

    def upsert_count_by_key(
        self,
        upsert_data: Dict[str, int],
        save_key_name: str = "word"
    ) -> None:
        """
        Comment:
            * to be used when text analysis
            * update count and insert document not to be saved
            * collection: {"key": count}, {"key", count} (ordered)
        Args:
            upsert_data: {"some": 5, "bla": 150 , ...}
                * will be upserted
        """
        KEY_NAME: Final[str] = save_key_name

        bulk_op_save_list: List[UpdateOne] = []
        keys_upsert_data: List[str] = list(upsert_data.keys())
        self.check_and_create_single_index(KEY_NAME, save=True, retrieve=False)

        # [{"_id": "", "bla": "bla", "count": 1}, ...]
        already_saved_data: List[Dict[str, Union[int, str]]] = list(
            self.save_mongo.collection.find(
                {
                    KEY_NAME: {"$in": keys_upsert_data}
                }
            )
        )

        for key_count_dict in already_saved_data:
            # count_by_key: {"_id": "bla", "KEY_NAME: "bla", "count": <number>}
            key_name: str = str(key_count_dict[KEY_NAME])
            key_count_dict["count"] = int(
                key_count_dict["count"]
            ) + upsert_data[key_name]

            bulk_op_save_list.append(
                UpdateOne(
                    {KEY_NAME: key_name},
                    {"$set": {
                        KEY_NAME: key_name,
                        "count": key_count_dict["count"]
                    }}
                )
            )
            del upsert_data[key_name]

        insert_data: List[Dict[str, Union[int, str]]] = [
            {KEY_NAME: key, "count": count}
            for key, count in upsert_data.items()
        ]

        if bulk_op_save_list:
            self.save_mongo.collection.bulk_write(bulk_op_save_list)
        if insert_data:
            self.save_mongo.collection.insert_many(insert_data)

        self.logger.info(
            "bulk upsert operations have been completed successfully"
        )

    def display_all(
        self,
        retrieve_callback: RetrieveCallback,
        optional_query: Optional[Dict[str, Any]],
        max_loop: Optional[int]
    ) -> None:
        """
        Comments:
            * show documents for test
            * for example investigate whether emoji compile works or not
        """
        cursor: Cursor = self.retrieve_mongo.collection.find(
            {} if optional_query is None else optional_query
        )
        total_count: int = cursor.count()

        if max_loop is None:
            max_loop = total_count

        for loop, document in enumerate(tqdm(cursor, total=total_count)):
            self.logger.debug(
                retrieve_callback(document)
            )
            if max_loop == loop:
                self.logger.info("loop achieves max_loop")
                break

    def get_cursor_from_retrieve(
        self,
        optional_query: Optional[Dict[str, Any]] = None
    ) -> Cursor:
        cursor: Cursor = self.retrieve_mongo.collection.find(
            {} if optional_query is None else
            optional_query
        )
        return cursor

    def get_cursor_and_count_from_retrieve(
        self,
        optional_query: Optional[Dict[str, Any]] = None
    ) -> Tuple[Cursor, int]:
        cursor: Cursor = self.get_cursor_from_retrieve(optional_query)
        return (cursor, cursor.count())

    def get_cursor_count(
        self,
        optional_query: Optional[Dict[str, Any]] = None
    ) -> int:
        cursor: Cursor = self.get_cursor_from_retrieve(optional_query)
        return cursor.count()

    def create_logger_message(
        self,
        saved_count: int,
        last_id: str
    ) -> str:
        default_message: str = (
            "operations {}"
            " have been performed"
        )
        return "{} {} by {}".format(
            saved_count,
            default_message,
            last_id
        )

    @classmethod
    def require_save_mongo(cls, f):
        def wrapper(*args):
            if args[0].save_mongo is None:
                raise Exception("please select save mongo")
            return f(*args)
        return wrapper

    @classmethod
    def unrequired_save_mongo(cls, f):
        def wrapper(*args):
            if not(args[0].save_mongo is None):
                raise Exception("save mongo is unrequired")
            return f(*args)
        return wrapper
