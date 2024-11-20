import shutil
import os
from functools import lru_cache
from uuid import uuid4

from .config import WORKSPACE

@lru_cache(256)
def get_path_to_workspace(id_workspace: str) -> str:
    """
    Возвращает путь к рабочему пространству по его ID.

    Параметры:
    - id_workspace (str): ID рабочего пространства.

    Возвращает:
    str: Путь к рабочему пространству.

    Исключения:
    - Exception: Если ID содержит недопустимые символы, такие как '/'.
    """
    if '/' in id_workspace or '\\' in id_workspace:
        raise Exception('Security error: invalid character in id_workspace')
    path_to_workspace = os.path.join(WORKSPACE, id_workspace)
    return path_to_workspace

def create_workspace() -> str:
    """
    Создаёт рабочее пространство и возвращает его ID.

    Возвращает:
    str: ID созданного рабочего пространства.
    """
    id_workspace = str(uuid4())
    path_to_workspace = get_path_to_workspace(id_workspace)
    os.makedirs(path_to_workspace, exist_ok=True)  # Создание каталога с проверкой существования
    return id_workspace

def del_workspace(id_workspace: str) -> bool:
    """
    Удаляет рабочее пространство по его ID.

    Параметры:
    - id_workspace (str): ID рабочего пространства.

    Возвращает:
    bool: True, если рабочее пространство было удалено, False, если его не существовало.
    """
    path_to_workspace = get_path_to_workspace(id_workspace)
    if not os.path.isdir(path_to_workspace):
        return None
    shutil.rmtree(path_to_workspace)
