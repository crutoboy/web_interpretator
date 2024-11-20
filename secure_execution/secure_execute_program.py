import os
import subprocess
from uuid import uuid4

from . import programing_languages
from .config import DEFAULT_CPU, DEFAULT_MEMORY, DEFAULT_TIMEOUT, WORKSPACE

def start_program(program: str, stdin: str = '', language: str = 'python', \
    cpu: float = DEFAULT_CPU, memory: int = DEFAULT_MEMORY, timeout: float = DEFAULT_TIMEOUT) -> tuple[str, str, str]:
    """
    Выполняет программы на различных языках программирования в изолированном окружении.

    Параметры:
    - program (str): Код программы.
    - stdin (str): Входные данные.
    - language (str): Язык программирования (поддерживается: 'python', 'cpp', 'c', 'java', 'js').
    - cpu (float): Ограничение на использование процессора.
    - memory (int): Ограничение на использование памяти в мегабайтах.
    - timeout (float): Лимит времени выполнения.

    Возвращает:
    tuple[str, str, str]: Кортеж (stdout, stderr, status_code), где:
                          - stdout (str): Стандартный вывод программы.
                          - stderr (str): Сообщения об ошибках выполнения.
                          - status_code (str): Код статуса выполнения ('ne' для успешного выполнения, 're' для ошибки выполнения, 'ce' для ошибки компиляции, None для неподдерживаемого языка).
    """
    if language == 'python':
        stdout, stderr, status_code = programing_languages.python_exec.execute_python_program(program, stdin, cpu, memory, timeout)
        return (stdout, stderr, status_code)
    elif language == 'cpp':
        stdout, stderr, status_code = programing_languages.cpp_exec.execute_cpp_program(program, stdin, cpu, memory, timeout)
        return (stdout, stderr, status_code)
    elif language == 'java':
        stdout, stderr, status_code = programing_languages.java_exec.execute_java_program(program, stdin, cpu, memory, timeout)
        return (stdout, stderr, status_code)
    elif language == 'c':
        stdout, stderr, status_code = programing_languages.c_exec.execute_c_program(program, stdin, cpu, memory, timeout)
        return (stdout, stderr, status_code)
    elif language == 'js':
        stdout, stderr, status_code = programing_languages.js_exec.execute_js_program(program, stdin, cpu, memory, timeout)
        return (stdout, stderr, status_code)
    else:
        return ('', 'Error: language not supported', None)
