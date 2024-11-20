import secure_execute_program
from config import DEFAULT_CPU, DEFAULT_MEMORY, DEFAULT_TIMEOUT

def test_program(program: str, data_for_check: list[list[str]], language: str, \
    cpu:float=DEFAULT_CPU, memory:int=DEFAULT_MEMORY, timeout:float=DEFAULT_TIMEOUT) -> tuple[tuple[str, str, str, str]]:
    """
    Тестирует выполнение передаваемой программы с проверкой её вывода для определённого ввода.

    Параметры:
    - program (str): Исходный код программы, который нужно протестировать.
    - data_for_check (list[list[str]]): Двумерный список пар [stdin, stdout], где:
      - stdin (str) — входные данные, подаваемые в программу.
      - stdout (str) — ожидаемый вывод программы для этих входных данных.
    - language (str): Язык программирования, на котором написан код.
      Возможные значения: см. secure_execute_program.start_program()
    - cpu (float): Ограничение на использование процессора в Docker-контейнере.
    - memory (int): Ограничение на использование ОЗУ в Docker-контейнере в мегабайтах.
    - timeout (float): Лимит времени выполнения программы в секундах.

    Возвращаемое значение:
    - tuple[tuple[str, str, str, str]]: Кортеж результатов, содержащий для каждого теста:
      - stdin (str): Входные данные.
      - actual_stdout (str): Фактический вывод программы.
      - expected_stdout (str): Ожидаемый вывод.
      - stderr (str): Данные об ошибках.
      - status_code (str): Статус код о проведённом тесте.
    """

    res_of_check = list()
    for stdin, expected_stdout in data_for_check:
        stdout, stderr = secure_execute_program.start_program(program, stdin, language, cpu, memory, timeout)
        is_correct = stdout.strip() == expected_stdout.strip()
        res_of_check.append([
            stdin, stdout, expected_stdout, stderr, is_correct
        ])
        print(stdin, stdout)
    print(res_of_check)

prog = """
n = int(input())
print(1/n)"""

data = [
    ['5', '0.2'], 
    ['10', '0.1'], 
    ['-50', '-0.02'], 
    ['0', '0']
]

test_program(prog, data, 'python')


# start_program(program: str, stdin: str = '', language: str = 'python', \
#     cpu=DEFAULT_CPU, memory=DEFAULT_MEMORY, timeout=DEFAULT_TIMEOUT)