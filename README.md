# mazebook
Maze-generation code based on the book Mazes for Programmers by Jamis Buck

This is the code I wrote while reading Jamis Buck's book "Mazes for Programmers".  None of his code is used directly.
In addition to writing in Python and PostScript instead of Ruby, I made a number of different choices as to how to
represent spaces.  The polygonal grids and complex maze code are original to me but feel free to reimplement them.

The maze generation code is pure Python but most output is via PostScript - to use this code you will need to have
ghostscript, perl, and the netpbm utilities installed and in your path.  This library includes much of the code in
my own dmmlib library, so it is not necessary to download that separately.

## Usage
`make_maze.py` is a command-line executable that will generate mazes in a variety of ways.  You can also use the libraries directly.

`./make_maze.py heart:10 -wf -o png -n heart -s 10`

![colorful heart-shaped maze](/images/heart.png)

### grid types
### maze algorithms
### printing methods
