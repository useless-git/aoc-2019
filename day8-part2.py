"""
--- Part Two ---

Now you're ready to decode the image. The image is rendered by stacking the layers and aligning the pixels with the same positions in each layer. The digits indicate the color of the corresponding pixel: 0 is black, 1 is white, and 2 is transparent.

The layers are rendered with the first layer in front and the last layer in back. So, if a given position has a transparent pixel in the first and second layers, a black pixel in the third layer, and a white pixel in the fourth layer, the final image would have a black pixel at that position.

For example, given an image 2 pixels wide and 2 pixels tall, the image data 0222112222120000 corresponds to the following image layers:

Layer 1: 02
         22

Layer 2: 11
         22

Layer 3: 22
         12

Layer 4: 00
         00

Then, the full image can be found by determining the top visible pixel in each position:

    The top-left pixel is black because the top layer is 0.
    The top-right pixel is white because the top layer is 2 (transparent), but the second layer is 1.
    The bottom-left pixel is white because the top two layers are 2, but the third layer is 1.
    The bottom-right pixel is black because the only visible pixel in that position is 0 (from layer 4).

So, the final image looks like this:

01
10

What message is produced after decoding your image?
"""

import itertools

def layerSplit(width, height, digits):
    """
    >>> layerSplit(3, 2, [1,2,3,4,5,6,7,8,9,0,1,2])
    [[1, 2, 3, 4, 5, 6], [7, 8, 9, 0, 1, 2]]
    """
    layersize = width * height
    return [digits[start:start+layersize] for start in range(0, len(digits), layersize)]

def checksum(width, height, digits):
    layers = layerSplit(width, height, digits)
    count_zero = sorted(layers, key=lambda l:sum((1 if x==0 else 0 for x in l)))
    l = count_zero[0] # layer with fewest zeroes
    return sum((1 if x==1 else 0 for x in l)) * sum((1 if x==2 else 0 for x in l))

def flattenPixel(pixel_layers):
    for pl in itertools.dropwhile(lambda pl:pl == 2, pixel_layers):
        if pl == 0:
            return ' ' # black
        else:
            return '#' # white
    return pixel_layers[-1]

def flattenLayers(layers):
    return [flattenPixel(pl) for pl in zip(*layers)]

def rasterizeLayer(width, height, layer):
    """
    >>> print(rasterizeLayer(3, 2, [1, 2, 3, 4, 5, 6]))
    123
    456
    """
    rows = [''.join((str(p) for p in layer[start:start+width])) for start in range(0, height*width, width)]
    return '\n'.join(rows)

if __name__=='__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        import doctest
        doctest.testmod()
        sys.exit(0)

    if len(sys.argv) <2:
        print("Syntax: {} <program file> [--test]".format(sys.argv[0]))
        sys.exit(0)

    with open(sys.argv[1], 'r') as digfile:
        raw_digits = digfile.read()
        digits = [int(d) for d in raw_digits.strip()]
        layers = layerSplit(25,6,digits)
        flat = flattenLayers(layers)
        raster = rasterizeLayer(25, 6, flat)
        print(raster)

