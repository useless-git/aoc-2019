"""
--- Part Two ---

Once you give them the coordinates, the Elves quickly deploy an Instant Monitoring Station to the location and discover
the worst: there are simply too many asteroids.

The only solution is complete vaporization by giant laser.

Fortunately, in addition to an asteroid scanner, the new monitoring station also comes equipped with a giant rotating
laser perfect for vaporizing asteroids. The laser starts by pointing up and always rotates clockwise, vaporizing any
asteroid it hits.

If multiple asteroids are exactly in line with the station, the laser only has enough power to vaporize one of them
before continuing its rotation. In other words, the same asteroids that can be detected can be vaporized, but if
vaporizing one asteroid makes another one detectable, the newly-detected asteroid won't be vaporized until the laser has
returned to the same position by rotating a full 360 degrees.

...

The Elves are placing bets on which will be the 200th asteroid to be vaporized. Win the bet by determining which
asteroid that will be; what do you get if you multiply its X coordinate by 100 and then add its Y coordinate? (For
example, 8,2 becomes 802.) """
import day10
import io
import itertools
import math

def x(coord):
    return coord[0]
def y(coord):
    return coord[1]
def move(coord, step):
    return tuple(c+s for c,s in zip(coord, step))

### square spirals are easy but tragically wrong ###
def squareSpiral():
    """
    clockwise square spirals follow a fairly easy pattern

    >>> list(itertools.islice(squareSpiral(),0,12))
    [(0, -1), (1, 0), (0, 1), (0, 1), (-1, 0), (-1, 0), (0, -1), (0, -1), (0, -1), (1, 0), (1, 0), (1, 0)]
    """
    up_clockwise_directions = ((0,-1), (1,0), (0, 1), (-1,0))
    di = 0
    for leg_len in itertools.count(1):
        for leg in (1,2):
            for step in range(leg_len):
                yield up_clockwise_directions[di]
            di = (di + 1) % len(up_clockwise_directions)

def squareSpiralFrom(start):
    pos = start
    for step in squareSpiral():
        pos = move(pos, step)
        yield pos

def angle(a, b):
    """
    >>> angle((8,3),(8,1))
    0.0
    >>> angle((8,3),(9,0)) > angle((8,3),(8,1))
    True
    >>> angle((8,3),(9,1)) > angle((8,3),(9,0))
    True
    >>> angle((8,3),(10,0)) > angle((8,3),(9,1))
    True
    >>> angle((8,3),(4,4)) > angle((8,3),(10,0))
    True
    >>> angle((8,3),(4,4)) > angle((8,3),(10,0))
    True
    """
    theta = math.atan2(x(b)-x(a), y(a)-y(b))
    if theta < 0:
        return theta + 2 * math.pi
    return theta

def rotate(seq, pred):
    """Rotate seq so the first element with pred=True is at the front
    (and the skipped elements are appended in-order)

    NB. This requires an actual sequence, not just a generator.
    Could re-write for non-sliceable iterables.
    """
    index = None
    for i,v in enumerate(seq):
        if pred(v):
            index = i
            break
    if not index:
        # either it is zero, or we didn't find any matches
        return seq
    return seq[index:] + seq[:index]

def sweep(start, field):
    remaining = set(field)
    lastangle = 0.0
    while len(field):
        candidates = day10.visible(start, field)
        if len(candidates) == 0:
            return
        clist = [(c, angle(start, c)) for c in candidates]
        clist.sort(key=lambda c:c[1])
        ## skip lower-theta candidates in later sweeps ...
        clist = rotate(clist, lambda c: c[1]>=lastangle)
        for c in clist:
            yield c[0]
        lastangle = clist[-1][1]
        remaining -= candidates
        field = list(remaining)


def rotatingLASERvapourisations(field, start):
    for pos in sweep(start, field):
        yield pos

def smallTest():
    """ new part 2 map test cases
    >>> field = smallTest()
    >>> list(itertools.islice(rotatingLASERvapourisations(field, (8,3)), 0, 9))
    [(8, 1), (9, 0), (9, 1), (10, 0), (9, 2), (11, 1), (12, 1), (11, 2), (15, 1)]

    >>> list(itertools.islice(rotatingLASERvapourisations(field, (8,3)), 9, 18))
    [(12, 2), (13, 2), (14, 2), (15, 2), (12, 3), (16, 4), (15, 4), (10, 4), (4, 4)]

    >>> list(itertools.islice(rotatingLASERvapourisations(field, (8,3)), 18, 27))
    [(2, 4), (2, 3), (0, 2), (1, 2), (0, 1), (1, 1), (5, 2), (1, 0), (5, 1)]

    >>> list(itertools.islice(rotatingLASERvapourisations(field, (8,3)), 27, 36))
    [(6, 1), (6, 0), (7, 0), (8, 0), (10, 1), (14, 0), (16, 1), (13, 3), (14, 3)]
    """
    field = day10.loadAsteroidField('day10-ex1.txt')
    return field

def largeTest():
    """ large external example test cases
    >>> field = day10.loadAsteroidField('day10-exl4.txt')
    >>> list(itertools.islice(rotatingLASERvapourisations(field, (11,13)), 0, 3))
    [(11, 12), (12, 1), (12, 2)]

    >>> list(itertools.islice(enumerate(rotatingLASERvapourisations(field, (11,13))), 9, 20, 10))
    [(9, (12, 8)), (19, (16, 0))]

    >>> list(itertools.islice(enumerate(rotatingLASERvapourisations(field, (11,13))), 49, 50))
    [(49, (16, 9))]

    >>> list(itertools.islice(rotatingLASERvapourisations(field, (11,13)), 99, 100))
    [(10, 16)]

    >>> list(itertools.islice(rotatingLASERvapourisations(field, (11,13)), 198, 201))
    [(9, 6), (8, 2), (10, 9)]

    >>> list(itertools.islice(rotatingLASERvapourisations(field, (11,13)), 298, 299))
    [(11, 1)]
    """
    pass

if __name__=='__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        import doctest
        doctest.testmod()
        sys.exit(0)

    if len(sys.argv) < 2:
        print("Syntax: {} <program file> [--debug]".format(sys.argv[0]))
        sys.exit(1)

    if len(sys.argv) > 2 and sys.argv[2] == '--debug':
        import pdb
        pdb.set_trace()

    field = day10.loadAsteroidField(sys.argv[1])
    most,best = day10.bestAsteroid(field)
    print("You can see {} asteroids from ({},{})".format(most, best[0], best[1]))
    winner = None
    for n,c in enumerate(rotatingLASERvapourisations(field, best)):
        if n == 199:
            print("{: >4d}  {}  ** WINNER **".format(n+1, c))
            winner = c
        else:
            print("{: >4d}  {}".format(n+1, c))
    print("and the 200th to be vapourised is ({},{}) -> {}".format(winner[0], winner[1], 100*winner[0]+winner[1]))



