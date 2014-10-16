Getting To Philosophy
====================

Description
-----------

Python script which repeatedly requests random pages from Wikipedia, and generates a graph of their path (if one exists) back to the Philosophy Wikipedia page.

This project is a fork of [David Muller's getting_to_philosophy](https://github.com/DavidMuller/getting_to_philosophy), allowing me to re-use his code for getting the first non-italisicised link in a Wikipedia page.

Inspiration
-----------

[XKCD](http://xkcd.com/903/)

Todo
----
+ Optimize to check for an existing path from current node to end node when making hops
+ Generate some statistics
    - Average number of hops
    - Minimum number of hops
    - Maximum number of hop
    - Common convergence points
    - Percentage of pages for which a path was not found

Requirements
------------

+ BeautifulSoup4
+ GraphViz | pip install pygraphviz
