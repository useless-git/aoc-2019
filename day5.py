import sys
import collections

TRACE=0
def trace(s):
    if TRACE:
        print(s)

## parameter modes
IMM=1
IND=0
modestring = {IMM:"IMM", IND:"IND"}

class GenericOpcode:
    """
    Generic wrapper for opcodes.

    Preconditions on concrete class:
     - PARAM contains expected parameter types including output addr if any
    """
    @staticmethod
    def __parse_params(opcode, expected, source, pc):
        pmask = opcode // 100
        opstr = str([source[x] for x in range(pc, pc+len(expected))])
        trace("[{0}] decode {1} with pmask {2:0{3}} ={4}=".format(pc, opcode, pmask, len(expected), opstr))
        pc += 1 # skip the opcode itself
        params = []
        for e in expected:
            actual = pmask % 10
            if actual == e:
                trace("[{}] param: {} {}".format(pc, modestring[e], source[pc]))
                params.append(source[pc])
            elif actual == IND and e == IMM:
                # expected imm got ind, so dereference
                trace("[{}] param: deref *{} -> {}".format(pc, source[pc], source[source[pc]]))
                params.append(source[source[pc]])
            else:
                # expected ind, got imm !?
                trace("got param type {} but expected {} in OPC:{} PMASK:{} expected:{} PC:{} source:{}".format(actual, e, opcode, pmask, expected, pc, source[pc:pc+len(expected)]))
                assert(False)
            pc += 1
            pmask = pmask // 10
        return params

    @staticmethod
    def execute(operator, opcode, source, pc):
        params = GenericOpcode.__parse_params(opcode, operator.PARAM, source, pc)
        operator.execute(source, pc, *params)
        return pc + 1 + len(params)

class OpcodeAdd:
    OPC = 1
    PARAM = [IMM,IMM,IND]

    @staticmethod
    def execute(source, pc, in1, in2, outaddr):
        trace("[{}] ADD ({}) ({}) -> *{}".format(pc, in1, in2, outaddr))
        source[outaddr] = in1 + in2

class OpcodeMul:
    OPC = 2
    PARAM = [IMM,IMM,IND]

    @staticmethod
    def execute(source, pc, in1, in2, outaddr):
        trace("[{}] MUL ({}) ({}) -> *{}".format(pc, in1, in2, outaddr))
        source[outaddr] = in1 * in2

class OpcodeInput:
    OPC = 3
    PARAM = [IND]

    @staticmethod
    def execute(source, pc, outaddr):
        directin = int(input('[{0}] enter a value: '.format(pc)))
        trace("[{}] INP ({}) -> *{}".format(pc, directin, outaddr))
        source[outaddr] = directin

class OpcodeOutput:
    OPC = 4
    PARAM = [IMM]

    @staticmethod
    def execute(source, pc, value):
        print("[{}] OUT {}".format(pc, value))

class OpcodeEnd:
    OPC = 99
    PARAM = []

    @staticmethod
    def execute(source, pc):
        trace("[{}] END".format(pc))
        raise StopIteration

class IntcodeProcessor:
    def __init__(self, opcodes):
        self.ops = dict([(op.OPC, op) for op in opcodes])
        self.dat = {}
        self.pc = 0

    def execute_one(self):
        raw_opcode = self.dat[self.pc]
        opcode = raw_opcode % 100
        if not opcode in self.ops:
            trace("opcode {}({}) not recognised".format(raw_opcode, opcode))
        op = self.ops[opcode]
        nextpc = GenericOpcode.execute(op, raw_opcode, self.dat, self.pc)
        return nextpc

    def execute(self, program):
        """program can be any iterable sequence of integer values"""
        self.dat = dict(enumerate(program))
        self.pc = 0

        try:
            while True:
                npc = self.execute_one()
                self.pc = npc
        except StopIteration:
            return
#       except Exception as ex:
#           print("some kind of error: {0}".format(sys.exc_info()[2]))

if len(sys.argv) > 2 and sys.argv[2] == '-v':
    TRACE=1

if len(sys.argv) < 2:
    print("Syntax: {} <program file> [-v]".format(sys.argv[0]))
    sys.exit(1)

progfile = open(sys.argv[1], 'r')

## import pdb
## pdb.set_trace()
## ipc.execute([2,3,0,3,99])

inprog = [int(x) for x in progfile.readline().strip().split(',')]
ipc = IntcodeProcessor([OpcodeAdd, OpcodeMul, OpcodeInput, OpcodeOutput, OpcodeEnd])
ipc.execute(inprog)

print("==result==\nPC={0}".format(ipc.pc))
maxkey = max(ipc.dat.keys())
outprog_dict = collections.defaultdict(int, ipc.dat)
outprog = [outprog_dict[i] for i in range(maxkey+1)]
print(outprog)

            
