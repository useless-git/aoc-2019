def mass2fuel(mass):
    return (mass // 3) - 2

import sys
print sum((mass2fuel(int(line)) for line in sys.stdin))
