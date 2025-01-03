def generate_unique_strings(n: int) -> list[str]:
    import random
    import string
    result = set()
    while len(result) < n:
        length = random.randint(5, 10)
        new_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        result.add(new_string)
    return list(result)