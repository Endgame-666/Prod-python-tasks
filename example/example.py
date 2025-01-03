from typing import List

import random


def generate_unique_numbers(n: int, min_value=1, max_value=10000) -> List[int]:
    if n > (max_value - min_value + 1):
        raise Exception("маленький диапазон!")

    result = set()  # type: ignore
    while len(result) < n:
        result.add(random.randint(min_value, max_value))

    return list(result)
