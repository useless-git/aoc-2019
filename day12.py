"""
--- Day 12: The N-Body Problem ---

The space near Jupiter is not a very safe place; you need to be careful of a big distracting red spot, extreme
radiation, and a whole lot of moons swirling around. You decide to start by tracking the four largest moons: Io, Europa,
Ganymede, and Callisto.

After a brief scan, you calculate the position of each moon (your puzzle input). You just need to simulate their motion
so you can avoid them.

Each moon has a 3-dimensional position (x, y, and z) and a 3-dimensional velocity. The position of each moon is given in
your scan; the x, y, and z velocity of each moon starts at 0.

Simulate the motion of the moons in time steps. Within each time step, first update the velocity of every moon by
applying gravity. Then, once all moons' velocities have been updated, update the position of every moon by applying
velocity. Time progresses by one step once all of the positions are updated.

"""

import itertools
import pdb
import re

def add(a, b):
    return tuple(ac+bc for ac,bc in zip(a, b))

class Body:
    def __init__(self, pos=(0,0,0), vel=(0,0,0)):
        self.pos = pos
        self.vel = vel

    def ke(self):
        "kinetic energy is the sum of the absolute values of its velocity coordinates"
        return sum(abs(v) for v in self.vel)

    def pe(self):
        "potential energy is the sum of the absolute values of its x, y, and z position coordinates"
        return sum(abs(p) for p in self.pos)

    def roughkey(self):
        "quick comparison"
        return hash(self.pos + self.vel)

    def exactkey(self):
        "just a tuple with everything in"
        return self.pos + self.vel

    @staticmethod
    def applyPairwiseAcceleration(a, b):
        """To apply gravity, consider every pair of moons.
        On each axis (x, y, and z), the velocity of each moon changes by exactly +1 or -1 to pull the moons together.
        For example, if Ganymede has an x position of 3, and Callisto has a x position of 5, then Ganymede's x velocity
        changes by +1 (because 5 > 3) and Callisto's x velocity changes by -1 (because 3 < 5). However, if the positions
        on a given axis are the same, the velocity on that axis does not change for that pair of moons.

        This mutates a.vel and b.vel

        >>> ganymede = Body((3,1),(0,0))
        >>> callisto = Body((5,1),(0,0))
        >>> Body.applyPairwiseAcceleration(ganymede, callisto)
        >>> ganymede.vel
        (1, 0)
        >>> callisto.vel
        (-1, 0)
        """
        def delta(ac, bc):
            "acceleration of ac towards bc"
            if ac < bc:
                return 1
            if ac > bc:
                return -1
            return 0

        a_towards_b = tuple(delta(ac, bc) for ac,bc in zip(a.pos, b.pos))
        b_towards_a = tuple(-d for d in a_towards_b)
        a.vel = add(a.vel, a_towards_b)
        b.vel = add(b.vel, b_towards_a)

    def applyVelocity(self):
        """
        Once all gravity has been applied, apply velocity: simply add the velocity of each moon to its own position. For
        example, if Europa has a position of x=1, y=2, z=3 and a velocity of x=-2, y=0,z=3, then its new position would
        be x=-1, y=2, z=6. This process does not modify the velocity of any moon.

        This mutates self.pos

        >>> europa = Body((1,2,3),(-2,0,3))
        >>> europa.applyVelocity()
        >>> europa.pos
        (-1, 2, 6)

        >>> europa.vel
        (-2, 0, 3)
        """
        self.pos = add(self.pos, self.vel)

class System:
    def __init__(self, initialPositions):
        self.bodies = [Body(pos) for pos in initialPositions]
        self.step = 0

    def advance(self):
        self.step += 1

        # 1. pairwise gravity step
        for a,b in itertools.combinations(self.bodies, 2):
            Body.applyPairwiseAcceleration(a,b)

        # 2. move step
        for b in self.bodies:
            b.applyVelocity()

    def roughkey(self):
        "quick comparison of system state"
        return sum(b.roughkey() for b in self.bodies)

    def exactkey(self):
        "it's a great big tuple!"
        return tuple(itertools.chain(*(b.exactkey() for b in self.bodies)))

class Trie:
    "need a better size-optimized way to pack our historical states"

    class Node:
        def __init__(self):
            self.children = {}
            self.val = None

        def size(self):
            return len(self.children) + sum(c.size() for c in self.children.values())

        def find(self, keys):
            if not keys or len(keys) == 0:
                return self

            nkey = keys[0]
            if nkey in self.children:
                return self.children[nkey].find(keys[1:])

            return None

        def findOrInsert(self, keys):
            if not keys or len(keys) == 0:
                return self

            nkey = keys[0]
            if nkey in self.children:
                child = self.children[nkey]
            else:
                child = Trie.Node()
                self.children[nkey] = child
            return child.findOrInsert(keys[1:])

    def __init__(self):
        self.root = Trie.Node()

    def contains(self, keyseq):
        return self.root.find(keyseq) != None

    def find(self, keyseq):
        node = self.root.find(keyseq)
        return node.val if node is not None else None

    def insert(self, keyseq, val):
        "return True if new node inserted, False if it was already there"
        leaf = self.root.findOrInsert(keyseq)
        if leaf.val is None:
            leaf.val = val
            return True
        else:
            if leaf.val != val:
                print("Trie:{} -> {}, collides with {}".format(str(keyseq), leaf.val, val))
            return False

    def size(self):
        return self.root.size()


class History:
    def __init__(self):
        self.states = Trie()

    def record(self, system):
        # add a rough pre-check / bloom filter if necessary
        # rkey = system.roughkey()
        xkey = system.exactkey()
        return self.states.insert(xkey, system.step)

    def describeLoop(self, system):
        xkey = system.exactkey()
        previous = self.states.find(xkey)
        print("State first reached in step {}, and repeated in step {}".format(previous, system.step))
        formatBodyPosVel(system)

positionREstr = r'<x=(?P<x>-?\d+), y=(?P<y>-?\d+), z=(?P<z>-?\d+)>'
positionRE = re.compile(positionREstr)
def parsePosition(line):
    m = positionRE.match(line)
    g = m.groupdict()
    return tuple(int(s) for s in (g['x'], g['y'], g['z']))

def loadInitialSystem(filename):
    with open(filename, 'r') as source:
        positions = [parsePosition(l) for l in source.readlines()]
        return System(positions)

def formatBodyPosVel(system):
    "format matching the examples given"

    if system.step == 1:
        head = "After 1 step:"
    else:
        head = "After {} steps:".format(system.step)
    
    bodyfmt="pos=<x={: d}, y={: d}, z={: d}>, vel=<x={: d}, y={: d}, z={: d}>"
    body = [bodyfmt.format(* b.pos+b.vel) for b in system.bodies]

    return '\n'.join([head] + body)

def formatBodyEnergies(system):
    "format matching the examples given"

    if system.step == 1:
        head = "Energy after 1 step:"
    else:
        head = "Energy after {} steps:".format(system.step)
    
    bodyfmt="pot:{:2d} +{:2d} +{:2d} = {:2d};   kin:{:2d} +{:2d} +{:2d} ={:2d};   total: {:2d} *{:2d} = {}"
    def energy(body):
        pe_components = tuple(abs(p) for p in body.pos)
        ke_components = tuple(abs(v) for v in body.vel)
        pe = body.pe()
        ke = body.ke()
        return pe_components + (pe,) + ke_components + (ke, pe, ke, pe*ke)

    energies = [energy(b) for b in system.bodies]
    totals = [e[-1] for e in energies]
    body = [bodyfmt.format(*e) for e in energies]
    tail = "Sum of total energy: " + ' + '.join((str(t) for t in totals)) + ' = {}'.format(sum(totals))

    return '\n'.join([head] + body + [tail])

def testExample1():
    """
    >>> testExample1()
    After 0 steps:
    pos=<x=-1, y= 0, z= 2>, vel=<x= 0, y= 0, z= 0>
    pos=<x= 2, y=-10, z=-7>, vel=<x= 0, y= 0, z= 0>
    pos=<x= 4, y=-8, z= 8>, vel=<x= 0, y= 0, z= 0>
    pos=<x= 3, y= 5, z=-1>, vel=<x= 0, y= 0, z= 0>
    After 1 step:
    pos=<x= 2, y=-1, z= 1>, vel=<x= 3, y=-1, z=-1>
    pos=<x= 3, y=-7, z=-4>, vel=<x= 1, y= 3, z= 3>
    pos=<x= 1, y=-7, z= 5>, vel=<x=-3, y= 1, z=-3>
    pos=<x= 2, y= 2, z= 0>, vel=<x=-1, y=-3, z= 1>
    After 2 steps:
    pos=<x= 5, y=-3, z=-1>, vel=<x= 3, y=-2, z=-2>
    pos=<x= 1, y=-2, z= 2>, vel=<x=-2, y= 5, z= 6>
    pos=<x= 1, y=-4, z=-1>, vel=<x= 0, y= 3, z=-6>
    pos=<x= 1, y=-4, z= 2>, vel=<x=-1, y=-6, z= 2>
    After 3 steps:
    pos=<x= 5, y=-6, z=-1>, vel=<x= 0, y=-3, z= 0>
    pos=<x= 0, y= 0, z= 6>, vel=<x=-1, y= 2, z= 4>
    pos=<x= 2, y= 1, z=-5>, vel=<x= 1, y= 5, z=-4>
    pos=<x= 1, y=-8, z= 2>, vel=<x= 0, y=-4, z= 0>
    After 4 steps:
    pos=<x= 2, y=-8, z= 0>, vel=<x=-3, y=-2, z= 1>
    pos=<x= 2, y= 1, z= 7>, vel=<x= 2, y= 1, z= 1>
    pos=<x= 2, y= 3, z=-6>, vel=<x= 0, y= 2, z=-1>
    pos=<x= 2, y=-9, z= 1>, vel=<x= 1, y=-1, z=-1>
    After 5 steps:
    pos=<x=-1, y=-9, z= 2>, vel=<x=-3, y=-1, z= 2>
    pos=<x= 4, y= 1, z= 5>, vel=<x= 2, y= 0, z=-2>
    pos=<x= 2, y= 2, z=-4>, vel=<x= 0, y=-1, z= 2>
    pos=<x= 3, y=-7, z=-1>, vel=<x= 1, y= 2, z=-2>
    After 6 steps:
    pos=<x=-1, y=-7, z= 3>, vel=<x= 0, y= 2, z= 1>
    pos=<x= 3, y= 0, z= 0>, vel=<x=-1, y=-1, z=-5>
    pos=<x= 3, y=-2, z= 1>, vel=<x= 1, y=-4, z= 5>
    pos=<x= 3, y=-4, z=-2>, vel=<x= 0, y= 3, z=-1>
    After 7 steps:
    pos=<x= 2, y=-2, z= 1>, vel=<x= 3, y= 5, z=-2>
    pos=<x= 1, y=-4, z=-4>, vel=<x=-2, y=-4, z=-4>
    pos=<x= 3, y=-7, z= 5>, vel=<x= 0, y=-5, z= 4>
    pos=<x= 2, y= 0, z= 0>, vel=<x=-1, y= 4, z= 2>
    After 8 steps:
    pos=<x= 5, y= 2, z=-2>, vel=<x= 3, y= 4, z=-3>
    pos=<x= 2, y=-7, z=-5>, vel=<x= 1, y=-3, z=-1>
    pos=<x= 0, y=-9, z= 6>, vel=<x=-3, y=-2, z= 1>
    pos=<x= 1, y= 1, z= 3>, vel=<x=-1, y= 1, z= 3>
    After 9 steps:
    pos=<x= 5, y= 3, z=-4>, vel=<x= 0, y= 1, z=-2>
    pos=<x= 2, y=-9, z=-3>, vel=<x= 0, y=-2, z= 2>
    pos=<x= 0, y=-8, z= 4>, vel=<x= 0, y= 1, z=-2>
    pos=<x= 1, y= 1, z= 5>, vel=<x= 0, y= 0, z= 2>
    After 10 steps:
    pos=<x= 2, y= 1, z=-3>, vel=<x=-3, y=-2, z= 1>
    pos=<x= 1, y=-8, z= 0>, vel=<x=-1, y= 1, z= 3>
    pos=<x= 3, y=-6, z= 1>, vel=<x= 3, y= 2, z=-3>
    pos=<x= 2, y= 0, z= 4>, vel=<x= 1, y=-1, z=-1>
    Energy after 10 steps:
    pot: 2 + 1 + 3 =  6;   kin: 3 + 2 + 1 = 6;   total:  6 * 6 = 36
    pot: 1 + 8 + 0 =  9;   kin: 1 + 1 + 3 = 5;   total:  9 * 5 = 45
    pot: 3 + 6 + 1 = 10;   kin: 3 + 2 + 3 = 8;   total: 10 * 8 = 80
    pot: 2 + 0 + 4 =  6;   kin: 1 + 1 + 1 = 3;   total:  6 * 3 = 18
    Sum of total energy: 36 + 45 + 80 + 18 = 179
    """
    s = loadInitialSystem('day12-ex1.txt')
    print(formatBodyPosVel(s)) # 0
    s.advance()
    print(formatBodyPosVel(s)) # 1
    s.advance()
    print(formatBodyPosVel(s)) # 2
    s.advance()
    print(formatBodyPosVel(s)) # 3
    s.advance()
    print(formatBodyPosVel(s)) # 4
    s.advance()
    print(formatBodyPosVel(s)) # 5
    s.advance()
    print(formatBodyPosVel(s)) # 6
    s.advance()
    print(formatBodyPosVel(s)) # 7
    s.advance()
    print(formatBodyPosVel(s)) # 8
    s.advance()
    print(formatBodyPosVel(s)) # 9
    s.advance()
    print(formatBodyPosVel(s)) # 10
    print(formatBodyEnergies(s))

import time

class Spinner:
    SYMS = r'|/-\*'
    def __init__(self, interval, out, fmt=" {sym:s} {tc[0]:02d}:{tc[1]:02d}:{tc[2]:02d}.{tc[3]:03d} === ({ips:.1f}/sec) === {val}       \r"):
        self.interval = interval
        self.current = 0
        self.beginTS = Spinner.now()
        self.out = out
        self.fmt = fmt

    def advance(self, value):
        if value >= self.current + self.interval:
            # update state
            self.current = value

            # graphic spinner
            sym = Spinner.SYMS[(value // self.interval) % len(Spinner.SYMS)]

            # elapsed time vals
            now = Spinner.now()
            elapsed = now - self.beginTS
            ips = value / elapsed
            tc = Spinner.timeComponents(elapsed)

            self.out.write(self.fmt.format(sym=sym, val=value, sec=elapsed, tc=tc, ips=ips))

    @staticmethod
    def now():
        return time.process_time()

    @staticmethod
    def timeComponents(ftime):
        # pdb.set_trace()
        raw_ns = int(1000000000 * ftime)
        ns = raw_ns % 1000
        us = (raw_ns // 1000) % 1000
        ms = (raw_ns // 1000000) % 1000
        raw_sec = int(ftime)
        ss = raw_sec % 60
        mm = (raw_sec // 60) % 60
        hh = (raw_sec // 60) // 60
        return (hh, mm, ss, ms, us, ns)


if __name__=='__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        import doctest
        doctest.testmod()
        sys.exit(0)


    s = loadInitialSystem('day12-input.txt')

    if len(sys.argv) > 1 and sys.argv[1] == '--part2':
        h = History()
        spin = Spinner(1000, sys.stdout)
        try:
            # pdb.set_trace()
            while h.record(s):
                s.advance()
                spin.advance(s.step)
            print("\n== done ==")
            h.describeLoop(s)
        except:
            # pdb.set_trace()
            # TODO discard Trie and minimize unique tracking size
            print("\ninterrupted/failed with {} Trie entries after {} steps".format(h.states.size(), s.step))
    else:
        for step in range(1000):
            s.advance()
        print(formatBodyEnergies(s))
