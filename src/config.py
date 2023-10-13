import os
from pathlib import Path

from dotenv import load_dotenv

from . import utils

load_dotenv(verbose=True)

ENVIRONMENT = utils.require_not_none(os.environ.get("ENVIRONMENT"))

API_TOKENS = set(os.environ.get("API_TOKENS", "").split(","))

__WORKING_DIR = Path(utils.require_not_none(os.environ.get("WORKING_DIR")))


def get_working_dir():
    __WORKING_DIR.mkdir(parents=True, exist_ok=True)
    return __WORKING_DIR


MODELS_PATH = get_working_dir().joinpath("models.json")
__MODELS_BACKUPS_PATH = get_working_dir().joinpath("backups")


def get_backups_dir():
    __MODELS_BACKUPS_PATH.mkdir(parents=True, exist_ok=True)
    return __MODELS_BACKUPS_PATH
