import subprocess
import os

from .. import workspace_tool
from ..config import DEFAULT_CPU, DEFAULT_MEMORY, DEFAULT_TIMEOUT


JAVA_FILENAME = 'source.java'

def create_java_file(path_to_workspace, program):
    """
    Создаёт Java файл с кодом программы в указанной директории рабочего пространства.

    Параметры:
    - path_to_workspace (str): Путь к рабочему пространству.
    - program (str): Код программы на Java, который нужно записать в файл.
    """
    with open(os.path.join(path_to_workspace, JAVA_FILENAME), 'w') as file:
        file.write(program)

def execute_java_program(program: str, stdin: str, \
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
    create_java_file(path_to_workspace, program)  # Запись программы в файл.

    # Сборка команды для запуска Java программы в Docker контейнере с ограничениями по ресурсам.
    cmd = [
        'docker', 'run', '--rm', '-i',
        f'--cpus={cpu}',  # Ограничение на количество процессоров.
        f'--memory={memory}m',  # Ограничение на использование памяти (в мегабайтах).
        '--network=none',  # Отключение сетевого доступа.
        '--read-only',  # Запуск в режиме только для чтения (для безопасности).
        '-v', f'{path_to_workspace}:/usr/src/app',  # Монтирование рабочего пространства в контейнер.
        'openjdk:17-jdk-slim',  # Использование образа OpenJDK 17.
        'java', f'/usr/src/app/{JAVA_FILENAME}'  # Выполнение Java программы.
    ]
    
    try:
        # Запуск контейнера с программой, передача входных данных через stdin.
        proc = subprocess.run(cmd, input=stdin, text=True, timeout=timeout, capture_output=True)
    except subprocess.TimeoutExpired:
        # Обработка таймаута выполнения программы.
        return ('', f'Execution error: Timeout exceeded ({timeout}s)', 're')

    # Проверка на ошибки выполнения или компиляции.
    if proc.returncode != 0:
        # Ошибка компиляции или выполнения программы.
        return (proc.stdout, proc.stderr, 'ce')
    
    # Возврат результатов выполнения программы (stdout, stderr) и статуса.
    return (proc.stdout, proc.stderr, 'ne')
