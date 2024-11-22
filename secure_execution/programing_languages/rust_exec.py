import subprocess
import os

from .. import workspace_tool
from ..config import DEFAULT_CPU, DEFAULT_MEMORY, DEFAULT_TIMEOUT


RUST_FILENAME = 'source.rs'
COMPILE_FILE = 'compile_rust_program'

def create_rust_file(path_to_workspace, program):
    """
    Создаёт Java файл с кодом программы в указанной директории рабочего пространства.

    Параметры:
    - path_to_workspace (str): Путь к рабочему пространству.
    - program (str): Код программы на Java, который нужно записать в файл.
    """
    with open(os.path.join(path_to_workspace, RUST_FILENAME), 'w') as file:
        file.write(program)

def compile_rust_program(workspace_id: str, \
    cpu: float = DEFAULT_CPU, memory: int = DEFAULT_MEMORY, timeout: float = DEFAULT_TIMEOUT) -> tuple[str, str, str]:
    """компиляция rust программы"""
    path_to_workspace = workspace_tool.get_path_to_workspace(workspace_id)

    cmd = [
        'docker', 'run', '-i',
        f'--cpus={cpu}',
        f'--memory={memory}m',
        '--network=none',
        '-v', f'{path_to_workspace}:/usr/src/app',
        'rust:latest',
        'rustc', f'/usr/src/app/{RUST_FILENAME}', '-o', f'/usr/src/app/{COMPILE_FILE}'
    ]
    try:
        proc = subprocess.run(cmd, text=True, timeout=timeout, capture_output=True)
    except subprocess.TimeoutExpired:
        return ('', f'compile error:\ntimeout error ({timeout}s)', 'ce')
    return (proc.stdout, proc.stderr, proc.returncode)

def run_rust_program(workspace_id: str, stdin: str, \
    cpu: float = DEFAULT_CPU, memory: int = DEFAULT_MEMORY, timeout: float = DEFAULT_TIMEOUT) -> tuple[str, str, str]:
    """запуск rust программы"""
    path_to_workspace = workspace_tool.get_path_to_workspace(workspace_id)

    cmd = [
        'docker', 'run', '--rm', '-i',
        f'--cpus={cpu}',
        f'--memory={memory}m',
        '--network=none',
        '--read-only',
        '-v', f'{path_to_workspace}:/usr/src/app',
        'rust:latest', f'/usr/src/app/{COMPILE_FILE}'
    ]
    try:
        proc = subprocess.run(cmd, input=stdin, text=True, timeout=timeout, capture_output=True)
    except subprocess.TimeoutExpired:
        return ('', f'runtime error:\ntimeout error ({timeout}s)', 're')
    return (proc.stdout, proc.stderr, proc.returncode)

def execute_rust_program(program: str, stdin: str, \
    cpu: float = DEFAULT_CPU, memory: int = DEFAULT_MEMORY, timeout: float = DEFAULT_TIMEOUT) -> tuple[str, str, str]:
    """
    Выполняет Java программу в изолированном Docker контейнере с заданными ограничениями по ресурсам.

    Параметры:
    - program (str): Код программы на Java, который нужно выполнить.
    - stdin (str): Входные данные, подаваемые на стандартный ввод программы.
    - cpu (float): Ограничение на использование процессора (в долях CPU).
    - memory (int): Ограничение на использование памяти в мегабайтах.
    - timeout (float): Максимальное время выполнения программы в секундах.

    Возвращает:
    tuple[str, str, str]: Кортеж, содержащий:
                          - stdout (str): Стандартный вывод программы.
                          - stderr (str): Сообщения об ошибках выполнения программы.
                          - status (str): Статус выполнения программы:
                                          - 'ne' (normal execution) при успешном завершении.
                                          - 're' (runtime error) при ошибке выполнения.
                                          - 'ce' (compilation error) при ошибке компиляции.
    """
    workspace_id = workspace_tool.create_workspace()  # Создание уникального рабочего пространства для временных файлов.
    path_to_workspace = workspace_tool.get_path_to_workspace(workspace_id)

    create_rust_file(path_to_workspace, program)  # Запись программы в файл.

    compile_stdout, compile_stderr, compile_returncode = compile_rust_program(workspace_id, cpu, memory, timeout)
    if compile_returncode != 0:
        workspace_tool.del_workspace(workspace_id)  # Удаление рабочего пространства при ошибке компиляции
        return (compile_stdout, compile_stderr, 'ce')

    exec_stdout, exec_stderr, exec_returncode = run_rust_program(workspace_id, stdin, cpu, memory, timeout)

    workspace_tool.del_workspace(workspace_id)  # Удаление рабочего пространства после выполнения программы

    if exec_returncode != 0:
        return (exec_stdout, exec_stderr, 're')
    return (exec_stdout, exec_stderr, 'ne')
