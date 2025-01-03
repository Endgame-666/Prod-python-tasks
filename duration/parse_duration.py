def leading_int(s):
    x = 0
    i = 0
    while i < len(s):
        c = s[i]
        if c < '0' or c > '9':
            break
        if x > (1 << 63 - 1) // 10:
            raise ValueError("time: bad [0-9]*")
        x = x * 10 + ord(c) - ord('0')
        if x < 0:
            raise ValueError("time: bad [0-9]*")
        i += 1
    return x, s[i:]


def leading_fraction(s):
    x = 0
    scale = 1.0
    i = 0
    overflow = False
    while i < len(s):
        c = s[i]
        if c < '0' or c > '9':
            break
        if overflow:
            i += 1
            continue
        if x > (1 << 63 - 1) // 10:
            overflow = True
            i += 1
            continue
        y = x * 10 + ord(c) - ord('0')
        if y < 0:
            overflow = True
            i += 1
            continue
        x = y
        scale *= 10
        i += 1
    return x, scale, s[i:]


names = {
    "ns": 1,
    "us": 1000,
    "µs": 1000,
    "μs": 1000,
    "ms": 1000000,
    "s": 1000000000,
    "m": 60000000000,
    "h": 3600000000000,
}


def parse_duration(s):
    orig = s
    d = 0
    neg = False

    if s != '':
        if s[0] == '-' or s[0] == '+':
            neg = s[0] == '-'
            s = s[1:]

    if s == '0':
        return 0
    if s == '':
        raise ValueError("time: invalid duration " + orig)  # 1

    while s != '':
        v = 0
        f = 0
        scale = 1.0

        if not (s[0] == '.' or ('0' <= s[0] <= '9')):
            raise ValueError("time: invalid duration " + orig)  # 2

        pl = len(s)
        try:
            v, s = leading_int(s)
        except ValueError:
            raise ValueError("time: invalid duration " + orig)
        pre = pl != len(s)

        post = False
        if s != '' and s[0] == '.':
            s = s[1:]
            pl = len(s)
            f, scale, s = leading_fraction(s)
            post = pl != len(s)
        if not pre and not post:
            raise ValueError("time: invalid duration " + orig)  # 4

        i = 0
        while i < len(s):
            c = s[i]
            if c == '.' or ('0' <= c <= '9'):
                break
            i += 1
        if i == 0:
            raise ValueError("time: missing unit in duration " + orig)  # 5
        u = s[:i]
        s = s[i:]
        unit = names.get(u)
        if unit is None:
            raise ValueError("time: unknown unit " + u + " in duration " + orig)
        if v > (1 << 63 - 1) // unit:
            raise ValueError("time: invalid duration " + orig)
        v *= unit
        if f > 0:
            v += int(float(f) * (float(unit) / scale))
            if v < 0:
                raise ValueError("time: invalid duration " + orig)
        d += v
        if d < 0:
            raise ValueError("time: invalid duration " + orig)

    if neg:
        d = -d

    return d

