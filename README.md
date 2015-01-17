wikipedia_network_analysis
==========================

Statistical Network Analysis of the Field of Statistics on Wikipedia In English

![Main statistical categories visualization](https://github.com/Framartin/wikipedia_network_analysis/blob/master/images/categories2.png)

## Introduction

The Python script, which extracts edges of our graphs, is inspired by the great brianckeegan's Wikipedia-Network-Analysis python notebook available on [github](https://github.com/brianckeegan/Wikipedia-Network-Analysis) under MIT license.

## Data

We build a directed graph using links between Wikipedia articles related to the specific field of Statistics (but you can quite easily change it if you want).

We have two solutions to get pages related to Statistics :

1. Using [Category:Statistics](http://en.wikipedia.org/wiki/Category:Statistics)
2. Using lists of articles about statistics ([List_of_statistics_articles](https://en.wikipedia.org/wiki/List_of_statistics_articles) and [Outline_of_statistics](https://en.wikipedia.org/wiki/Outline_of_statistics)) featured in the [Portal:Statistics](https://en.wikipedia.org/wiki/Portal:Statistics)

See `Extract_links_from_API.py` for more details. We strongly recommend using the second solution.

- Data, available in `edges1.csv` and `vertex1.csv` files, was extracted the 30/12/2014 using the first solution.
- Data, available in `edges2.csv` and `vertex2.csv` files, was extracted the 27/12/2014 using the second solution.

If you want to update this data, please [donate to Wikimedia](https://donate.wikimedia.org), because this operation is quite resource consuming for the [MediaWiki API](https://www.mediawiki.org/wiki/API:Main_page).

## Warnings

Please consider the following problem pointed out by [brianckeegan](https://github.com/brianckeegan/Wikipedia-Network-Analysis) :

> Wikipedia article also contain templates (https://en.wikipedia.org/wiki/Help:Template) which creates lots of "redundant" links between articles that share templates even those these links don't appear in the body of the article itself. You'll need to do much more advanced text parsing of wiki-markup to actually get links in the body of an article

## Requirements

* Python 2.7
* [`Anaconda`](http://continuum.io/downloads)
* [`wikitools`](https://pypi.python.org/pypi/wikitools) which you can install with pip : `pip install wikitools`
* `R` and its package `igraph`

## License

The Python and R scripts are under MIT License.
