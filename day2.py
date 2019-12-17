TRACE=0
def trace(s):
    if TRACE:
        print(s)

class OpcodeAdd:
    OPC = 1
    LEN = 4

    @staticmethod
    def execute(source, pc):
        in1addr = source[pc + 1]
        in2addr = source[pc + 2]
        outaddr = source[pc + 3]
        in1 = source[in1addr]
        in2 = source[in2addr]
        trace("ADD (*{0}={1}) (*{2}={3}) -> *{4}".format(in1addr, in1, in2addr, in2, outaddr))
        source[outaddr] = in1 + in2
        return pc + OpcodeAdd.LEN

class OpcodeMul:
    OPC = 2
    LEN = 4

    @staticmethod
    def execute(source, pc):
        in1addr = source[pc + 1]
        in2addr = source[pc + 2]
        outaddr = source[pc + 3]
        in1 = source[in1addr]
        in2 = source[in2addr]
        trace("MUL (*{0}={1}) (*{2}={3}) -> *{4}".format(in1addr, in1, in2addr, in2, outaddr))
        source[outaddr] = in1 * in2
        return pc + OpcodeMul.LEN

class OpcodeEnd:
    OPC = 99
    LEN = 1

    @staticmethod
    def execute(source, pc):
        trace("END")
        raise StopIteration

class IntcodeProcessor:
    def __init__(self, opcodes):
        self.ops = dict([(op.OPC, op) for op in opcodes])
        self.dat = {}
        self.pc = 0

    def execute_one(self):
        opcode = self.dat[self.pc]
        op = self.ops[opcode]
        nextpc = op.execute(self.dat, self.pc)
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
        except:
            print("some kind of error")

import sys
import collections

if len(sys.argv) > 1 and sys.argv[1] == '-v':
    TRACE=1

## import pdb
## pdb.set_trace()
## ipc.execute([2,3,0,3,99])

inprog = [int(x) for x in sys.stdin.readline().strip().split(',')]
ipc = IntcodeProcessor([OpcodeAdd, OpcodeMul, OpcodeEnd])
ipc.execute(inprog)

print("==result==\nPC={0}".format(ipc.pc))
maxkey = max(ipc.dat.iterkeys())
outprog_dict = collections.defaultdict(int, ipc.dat)
outprog = [outprog_dict[i] for i in range(maxkey+1)]
print outprog

            
