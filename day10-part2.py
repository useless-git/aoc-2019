"""
--- Part Two ---

Once you give them the coordinates, the Elves quickly deploy an Instant Monitoring Station to the location and discover the worst: there are simply too many asteroids.

The only solution is complete vaporization by giant laser.

Fortunately, in addition to an asteroid scanner, the new monitoring station also comes equipped with a giant rotating laser perfect for vaporizing asteroids. The laser starts by pointing up and always rotates clockwise, vaporizing any asteroid it hits.

If multiple asteroids are exactly in line with the station, the laser only has enough power to vaporize one of them before continuing its rotation. In other words, the same asteroids that can be detected can be vaporized, but if vaporizing one asteroid makes another one detectable, the newly-detected asteroid won't be vaporized until the laser has returned to the same position by rotating a full 360 degrees.

...

The Elves are placing bets on which will be the 200th asteroid to be vaporized. Win the bet by determining which asteroid that will be; what do you get if you multiply its X coordinate by 100 and then add its Y coordinate? (For example, 8,2 becomes 802.)
"""
import day10
import itertools

def x(coord):
    return coord[0]
def y(coord):
    return coord[1]

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

def rotatingLASERvapourisations(field, source):
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
    winner = next(c for n,c in enumerate(rotatingLASERvapourisations(field, best)) if n == 200)
    print("and the 200th to be vapourised is ({},{}) -> {}".format(winner[0], winner[1], 100*winner[0]+winner[1]))



