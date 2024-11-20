import subprocess

from .. import workspace_tool
from ..config import DEFAULT_CPU, DEFAULT_MEMORY, DEFAULT_TIMEOUT

COMPILING_FILE_NAME = 'compile_c_program'

def compile_c_program(program: str, workspace_id: str, \
    cpu: float = DEFAULT_CPU, memory: int = DEFAULT_MEMORY, timeout: float = DEFAULT_TIMEOUT) -> tuple[str, str, str]:
    """
    Компилирует C программу и возвращает ID программы и информацию об ошибках.

    Параметры:
    - program (str): Код программы на C.
    - workspace_id (str): ID рабочего пространства, где будет происходить компиляция.
    - cpu (float): Ограничение на использование процессора.
    - memory (int): Ограничение на использование памяти в мегабайтах.
    - timeout (float): Лимит времени компиляции в секундах.

    Возвращает:
    tuple[str, str, str]: Кортеж (stdout, stderr, returncode), где:
                          - stdout (str): Стандартный вывод процесса компиляции.
                          - stderr (str): Сообщения об ошибках компиляции.
                          - returncode (str): Код возврата процесса.
    """
    path_to_workspace = workspace_tool.get_path_to_workspace(workspace_id)

    cmd = [
        'docker', 'run', '-i',
        f'--cpus={cpu}',
        f'--memory={memory}m',
        '--network=none',
        '-v', f'{path_to_workspace}:/usr/src/app',
        'gcc:latest',
        "gcc", "-x", "c", "-", "-o", f'/usr/src/app/{COMPILING_FILE_NAME}'
    ]
    try:
        proc = subprocess.run(cmd, input=program, text=True, timeout=timeout, capture_output=True)
    except subprocess.TimeoutExpired:
        return ('', f'compile error:\ntimeout error ({timeout}s)', 'ce')
    return (proc.stdout, proc.stderr, proc.returncode)

def run_c_program(workspace_id: str, stdin: str, \
    cpu: float = DEFAULT_CPU, memory: int = DEFAULT_MEMORY, timeout: float = DEFAULT_TIMEOUT) -> tuple[str, str, str]:
    """
    Запускает скомпилированную C программу и возвращает результат выполнения.

    Параметры:
    - workspace_id (str): ID рабочего пространства, где хранится скомпилированная программа.
    - stdin (str): Входные данные для программы.
    - cpu (float): Ограничение на использование процессора.
    - memory (int): Ограничение на использование памяти в мегабайтах.
    - timeout (float): Лимит времени выполнения в секундах.

    Возвращает:
    tuple[str, str, str]: Кортеж (stdout, stderr, returncode), где:
                          - stdout (str): Стандартный вывод программы.
                          - stderr (str): Сообщения об ошибках выполнения.
                          - returncode (str): Код возврата процесса.
    """
    path_to_workspace = workspace_tool.get_path_to_workspace(workspace_id)

    cmd = [
        'docker', 'run', '--rm', '-i',
        f'--cpus={cpu}',
        f'--memory={memory}m',
        '--network=none',
        '--read-only',
        '-v', f'{path_to_workspace}:/usr/src/app',
        'gcc:latest', f'/usr/src/app/{COMPILING_FILE_NAME}'
    ]
    try:
        proc = subprocess.run(cmd, input=stdin, text=True, timeout=timeout, capture_output=True)
    except subprocess.TimeoutExpired:
        return ('', f'runtime error:\ntimeout error ({timeout}s)', 're')
    return (proc.stdout, proc.stderr, proc.returncode)

def execute_c_program(program: str, stdin: str, \
    cpu: float = DEFAULT_CPU, memory: int = DEFAULT_MEMORY, timeout: float = DEFAULT_TIMEOUT) -> tuple[str, str, str]:
    """
    Компилирует и выполняет C программу, возвращает результат выполнения.

    Параметры:
    - program (str): Код программы на C.
    - stdin (str): Входные данные для программы.
    - cpu (float): Ограничение на использование процессора.
    - memory (int): Ограничение на использование памяти в мегабайтах.
    - timeout (float): Лимит времени выполнения в секундах.

    Возвращает:
    tuple[str, str, str]: Кортеж (stdout, stderr, status), где:
                          - stdout (str): Стандартный вывод выполнения программы.
                          - stderr (str): Сообщения об ошибках выполнения или компиляции.
                          - status (str): Статус выполнения ('ce' для ошибок компиляции,
                                          're' для ошибок выполнения, 'ne' при успешном выполнении).
    """
    id_workspace = workspace_tool.create_workspace()  # Создание рабочего пространства для временных файлов

    compile_stdout, compile_stderr, compile_returncode = compile_c_program(program, id_workspace, cpu, memory, timeout)
    if compile_returncode != 0:
        workspace_tool.del_workspace(id_workspace)  # Удаление рабочего пространства при ошибке компиляции
        return (compile_stdout, compile_stderr, 'ce')

    exec_stdout, exec_stderr, exec_returncode = run_c_program(id_workspace, stdin, cpu, memory, timeout)

    workspace_tool.del_workspace(id_workspace)  # Удаление рабочего пространства после выполнения программы

    if exec_returncode != 0:
        return (exec_stdout, exec_stderr, 're')
    return (exec_stdout, exec_stderr, 'ne')
