
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
            if cName in self.bodies:
                # fix up the chain for out-of-order creation
                child = self.bodies[cName]
                if child.parent and child.parent != parent:
                    print("child {} already exists with parent {} (would attach to {})".format(cName, child.parent.name, pName))
                else:
                    child.parent = parent
            else:
                self.bodies[cName] = Body(cName, parent)
            # print("{}){} -> {}".format(pName, cName, child.orbitalChain()))

    def totalOrbitalDepth(self):
        return sum((b.orbitalDepth() for b in self.bodies.values()))

    def com(self):
        return [b.name for b in self.bodies.values() if b.orbitalDepth() == 0]

    def orbitalTransfers(self, fromName, toName):
        source = self.bodies[fromName].parent
        sourcepath = list(reversed(source.orbitalChain()))

        ## build the outbound path lookup
        dest = self.bodies[toName].parent
        destpath = list(reversed(dest.orbitalChain()))
        deststeps = dict(((name, val) for val,name in enumerate(destpath)))

        for step in enumerate(sourcepath):
            if step[1] in deststeps:
                outbound = deststeps[step[1]]
                print("{} steps inwards {}->{}->{} + {} steps outwards {}->{}->{}".format(step[0], fromName, sourcepath[:step[0]], step[1], outbound, step[1], dest.orbitalChain()[-outbound:], toName))
                return step[0] + outbound


import sys
import pdb

om = OrbitalMap()
with open(sys.argv[1], 'r') as mapfile:
    om.load(mapfile)
print("un-parented: COM={}".format(om.com()))
print("total orbital depth: {}".format(om.totalOrbitalDepth()))
## pdb.set_trace()
print("transfers YOU->SAN: {}".format(om.orbitalTransfers('YOU', 'SAN')))
