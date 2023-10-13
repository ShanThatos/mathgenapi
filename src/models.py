import datetime
import json
import shutil
from typing import Optional, List

from mathgen import MathProblemModel, MathProblemModelAdapter
from pydantic import TypeAdapter, ValidationError

from . import config, utils


__MODELS: List[MathProblemModel] = []
ModelsTypeAdapter = TypeAdapter(List[MathProblemModel])

class ModelsException(Exception):
    pass

@utils.on_startup()
def load_models():
    global __MODELS
    if not config.MODELS_PATH.exists():
        config.MODELS_PATH.write_text("[]")
    try:
        __MODELS = ModelsTypeAdapter.validate_json(config.MODELS_PATH.read_text())
    except ValidationError as e:
        print(e)

def save_models():
    global __MODELS
    backup_models()
    json.dump(__MODELS, config.MODELS_PATH.open("w"))

def backup_models():
    backup_name = datetime.datetime.now().strftime(r"models-backup-%Y%m%d%H%M%S")
    backup_path = config.get_backups_dir().joinpath(f"./{backup_name}.json")
    backup_id_count = 0
    while backup_path.exists():
        backup_id_count += 1
        backup_path = backup_path.with_name(
            backup_path.name + f" ({backup_id_count})"
        ).with_suffix(".json")
    shutil.copyfile(config.MODELS_PATH, backup_path)
    print(f"Backed up models to: {backup_path}")

def add_model(model: MathProblemModel) -> Optional[str]:
    global __MODELS
    try:
        MathProblemModelAdapter.validate_python(model)
    except ValidationError as e:
        raise ModelsException(f"Invalid model") from e
    if has_model(model.name):
        raise ModelsException(f"Model {model.name} already exists.")
    
    __MODELS.append(model)
    save_models()

def get_model(model_name: str) -> MathProblemModel:
    global __MODELS
    for model in __MODELS:
        if model.name == model_name:
            return model
    raise ModelsException(f"Model {model_name} not found.")

def has_model(model_name: str) -> bool:
    try:
        get_model(model_name)
        return True
    except ModelsException:
        return False