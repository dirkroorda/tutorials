# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: Python3.9
#     language: python
#     name: python3
# ---

# <img src="images/pthu.png"/>
# <img align="right" src="images/tf-small.png" width="128"/>
# <img align="right" src="images/dans-small.png"/>
#
# # Tutorial
#
# This notebook gets you started with using
# [Text-Fabric](https://annotation.github.io/text-fabric/) for coding in the Greek Literature.
#
# ## About
#
# Ernst Boogert, while at the [PThU](https://www.pthu.nl/en/) has mass-converted Greek Literature from
# high quality libraries such as Perseus to the Text-Fabric format.
#
# He has delivered the outcome to the [greek_literature](https://github.com/pthu/greek_literature) repository on GitHub.
#
# It consists of nearly 1800 works by over 250 authors.
#
# ## Catalog
#
# At first sight, it is not easy to see what is in this repo.
# So we make a catalog and show the results.
#
# In this notebook we show how you can make an inventory by coding some functions in Python.
# We also have written a small library, `catalog.py` that contains catalog functions, so that we can
# easily use the catalog in other notebooks.

# Our catalog functions make use of pretty low-level Text-Fabric stuff.
#
# Do not let this deter you. Later, when we are using Text-Fabric for individual works, we use a much more high-level interface to
# Text-Fabric.
#
# We also use a pretty-printer of Python datastructures: `pprint`.

# +
import os
import collections
import pprint as pp

from tf.core.timestamp import Timestamp
from tf.core.data import Data, WARP

PP = pp.PrettyPrinter(indent=2)


def pprint(x):
    PP.pprint(x)


# -

# ## Clone the repo
#
# Make sure you have cloned the Greek Literature repository to your computer.
#
# I assume that you have created a directory `github` in your home directory, and under that a directory `pthu`.
#
# <img align="right" src="images/github.png" width="400"/>
#
# ### novice way
#
# If you have never used `git`, use the following procedure:
#
# 1. go to [greek_literature](https://github.com/pthu/greek_literature) and locate the green `code` button.
# 1. click the little triangle and then click `Download ZIP`.
# 1. go to your `Downloads` folder and locate the file `greek_literature-master.zip`
#    (it may take a while before the file has arrived, because it is 450 MB)
# 1. unzip the result, it will be a directory `greek_literature-master`
#    with a size of nearly 2GB and 45,000 files in it.
# 1. move this directory straight under the `github/pthu` directory you have created before
# 1. rename this directory to `greek_literature`
#
# ### expert way
#
# If you are comfortable with `git` and have it already installed on your computer, you can proceed like this:
#
# On the command line, go to the directory `~/github/pthu`, and say
#
# ```
# git clone https://github.com/pthu/greek_literature
# ```
#
# After that you have all works in Greek Literature stored on your computer.

# By means of a few definitions we tell our functions where the data is.

BASE = os.path.expanduser("~/github")
ORG = "pthu"
REPO = "greek_literature"
REPO_PATH = f"{BASE}/{ORG}/{REPO}"
VERSION = "1.0"


# The next function collects all `tf` directories that can be found somewhere below a base directory.


def collectTfDirs(path, result):
    """Collect TF directories.

    Collect all directories named `tf` that are somewhere below `path` and add
    the path names of those directories to the list `result`.

    Note: we strip the initial part that is common to all result paths.
    """

    with os.scandir(path) as it:
        for entry in it:
            name = entry.name
            if not name.startswith(".") and entry.is_dir():
                subPath = f"{path}/{name}"
                if name == "tf":
                    result.append(subPath.removeprefix(f"{REPO_PATH}/"))
                else:
                    collectTfDirs(subPath, result)


# +
tfDirs = []

collectTfDirs(REPO_PATH, tfDirs)

len(tfDirs)
# -

# Here are a few of the paths that we have found.

pprint(tfDirs[0:10])
print("")
pprint(tfDirs[100:110])
print("")
pprint(tfDirs[1000:1010])
print("")
pprint(tfDirs[-10:])

# In order to get the authors and titles of the works, we load a single feature of each
# `tf` directory and inspect its metadata.
#
# The feature in question is called `otype`, it is present in all Text-Fabric datasets.
# See [data model](https://annotation.github.io/text-fabric/tf/about/datamodel.html) for more info on this.

tmObj = Timestamp()
OTYPE = WARP[0]


# The following function gives us the metadata of the `otype` feature.


def getMeta(tfDir):
    """Load the otype function of a TF dataset and deliver its metadata."""

    otypePath = f"{REPO_PATH}/{tfDir}/{VERSION}/{OTYPE}.tf"
    dataObj = Data(otypePath, tmObj)
    dataObj.load(metaOnly=True, silent=True)
    return dataObj.metaData


# We print out the metadata of the first, last and an intermediate dataset.
#
# We also print out the number of authors.
# Scroll down to the bottom in order to view it.

pprint(getMeta(tfDirs[0]))
pprint(getMeta(tfDirs[1000]))
pprint(getMeta(tfDirs[-1]))


# We now make a catalog based on author and title of the works.


def getCatalog(tfDirs):
    """Given a list of TF datasets, make a catalog of them.

    The catalog is first by author, then by title.
    """

    works = collections.defaultdict(list)

    for tfDir in tfDirs:
        meta = getMeta(tfDir)
        author = meta.get("author", "")
        title = meta.get("title", "")
        works[author].append(title)

    return works


works = getCatalog(tfDirs)
pprint(works)
print(f"{len(works)} authors")

# # All steps
#
# By now you have an impression of what to find in the Greek Literature.
# The next step is to pick and choose works and start computing with them in the Text-Fabric way.
#
# * **start** catalogue of Greek Literature
# * **[load](load.ipynb)** load a Greek work
# * (later) ~[display](display.ipynb)~ create pretty displays of your text structures
# * **[compute](compute.ipynb)** compute with text and features
# * (later) ~[search](search.ipynb)~ turbo charge your hand-coding with search templates
# * (later) ~[exportExcel](exportExcel.ipynb)~ make tailor-made spreadsheets out of your results
# * (later) ~[share](share.ipynb)~ draw in other people's data and let them use yours
#
# CC-BY Ernst Boogert, Dirk Roorda
