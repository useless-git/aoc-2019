"""
--- Day 3: Crossed Wires ---

The gravity assist was successful, and you're well on your way to the Venus refuelling station. During the rush back on Earth, the fuel management system wasn't completely installed, so that's next on the priority list.

Opening the front panel reveals a jumble of wires. Specifically, two wires are connected to a central port and extend outward on a grid. You trace the path each wire takes as it leaves the central port, one wire per line of text (your puzzle input).

The wires twist and turn, but the two wires occasionally cross paths. To fix the circuit, you need to find the intersection point closest to the central port. Because the wires are on a grid, use the Manhattan distance for this measurement. While the wires do technically cross right at the central port where they both start, this point does not count, nor does a wire count as crossing with itself.""

For example, if the first wire's path is R8,U5,L5,D3, then starting from the central port (o), it goes right 8, up 5, left 5, and finally down 3:

...........
...........
...........
....+----+.
....|....|.
....|....|.
....|....|.
.........|.
.o-------+.
...........

Then, if the second wire's path is U7,R6,D4,L4, it goes up 7, right 6, down 4, and left 4:

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

These wires cross at two locations (marked X), but the lower-left one is closer to the central port: its distance is 3 + 3 = 6.

Here are a few more examples:

    R75,D30,R83,U83,L12,D49,R71,U7,L72
    U62,R66,U55,R34,D71,R55,D58,R83 = distance 159
    R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51
    U98,R91,D20,R16,D67,R40,U7,R15,U6,R7 = distance 135

What is the Manhattan distance from the central port to the closest intersection?
"""

def metric(x,y):
    """Manhattan distance
    
    >>> metric(3,3)
    6
    """
    return abs(x) + abs(y)

## simple solver: build a complete (x,y)->value map
## where value is 1 for the first wire, 2 for the second, and 3 for both (intersection)
from collections import defaultdict

intersections = {}
def addIntersection(x, y):
    intersections[metric(x,y)] = (x,y)

grid = defaultdict(int)
def walk(path, wirenum):
    step = {'R':(1,0), 'L':(-1,0), 'U':(0,1), 'D':(0,-1)}

    x,y=(0,0)
    for segment in path:
        direction = segment[0]
        distance = int(segment[1:])
        dx,dy = step[direction]
        for _ in range(distance):
            x,y = (x+dx, y+dy)
            val = grid[(x,y)]
            nval = val | wirenum
            if nval != val:
                grid[(x,y)] = nval
                if nval == 3:
                    addIntersection(x,y)

def closestIntersection(line1,line2):
    """Walk both paths and return the closest intersection

    >>> closestIntersection('R8,U5,L5,D3','U7,R6,D4,L4')
    6

    >>> closestIntersection('R75,D30,R83,U83,L12,D49,R71,U7,L72','U62,R66,U55,R34,D71,R55,D58,R83')
    159
    >>> closestIntersection('R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51','U98,R91,D20,R16,D67,R40,U7,R15,U6,R7')
    135
    """
    path1 = line1.split(',')
    path2 = line2.split(',')
    walk(path1, 1)
    walk(path2, 2)

    distances = intersections.keys()
    distances.sort()
    return distances[0]

import sys

if len(sys.argv) > 1 and sys.argv[1] == '--test':
    import doctest
    doctest.testmod()
    sys.exit(0)

line1=sys.stdin.readline()
line2=sys.stdin.readline()
result = closestIntersection(line1,line2)
print result

