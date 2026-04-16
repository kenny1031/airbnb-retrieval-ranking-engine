from pathlib import Path
import yaml


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "retrieval_ranking.yaml"
_config_cache = None


def load_config() -> dict:
    global _config_cache
    if _config_cache is None:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            _config_cache = yaml.safe_load(f)
    return _config_cache


def get_embedding_config() -> dict:
    return load_config()["embedding"]


def get_xgboost_config() -> dict:
    return load_config()["xgboost"]


def get_ranking_config() -> dict:
    return load_config()["ranking"]


def get_training_data_config() -> dict:
    return load_config()["training_data"]