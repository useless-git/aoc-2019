"""
--- Day 11: Space Police ---

On the way to Jupiter, you're pulled over by the Space Police.

"Attention, unmarked spacecraft! You are in violation of Space Law! All spacecraft must have a clearly visible
registration identifier! You have 24 hours to comply or be sent to Space Jail!"

Not wanting to be sent to Space Jail, you radio back to the Elves on Earth for help. Although it takes almost three
hours for their reply signal to reach you, they send instructions for how to power up the emergency hull painting robot
and even provide a small Intcode program (your puzzle input) that will cause it to paint your ship appropriately.

There's just one problem: you don't have an emergency hull painting robot.

You'll need to build a new emergency hull painting robot. The robot needs to be able to move around on the grid of
square panels on the side of your ship, detect the color of its current panel, and paint its current panel black or
white. (All of the panels are currently black.)

The Intcode program will serve as the brain of the robot. The program uses input instructions to access the robot's
camera: provide 0 if the robot is over a black panel or 1 if the robot is over a white panel. Then, the program will
output two values:

    First, it will output a value indicating the color to paint the panel the robot is over: 0 means to paint the panel
    black, and 1 means to paint the panel white.
    
    Second, it will output a value indicating the direction the robot should turn: 0 means it should turn left 90
    degrees, and 1 means it should turn right 90 degrees.

After the robot turns, it should always move forward exactly one panel. The robot starts facing up.

The robot will continue running for a while like this and halt when it is finished drawing. Do not restart the Intcode
computer inside the robot during this process.

For example, suppose the robot is about to start running. Drawing black panels as ., white panels as #, and the robot
pointing the direction it is facing (< ^ > v), the initial state and region near the robot looks like this:

.....
.....
..^..
.....
.....

The panel under the robot (not visible here because a ^ is shown instead) is also black, and so any input instructions
at this point should be provided 0. Suppose the robot eventually outputs 1 (paint white) and then 0 (turn left). After
taking these actions and moving forward one panel, the region now looks like this:

.....
.....
.<#..
.....
.....

Input instructions should still be provided 0. Next, the robot might output 0 (paint black) and then 0 (turn left):

.....
.....
..#..
.v...
.....

After more outputs (1,0, 1,0):

.....
.....
..^..
.##..
.....

The robot is now back where it started, but because it is now on a white panel, input instructions should be provided 1.
After several more outputs (0,1, 1,0, 1,0), the area looks like this:

.....
..<#.
...#.
.##..
.....

Before you deploy the robot, you should probably have an estimate of the area it will cover: specifically, you need to
know the number of panels it paints at least once, regardless of color. In the example above, the robot painted 6 panels
at least once. (It painted its starting panel twice, but that panel is still only counted once; it also never painted
the panel it ended on.)

Build a new emergency hull painting robot and run the Intcode program on it. How many panels does it paint at least
once?

"""
import collections
import intcode9

class Turtle:
    """this emergency hull-painting robot is very LOGO-like"""
    Directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    DirectionNames = ["up", "right", "down", "left"]
    DirectionSymbols = ["^", ">", "v", "<"]

    def __init__(self, initial = 0):
        self.direction = 0
        self.pos = (0,0)
        self.field = collections.defaultdict(int)
        self.written = collections.defaultdict(int) # stop outputs being polluted by lazily-populated inputs

        # set the initial panel colour for part2
        self.field[self.pos] = initial

        def localGetInput(prompt):
            """provide current panel colour as input"""
            nonlocal self
            intcode9.trace(">> INPUT {} is {}".format(self.pos, self.field[self.pos]))
            return self.field[self.pos]

        outputs = 0
        def localWriteOutput(prompt, value):
            """get paint colour + rotation"""
            nonlocal outputs
            nonlocal self
            # even numbered outputs are paint
            isPaintOutput = (outputs % 2 == 0)
            outputs += 1
            if isPaintOutput:
                intcode9.trace("<< PAINT {} {}".format(self.pos, value))
                self.written[self.pos] = value
                self.field[self.pos] = value
            else:
                if value:
                    dd = 1 # rotate right
                else:
                    dd = -1
                direction = (self.direction + dd) % len(Turtle.Directions)
                intcode9.trace("<< ROTATE {} {} = {}".format(Turtle.DirectionNames[self.direction], ["left","right"][value], Turtle.DirectionNames[direction]))
                self.direction = direction
                pos = tuple(c+s for c,s in zip(self.pos, Turtle.Directions[direction]))
                intcode9.trace("<< MOVE {} from {} to {}".format(Turtle.DirectionNames[self.direction], self.pos, pos))
                self.pos = pos

            
        intcode9.getInput = localGetInput
        intcode9.writeOutput = localWriteOutput

        self.ipc = intcode9.makeIntcodeProcessor()

    def execute(self, program):
        self.ipc.execute(program)

    def totalPainted(self):
        return len(self.written)

    def toString(self, showTurtle = False):
        minx = min(k[0] for k in self.field.keys())
        maxx = max(k[0] for k in self.field.keys())
        miny = min(k[1] for k in self.field.keys())
        maxy = max(k[1] for k in self.field.keys())

        def sym(pos):
            nonlocal self
            nonlocal showTurtle
            if showTurtle and pos == self.pos:
                return Turtle.DirectionSymbols[self.direction]
            return ['.', '#'][self.field[pos]]

        rows=[''.join([sym((x,y)) for x in range(minx, maxx+1)]) for y in range(miny, maxy+1)]
        return '\n'.join(rows)

#       rows = []
#       for y in range(miny, maxy+1):
#           row = [sym((x,y)) for x in range(minx, maxx+1)]
#           rows.append(row)

import sys
if __name__=='__main__':
    if len(sys.argv) > 2 and sys.argv[2] == '-v':
        intcode9.TRACE=1

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

    initial = 0
    if len(sys.argv) > 2 and sys.argv[2] == '--part2':
        initial = 1

    turtle = Turtle(initial)
    turtle.execute(inprog)
    print("painted {} panels (at least once)".format(turtle.totalPainted()))

    if initial:
        print(" --- final state --- ")
        print(turtle.toString(True))


