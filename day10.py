"""
--- Day 10: Monitoring Station ---

You fly into the asteroid belt and reach the Ceres monitoring station. The Elves here have an emergency: they're having trouble tracking all of the asteroids and can't be sure they're safe.

The Elves would like to build a new monitoring station in a nearby area of space; they hand you a map of all of the asteroids in that region (your puzzle input).

The map indicates whether each position is empty (.) or contains an asteroid (#). The asteroids are much smaller than they appear on the map, and every asteroid is exactly in the center of its marked position. The asteroids can be described with X,Y coordinates where X is the distance from the left edge and Y is the distance from the top edge (so the top-left corner is 0,0 and the position immediately to its right is 1,0).

Your job is to figure out which asteroid would be the best place to build a new monitoring station. A monitoring station can detect any asteroid to which it has direct line of sight - that is, there cannot be another asteroid exactly between them. This line of sight can be at any angle, not just lines aligned to the grid or diagonally. The best location is the asteroid that can detect the largest number of other asteroids.

For example, consider the following map:

.#..#
.....
#####
....#
...##

The best location for a new monitoring station on this map is the highlighted asteroid at 3,4 because it can detect 8 asteroids, more than any other location. (The only asteroid it cannot detect is the one at 1,0; its view of this asteroid is blocked by the asteroid at 2,2.) All other asteroids are worse locations; they can detect 7 or fewer other asteroids. Here is the number of other asteroids a monitoring station on each asteroid could detect:

.7..7
.....
67775
....7
...87

Here is an asteroid (#) and some examples of the ways its line of sight might be blocked. If there were another asteroid at the location of a capital letter, the locations marked with the corresponding lowercase letter would be blocked and could not be detected:

#.........
...A......
...B..a...
.EDCG....a
..F.c.b...
.....c....
..efd.c.gb
.......c..
....f...c.
...e..d..c

Here are some larger examples:

Best is 5,8 with 33 other asteroids detected:

......#.#.
#..#.#....
..#######.
.#.#.###..
.#..#.....
..#....#.#
#..#....#.
.##.#..###
##...#..#.
.#....####

Best is 1,2 with 35 other asteroids detected:

#.#...#.#.
.###....#.
.#....#...
##.#.#.#.#
....#.#.#.
.##..###.#
..#...##..
..##....##
......#...
.####.###.

Best is 6,3 with 41 other asteroids detected:

.#..#..###
####.###.#
....###.#.
..###.##.#
##.##.#.#.
....###..#
..#.#..#.#
#..#.#.###
.##...##.#
.....#.#..

Best is 11,13 with 210 other asteroids detected:

.#..##.###...#######
##.############..##.
.#.######.########.#
.###.#######.####.#.
#####.##.#.##.###.##
..#####..#.#########
####################
#.####....###.#.#.##
##.#################
#####.##.###..####..
..######..##.#######
####.##.####...##..#
.#####..#.######.###
##...#.##########...
#.##########.#######
.####.#.###.###.#.##
....##.##.###..#####
.#.#.###########.###
#.#.#.#####.####.###
###.##.####.##.#..##

Find the best location for a new monitoring station. How many other asteroids can be detected from that location?
"""
import math
import itertools
import pdb

def x(coord):
    return coord[0]
def y(coord):
    return coord[1]
def distance(a, b):
    xx = (x(a) - x(b)) ** 2
    yy = (y(a) - y(b)) ** 2
    return math.sqrt(xx + yy)


def raycast(source, dest):
    """Generate a sequence of integral positions from (source,dest).
    Doesn't check they're 

    >>> list(raycast((0,0), (2,2)))
    [(1, 1)]

    >>> list(raycast((0,0), (0,3)))
    [(0, 1), (0, 2)]

    >>> list(raycast((0,0), (-5,0)))
    [(-1, 0), (-2, 0), (-3, 0), (-4, 0)]

    >>> list(raycast((5,5), (10,15)))
    [(6, 7), (7, 9), (8, 11), (9, 13)]
    """
    # pdb.set_trace()
    delta_x = x(dest)-x(source)
    delta_y = y(dest)-y(source)
    if delta_x and delta_y:
        div = math.gcd(delta_x, delta_y)
        dx = int(delta_x / div)
        dy = int(delta_y / div)
    else:
        if delta_y:
            # vertical
            dx = 0
            dy = int(delta_y / abs(delta_y))
        else:
            # horizontal
            dx = int(delta_x / abs(delta_x))
            dy = 0

    def next(coord, step):
        return tuple(c+s for c,s in zip(coord, step))

    pos = next(source, (dx,dy))
    while pos != dest:
        yield pos
        pos = next(pos, (dx,dy))

def visible(source, others):
    closest = sorted(others, key=lambda dst: distance(source, dst))
    if len(closest) and closest[0] == source:
        del closest[0]
    seen = set()
    for c in closest:
        ## walk the ray looking for intersections with closer asteroids
        collision = None
        for pos in raycast(source, c):
            if pos in seen:
                collision = pos
                break
        if not collision:
            seen.add(c)
    return seen

def bestAsteroid(field):
    """
    >>> bestAsteroid(set([(1,0),(4,0),(0,2),(1,2),(2,2),(3,2),(4,2),(4,3),(3,4),(4,4)]))
    (8, (3, 4))

    >>> 
    """
    most_seen = 0
    best_site = None

    for asteroid in field:
        seen = visible(asteroid, field)
        if len(seen) > most_seen:
            most_seen = len(seen)
            best_site = asteroid

    return (most_seen, best_site)

def parseAsteroidField(source):
    asteroid_field = set()
    for y,l in enumerate(l.strip() for l in source.readlines()):
        for x,c in enumerate(l):
            if c == '#':
                asteroid_field.add((x,y))
    return asteroid_field

def loadAsteroidField(filename):
    with open(filename, 'r') as affile:
        return parseAsteroidField(affile)

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

    field = loadAsteroidField(sys.argv[1])
    most,best = bestAsteroid(field)
    print("You can see {} asteroids from ({},{})".format(most, best[0], best[1]))
