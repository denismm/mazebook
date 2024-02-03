# mazebook
Maze-generation code based on the book Mazes for Programmers by Jamis Buck

This is the code I wrote while reading Jamis Buck's book "Mazes for
Programmers".  None of his code is used directly.  In addition to writing
in Python and PostScript instead of Ruby, I made a number of different
choices as to how to represent spaces.  The polygonal grids and complex
maze code are original to me but feel free to reimplement them.

The maze generation code is pure Python but most output is via PostScript.
To use this code you will need to have python3, gs, perl, and the netpbm
utilities installed and in your path.  This library includes much of the
code in my own dmmlib library, so it is not necessary to download that
separately.

## Usage
`make_maze.py` is a command-line executable that will generate mazes in a
variety of ways.  You can also use the libraries directly.

`./make_maze.py heart:10 -wf -o png -n heart -s 10`

![colorful heart-shaped maze](/images/heart.png)

## grid types

### maze.rectgrid: rectangular grids

These are grids with square or nearly-square cells that have neighbors in the
traditional cardinal directions.

* RectGrid: normal square grid with orthogonal connections.  Specified as HxW or HxWg, as in "10x10".  If a mask is provided, the grid will be a RectGrid the size of the mask.
* ZetaGrid: like RectGrid but adds diagonal connections. Specified as HxWz.
* UpsilonGrid: like RectGrid but adds a diamond-shaped cell at each vertex, so half of the cells are octagons connecting in 8 directions and the other half are diamonds connecting in only the diagonal directions.  Specified as HxWu.

### maze.hexgrid: triangular and hexagonal grids

These are grids with triangular geometry in some way.  (https://www.redblobgames.com/grids/hexagons/) was a very useful resource in coding this section.

* HexGrid: a hexagonal grid, with connections in 6 directions. The cells are oriented with a flat top, and the entire grid has the shape of a pointy-topped hexagon.  Specified as Rd, where R is the radius from the center hex (not inclusive), as in "5s" which will create a grid 11 hexes across at the widest points.
* TriGrid: a triagonal grid, with connections in 3 directions.  The cells are upward-pointing and downward-pointing triangles, and the entire grid has the shape of an upward-pointing triangle.  Specified as Wd, where W is the length of one side of the grid, as in "7d".

### maze.circlegrid: circular and regular-polygonal grids

These are grids that radiate out from a central point which may be a cell or
an intersection.  Most cells have 4 or 5 neighbors - one inward, one to the
clockwise and counterclockwise direction, and either one or two outward
as the number of cells in a ring occasionally doubles to keep the cells
as square as possible.  If there's a center cell, it will have every cell
in the first ring as a neighbor.

* CircleGrid: a circular grid where the central cell is circular and all other cells are annular sectors.  Specified as "R@" or "Ro", where @ means a central cell and o means no central cell and R is the radius, not including the central cell if present, as in "5o".
* PolygonGrid: a grid the shape of a regular polygon where the central cell is the shape of the full grid and all other cells are trapezoids.  Specified as "R@S" or "RoS", where @ means a central cell and o means no central cell, R is the radius, and S is the number of sides of the grid, as in "8@7".
* SemiCircleGrid: a special case of circular grid that only include 180 degrees of the circle, providing a flat side.  Not available directly through make_maze but useful in complex grids.

Relevant arguments:
* `firstring`: how many cells to put in the first ring (ignoring the central cell).  If not specified for circular grids, it will end up as 6 if there is a central cell and 3 if not.  If not specified for polygonal grids, it defaults to the number of sides.
* `degrees`: how much of the circle or polygon to actually include, out of 360 degrees.  Strange behavior may result if the firstring value doesn't evenly divide the available angles.
* `slices`: how much of the polygon to include, from 1 to the number of sides.

### maze.complex_maze: complex grids assembled from subgrids

These are grids made of simpler grids stitched together.  Only the following grids can be used in complex grids:
* RectGrid
* TriGrid
* PolygonGrid
* SemiCircleGrid

Only the following complex mazes can be used directly from make_maze, specified as "N:S" where N is the name of the complex grid and S is the size of some internal edge, as in "slender_star:9":
* slender_star: a five-pointed star with collinear edges
* fat_star: a five-pointed star with shorter edges
* cube: an unfolded cube
* heart: a heart, consisting of a square connected to two semicircles

## maze algorithms

- `-a', `--algorithm`: maze algorithm to use.  Not all algorithms are available for all grids.
  - aldous_broder
  - wilson
  - hunt_kill
  - backtrack
  - kruskal
  - simple_prim
  - true_prim
  - random_tree
  - last_tree
  - half_tree
  - first_tree
  - median_tree
  - eller (RectGrid, CircleGrid, PolygonGrid only)
  - fractal (RectGrid, CircleGrid, PolygonGrid only)
  - binary (RectGrid only)
  - sidewinder (RectGrid only)

- -s --seed
- -f --field
- -p --path
- -w --weave
- -b --braid
- --room_size
- -y --hyper

## printing methods

* -o --output
* -n --name
* --inset
* --linewidth
* --bg
* --pathcolor
* --pixels
* --noflat

## incompatible combinations
