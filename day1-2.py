def mass2fuel(mass):
    def fuel(m):
        return (m // 3) - 2

    def fuelmass(m):
        f = fuel(m)
        while f > 0:
            yield f
            f = fuel(f)

    return sum(fuelmass(mass))

import sys
print sum((mass2fuel(int(line)) for line in sys.stdin))
