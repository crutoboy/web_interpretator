import subprocess

from ..config import DEFAULT_CPU, DEFAULT_MEMORY, DEFAULT_TIMEOUT

def execute_js_program(program: str, stdin: str, \
    cpu: float = DEFAULT_CPU, memory: int = DEFAULT_MEMORY, timeout: float = DEFAULT_TIMEOUT) -> tuple[str, str, str]:
    """
    Выполняет JavaScript скрипт в изолированном Docker-контейнере с ограничениями.

    Параметры:
    - program (str): Код программы на JavaScript.
    - stdin (str): Входные данные, подаваемые программе.
    - cpu (float): Ограничение на использование процессора в контейнере.
    - memory (int): Ограничение на использование памяти в контейнере в мегабайтах.
    - timeout (float): Лимит времени выполнения программы в секундах.

    Возвращает:
    tuple[str, str, str]: Кортеж (stdout, stderr, status), где:
                          - stdout (str): Стандартный вывод программы.
                          - stderr (str): Сообщения об ошибках выполнения.
                          - status (str): Статус выполнения ('re' при ошибке выполнения, 'ne' при успешном выполнении).
    """
    cmd = [
        'docker', 'run', '--rm', '-i',
        f'--cpus={cpu}',
        f'--memory={memory}m',
        '--network=none',
        '--read-only',
        'node:16-slim',
        'node', '-e', program
    ]
    try:
        proc = subprocess.run(cmd, input=stdin, text=True, timeout=timeout, capture_output=True)
    except subprocess.TimeoutExpired:
        return ('', f'execution error:\ntimeout error ({timeout}s)', 're')

    if proc.returncode != 0:
        return (proc.stdout, proc.stderr, 're')
    
    return (proc.stdout, proc.stderr, 'ne')
