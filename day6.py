
class Body:
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

    def orbitalDepth(self):
        """memoize if it gets too slow"""
        if not self.parent:
            # we're not orbiting anything
            return 0
        return 1 + self.parent.orbitalDepth()

    def orbitalChain(self):
        if self.parent:
            prefix = self.parent.orbitalChain()
        else:
            prefix = []
        return prefix + [self.name]

class OrbitalMap:
    def __init__(self):
        self.bodies = {}

    def load(self, source):
        for line in source:
            pName,cName = [s.strip() for s in line.split(')')]
            if not pName in self.bodies:
                self.bodies[pName] = Body(pName, None)
            parent = self.bodies[pName]
            child = Body(cName, parent)
            self.bodies[cName] = child
            print("{}){} -> {}".format(pName, cName, child.orbitalChain()))

    def totalOrbitalDepth(self):
        return sum((b.orbitalDepth() for b in self.bodies.values()))

    def com(self):
        return [b.name for b in self.bodies.values() if b.orbitalDepth() == 0]

import sys
import pdb
## pdb.set_trace()

om = OrbitalMap()
with open(sys.argv[1], 'r') as mapfile:
    om.load(mapfile)
print("un-parented: COM={}".format(om.com()))
print("total orbital depth: {}".format(om.totalOrbitalDepth()))

