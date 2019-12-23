"""
https://adventofcode.com/2019/day/7#part2

--- Part Two ---

It's no good - in this configuration, the amplifiers can't generate a large enough output signal to produce the thrust you'll need. The Elves quickly talk you through rewiring the amplifiers into a feedback loop:

      O-------O  O-------O  O-------O  O-------O  O-------O
0 -+->| Amp A |->| Amp B |->| Amp C |->| Amp D |->| Amp E |-.
   |  O-------O  O-------O  O-------O  O-------O  O-------O |
   |                                                        |
   '--------------------------------------------------------+
                                                            |
                                                            v
                                                     (to thrusters)

Most of the amplifiers are connected as they were before; amplifier A's output is connected to amplifier B's input, and so on. However, the output from amplifier E is now connected into amplifier A's input. This creates the feedback loop: the signal will be sent through the amplifiers many times.

In feedback loop mode, the amplifiers need totally different phase settings: integers from 5 to 9, again each used exactly once. These settings will cause the Amplifier Controller Software to repeatedly take input and produce output many times before halting. Provide each amplifier its phase setting at its first input instruction; all further input/output instructions are for signals.

Don't restart the Amplifier Controller Software on any amplifier during this process. Each one should continue receiving and sending signals until it halts.

All signals sent or received in this process will be between pairs of amplifiers except the very first signal and the very last signal. To start the process, a 0 signal is sent to amplifier A's input exactly once.

Eventually, the software on the amplifiers will halt after they have processed the final loop. When this happens, the last output signal from amplifier E is sent to the thrusters. Your job is to find the largest output signal that can be sent to the thrusters using the new phase settings and feedback loop arrangement.

Here are some example programs:

    Max thruster signal 139629729 (from phase setting sequence 9,8,7,6,5):

    3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,
    27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5

    Max thruster signal 18216 (from phase setting sequence 9,7,8,5,6):

    3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,
    -5,54,1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,
    53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10

Try every combination of the new phase settings on the amplifier feedback loop. What is the highest signal that can be sent to the thrusters?

"""

### yield on output and chain to input that way?
### it's going to be easier to chain with multiprocessing in this case ...
import intcode7

def runAmpProc(inpipe, outpipe, result, program):
    # first intercept the inputs
    def localGetInput(prompt):
        nonlocal inpipe
        return inpipe.recv()

    # then intercept the output
    def localWriteOutput(prompt, value):
        nonlocal result
        result.value = value
        nonlocal outpipe
        outpipe.send(value)

    # and finally run up our processor
    intcode7.getInput = localGetInput
    intcode7.writeOutput = localWriteOutput
    ipc = intcode7.makeIntcodeProcessor()
    ipc.execute(program)

import multiprocessing

def runAmpPipeline(phases, program):
    # one pipe per stage
    pipes = [multiprocessing.Pipe() for _ in phases]
    initial_input = pipes[0][0] # first stage reads from the other end of this pipe
    final_output = pipes[-1][1] # last stage writes to the other end of this pipe
    io_pairs = [(i[1], o[0]) for i,o in zip(pipes[:-1],pipes[1:])] + [(final_output, initial_input)]
    params = [(i, o, multiprocessing.Value('i', 0)) for i,o in io_pairs]
    # start all the subprocesses
    stages = [multiprocessing.Process(target=runAmpProc, args=(i, o, v, program)) for i,o,v in params]
    for stage in stages:
        stage.start()
    # send the phase to each subprocess as its first input
    for phase, io in zip(phases, pipes):
        io[0].send(phase)
    # kickoff
    initial_input.send(0)
    # wait for the result
    for stage in stages:
        stage.join()
    return params[-1][2].value

def testAmpSequence(phases, program):
    """create a separate processor for each sequence, give it the correct phase and pass its output to the next stage
    """
    value = 0
    for p in phases:
        value = runAmp([p, value], program)
    return value

import itertools
def maxAmpSequence(phases, program):
    maxval = 0
    maxseq = None
    for phase_sequence in itertools.permutations(phases):
        val = runAmpPipeline(phase_sequence, program)
        if val > maxval:
            maxval = val
            maxseq = phase_sequence
    return maxval, maxseq

import sys
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
    val, seq = maxAmpSequence([5,6,7,8,9], inprog)
    print("max = {}\nfrom sequence {}".format(val, seq))


