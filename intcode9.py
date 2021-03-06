import sys
import collections

TRACE=0
def trace(s):
    if TRACE:
        print(s)

## parameter modes
REL=2
IMM=1
IND=0
modestring = {REL:"REL", IMM:"IMM", IND:"IND"}

## HACK - mutable global state
## (otherwise should thread interpreter state through op execute calls)
RELATIVE_BASE = 0

def getInput(prompt):
    return int(input(prompt))

def writeOutput(prompt, value):
    print(prompt + "{}".format(value))

class GenericOp:
    """
    Generic wrapper for operators.

    We use "opcode" to mean the integer value in the code, "*Op" to mean the class implementing that operator.

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
        global RELATIVE_BASE
        for e in expected:
            actual = pmask % 10
            if actual == e:
                trace("[{}] param: {} {}".format(pc, modestring[e], source[pc]))
                params.append(source[pc])
            elif actual == IND and e == IMM:
                # expected imm got ind, so dereference
                trace("[{}] param: deref *{} -> {}".format(pc, source[pc], source[source[pc]]))
                params.append(source[source[pc]])
            elif actual == REL and e == IMM:
                # expected imm got rel, so dereference
                trace("[{}] param: deref *({}{:+d}) -> {}".format(pc, source[pc], RELATIVE_BASE, source[source[pc]+RELATIVE_BASE]))
                params.append(source[source[pc]+RELATIVE_BASE])
            elif actual == REL and e == IND:
                # expected imm got rel, so calculate absolute address
                trace("[{}] param: relbase ({}{:+d}) -> {}".format(pc, source[pc], RELATIVE_BASE, source[pc]+RELATIVE_BASE))
                params.append(source[pc]+RELATIVE_BASE)
            else:
                # expected ind, got imm !?
                source_slice = [source[x] for x in range(pc, pc+len(expected))]
                trace("got param type {} but expected {} in OPC:{} PMASK:{} expected:{} PC:{} source:{}".format(actual, e, opcode, pmask, expected, pc, source_slice))
                assert(False)
            pc += 1
            pmask = pmask // 10
        return params

    @staticmethod
    def execute(operator, opcode, source, pc):
        params = GenericOp.__parse_params(opcode, operator.PARAM, source, pc)
        return operator.execute(source, pc, *params)

class OpAdd:
    OPC = 1
    PARAM = [IMM,IMM,IND]

    @staticmethod
    def execute(source, pc, in1, in2, outaddr):
        trace("[{}] ADD ({}) ({}) -> *{}".format(pc, in1, in2, outaddr))
        source[outaddr] = in1 + in2
        return pc + 1 + len(OpAdd.PARAM)

class OpMul:
    OPC = 2
    PARAM = [IMM,IMM,IND]

    @staticmethod
    def execute(source, pc, in1, in2, outaddr):
        trace("[{}] MUL ({}) ({}) -> *{}".format(pc, in1, in2, outaddr))
        source[outaddr] = in1 * in2
        return pc + 1 + len(OpMul.PARAM)

class OpInput:
    OPC = 3
    PARAM = [IND]

    @staticmethod
    def execute(source, pc, outaddr):
        directin = getInput('[{0}] enter a value: '.format(pc))
        trace("[{}] INP ({}) -> *{}".format(pc, directin, outaddr))
        source[outaddr] = directin
        return pc + 1 + len(OpInput.PARAM)

class OpOutput:
    OPC = 4
    PARAM = [IMM]

    @staticmethod
    def execute(source, pc, value):
        writeOutput("[{}] OUT ".format(pc), value)
        return pc + 1 + len(OpOutput.PARAM)

class OpJNZ:
    OPC = 5
    PARAM = [IMM, IMM]

    @staticmethod
    def execute(source, pc, flag, dst):
        trace("[{}] JNZ {} ({}) {}".format(pc, flag, bool(flag), dst))
        if flag:
            return dst
        return pc + 1 + len(OpJNZ.PARAM)

class OpJZ:
    OPC = 6
    PARAM = [IMM, IMM]

    @staticmethod
    def execute(source, pc, flag, dst):
        trace("[{}] JZ {} ({}) {}".format(pc, flag, bool(flag==0), dst))
        if flag == 0:
            return dst
        return pc + 1 + len(OpJZ.PARAM)

class OpLT:
    OPC = 7
    PARAM = [IMM, IMM, IND]

    @staticmethod
    def execute(source, pc, left, right, dst):
        trace("[{}] LT {} {} ({}) {}".format(pc, left, right, bool(left < right), dst))
        if left < right:
            source[dst] = 1
        else:
            source[dst] = 0
        return pc + 1 + len(OpLT.PARAM)

class OpEQ:
    OPC = 8
    PARAM = [IMM, IMM, IND]

    @staticmethod
    def execute(source, pc, left, right, dst):
        trace("[{}] EQ {} {} ({}) {}".format(pc, left, right, bool(left == right), dst))
        if left == right:
            source[dst] = 1
        else:
            source[dst] = 0
        return pc + 1 + len(OpLT.PARAM)

class OpSRB:
    """Set Relative Base"""
    OPC = 9
    PARAM = [IMM]

    @staticmethod
    def execute(source, pc, delta):
        global RELATIVE_BASE
        next_rb = RELATIVE_BASE + delta
        trace("[{}] SRB {} {:+d} -> {}".format(pc, RELATIVE_BASE, delta, next_rb))
        RELATIVE_BASE = next_rb
        return pc + 1 + len(OpSRB.PARAM)

class OpEnd:
    OPC = 99
    PARAM = []

    @staticmethod
    def execute(source, pc):
        trace("[{}] END".format(pc))
        raise StopIteration

class IntcodeProcessor:
    def __init__(self, opcodes):
        self.ops = dict([(op.OPC, op) for op in opcodes])
        self.dat = collections.defaultdict(int)
        self.pc = 0

    def execute_one(self):
        raw_opcode = self.dat[self.pc]
        opcode = raw_opcode % 100
        if not opcode in self.ops:
            trace("opcode {}({}) not recognised".format(raw_opcode, opcode))
        op = self.ops[opcode]
        nextpc = GenericOp.execute(op, raw_opcode, self.dat, self.pc)
        return nextpc

    def execute(self, program):
        """program can be any iterable sequence of integer values"""
        self.dat = collections.defaultdict(int, enumerate(program))
        self.pc = 0

        try:
            while True:
                npc = self.execute_one()
                self.pc = npc
        except StopIteration:
            return
#       except Exception as ex:
#           print("some kind of error: {0}".format(sys.exc_info()[2]))

def makeIntcodeProcessor():
    "decouple the operator list from the main driver code"
    return IntcodeProcessor([OpAdd, OpMul, OpInput, OpOutput, OpJNZ, OpJZ, OpLT, OpEQ, OpSRB, OpEnd])

if __name__=='__main__':
    if len(sys.argv) > 2 and sys.argv[2] == '-v':
        TRACE=1

    if len(sys.argv) < 2:
        print("Syntax: {} <program file> [-v]".format(sys.argv[0]))
        sys.exit(1)

    progfile = open(sys.argv[1], 'r')

    ## import pdb
    ## pdb.set_trace()
    ## ipc.execute([2,3,0,3,99])

    line = progfile.readline().strip()
    while line.startswith('#'):
        ## print (and skip) comments starting with hash
        print(line)
        line = progfile.readline().strip()

    inprog = [int(x) for x in line.split(',')]
    ipc = makeIntcodeProcessor()
    ipc.execute(inprog)

    if TRACE:
        print("==result==\nPC={0}".format(ipc.pc))
        maxkey = max(ipc.dat.keys())
        outprog_dict = collections.defaultdict(int, ipc.dat)
        outprog = [outprog_dict[i] for i in range(maxkey+1)]
        print(outprog)

                    
