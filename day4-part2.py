"""
--- Day 4: Secure Container ---

You arrive at the Venus fuel depot only to discover it's protected by a password. The Elves had written the password on a sticky note, but someone threw it out.

However, they do remember a few key facts about the password:

    It is a six-digit number.
    The value is within the range given in your puzzle input.
    Two adjacent digits are the same (like 22 in 122345).
    Going from left to right, the digits never decrease; they only ever increase or stay the same (like 111123 or 135679).

Other than the range rule, the following are true:

    111111 meets these criteria (double 11, never decreases).
    223450 does not meet these criteria (decreasing pair of digits 50).
    123789 does not meet these criteria (no double).

How many different passwords within the range given in your puzzle input meet these criteria?

Your puzzle input is 271973-785961.

--- Part Two ---

An Elf just remembered one more important detail: the two adjacent matching digits are not part of a larger group of matching digits.

Given this additional criterion, but still ignoring the range rule, the following are now true:

    112233 meets these criteria because the digits never decrease and all repeated digits are exactly two digits long.
    123444 no longer meets the criteria (the repeated 44 is part of a larger group of 444).
    111122 meets the criteria (even though 1 is repeated more than twice, it still contains a double 22).

How many different passwords within the range given in your puzzle input meet all of the criteria?
"""

def digits(numstr):
    """easier to work with [1,2,3] than "123" or 123
    
    >>> digits("")
    []
    
    >>> digits("271973")
    [2, 7, 1, 9, 7, 3]
    """
    return [int(d) for d in numstr.strip()]

def nondecreasing(dig):
    """return true if the nondecreasing predicate holds
    
    >>> nondecreasing([2,7,1,9,7,3])
    False
    
    >>> nondecreasing([2,3,4,5,5,7])
    True
    """
    return all((a<=b for a,b in zip(dig[:-1],dig[1:])))

def makeNondecreasing(dig):
    """skip ahead to the first non-decreasing value.

    >>> makeNondecreasing([2,7,1,9,7,3])
    [2, 7, 7, 7, 7, 7]

    >>> makeNondecreasing([2,3,4,5,5,7])
    [2, 3, 4, 5, 5, 7]
    """
    if nondecreasing(dig):
        return dig
    out = dig[:]
    for i in range(1, len(out)):
        if out[i] < out[i-1]:
            out[i] = out[i-1]
            return out[:i] + [out[i-1]] * (len(out)-i)
    return None

def nextNondecreasing(dig):
    """smallest increment to a valid non-decreasing number

    >>> nextNondecreasing([2, 7, 7, 0, 0, 0])
    [2, 7, 7, 0, 0, 1]

    >>> nextNondecreasing([2, 7, 7, 0, 0, 9])
    [2, 7, 7, 0, 1, 1]

    >>> nextNondecreasing([2, 3, 4, 5, 5, 7])
    [2, 3, 4, 5, 5, 8]

    >>> nextNondecreasing([2, 9, 9, 9, 9, 9])
    [3, 3, 3, 3, 3, 3]
    """
    # special case the last digit which can't break the nondecreasing property
    if dig[-1] < 9:
        return dig[:-1] + [dig[-1]+1]

    for i in reversed(range(len(dig)-1)):
        if dig[i] < 9:
            return dig[:i] + [dig[i]+1] * (len(dig)-i)

def adjacent(dig):
    """the new adjacency predicate is that there must be at least one group with exactly two repetitions

    >>> adjacent([1,2,3,4,4,4])
    False
    
    >>> adjacent([1,1,1,1,2,2])
    True
    """
    def rle(seq):
        cval = seq[0]
        cnum = 1
        for elem in seq[1:]:
            if elem == cval:
                cnum += 1
            else:
                if cnum > 1:
                    yield (cval, cnum)
                cval = elem
                cnum = 1
        # final run
        if cnum > 1:
            yield (cval, cnum)

    return any((num==2 for val,num in rle(dig)))

def compare(ad, bd):
    """compare two numbers in digit-sequence form.
    ad <  bd => -1
    ad == bd =>  0
    ad  > bd => +1

    >>> compare([2,7,1,9,7,3],[2,7,1,9,7,3])
    0
    
    >>> compare([7,8,5,9,6,1],[2,7,1,9,7,3])
    1
    
    >>> compare([2,7,1,9,7,3],[7,8,5,9,6,1])
    -1
    """
    for a,b in zip(ad,bd):
        if a < b:
            return -1
        if a > b:
            return 1
    return 0

def generatePasswords(begin, end):
    cur = makeNondecreasing(begin);
    while compare(cur, end) <= 0:
        if adjacent(cur):
            yield cur
        cur = nextNondecreasing(cur)

def countPasswords(beginstr, endstr):
    begin = digits(beginstr)
    end = digits(endstr)
    count = 0
    for pw in generatePasswords(begin, end):
        count += 1
        print(pw)
    return count

import sys

if len(sys.argv) > 1 and sys.argv[1] == '--test':
    import doctest
    doctest.testmod()
    sys.exit(0)

print countPasswords("271973","785961")

