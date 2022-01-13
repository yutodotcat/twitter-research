from src.core.loader import AnalysisConfigLoader, ConfigLoader


def test_config_loader():
    # python path is /worker/
    assert "/worker/" == ConfigLoader.get_app_root_directory()
    # config file path
    assert ConfigLoader.get_config_file_path() == (
        "/worker/src/"
        "config/config.json"
    )


def test_analysis_config_loader():
    # get config keys
    assert set(AnalysisConfigLoader.get_mongo_config_keys()) == set(
        [
            "auth",
            "database_name",
            "collection_name",
            "host",
            "port",
            "username",
            "password",
            "authSource",
            "authMechanism"
        ]
    )
