"""
--- Part Two ---

It turns out that this circuit is very timing-sensitive; you actually need to minimize the signal delay.

To do this, calculate the number of steps each wire takes to reach each intersection; choose the intersection where the sum of both wires' steps is lowest. If a wire visits a position on the grid multiple times, use the steps value from the first time it visits that position when calculating the total value of a specific intersection.

The number of steps a wire takes is the total number of grid squares the wire has entered to get to that location, including the intersection being considered. Again consider the example from above:

...........
.+-----+...
.|.....|...
.|..+--X-+.
.|..|..|.|.
.|.-X--+.|.
.|..|....|.
.|.......|.
.o-------+.
...........

In the above example, the intersection closest to the central port is reached after 8+5+5+2 = 20 steps by the first wire and 7+6+4+3 = 20 steps by the second wire for a total of 20+20 = 40 steps.

However, the top-right intersection is better: the first wire takes only 8+5+2 = 15 and the second wire takes only 7+6+2 = 15, a total of 15+15 = 30 steps.

Here are the best steps for the extra examples from above:

    R75,D30,R83,U83,L12,D49,R71,U7,L72
    U62,R66,U55,R34,D71,R55,D58,R83 = 610 steps
    R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51
    U98,R91,D20,R16,D67,R40,U7,R15,U6,R7 = 410 steps

What is the fewest combined steps the wires must take to reach an intersection?
"""

def metric(x,y):
    """Manhattan distance
    
    >>> metric(3,3)
    6
    """
    return abs(x) + abs(y)

## less simple solver: build a complete (x,y)->(d1,d2) map
## where d1 is the minimum path distance along the first wire, d2 the second wire
from collections import defaultdict

shortest_intersection = None
def addIntersection(distance):
    global shortest_intersection
    if shortest_intersection and shortest_intersection <= distance:
        pass
    else:
        shortest_intersection = distance

grid = defaultdict(lambda :[0,0])
def walk(path, wirenum):
    """switch to zero-based wirenum for indexing"""
    step = {'R':(1,0), 'L':(-1,0), 'U':(0,1), 'D':(0,-1)}

    x,y=(0,0)    # current coordinats
    pathlen=0       # path length so far

    for segment in path:
        direction = segment[0]
        distance = int(segment[1:])
        dx,dy = step[direction]
        for _ in range(distance):
            x,y = (x+dx, y+dy)
            pathlen += 1 # every step adds 1
            ## two stored path lengths per coord
            stored = grid[(x,y)]
            if stored[wirenum] == 0:
                stored[wirenum] = pathlen # mutate in-place
            if stored[0] and stored[1]:
                addIntersection(stored[0]+stored[1])

def closestIntersection(line1,line2):
    """Walk both paths and return the intersection with the shortest total path length

    >>> closestIntersection('R8,U5,L5,D3','U7,R6,D4,L4')
    30

    >>> closestIntersection('R75,D30,R83,U83,L12,D49,R71,U7,L72','U62,R66,U55,R34,D71,R55,D58,R83')
    610
    >>> closestIntersection('R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51','U98,R91,D20,R16,D67,R40,U7,R15,U6,R7')
    410
    """
    path1 = line1.split(',')
    path2 = line2.split(',')
    walk(path1, 0)
    walk(path2, 1)

    return shortest_intersection

import sys

if len(sys.argv) > 1 and sys.argv[1] == '--test':
    import doctest
    doctest.testmod()
    sys.exit(0)

line1=sys.stdin.readline()
line2=sys.stdin.readline()
result = closestIntersection(line1,line2)
print result

