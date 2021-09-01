# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# <img align="right" src="images/tf-small.png" width="128"/>
# <img align="right" src="images/etcbc.png"/>
# <img align="right" src="images/dans-small.png"/>
#
# # Tutorial
#
# This notebook gets you started with using
# [Text-Fabric](https://annotation.github.io/text-fabric/) for coding in the Hebrew Bible.
#
# If you are totally new to Text-Fabric, it might be helpful to read about the underlying
# [data model](https://annotation.github.io/text-fabric/tf/about/datamodel.html) first.
#
# Short introductions to other TF datasets:
#
# * [Dead Sea Scrolls](https://nbviewer.jupyter.org/github/annotation/tutorials/blob/master/lorentz2020/dss.ipynb),
# * [Old Babylonian Letters](https://nbviewer.jupyter.org/github/annotation/tutorials/blob/master/lorentz2020/oldbabylonian.ipynb),
# or the
# * [Q'uran](https://nbviewer.jupyter.org/github/annotation/tutorials/blob/master/lorentz2020/quran.ipynb)
#

# # Export to Excel
#
# In a notebook, you can perform searches and view them in a tabular display and zoom in on items with
# pretty displays.
#
# But there are times that you want to take your results outside Text-Fabric, outside a notebook, outside Python, and just
# work with them in other programs, such as Excel.
#
# You want to do that not only with query results, but with all kinds of lists of tuples of nodes.
#
# There is a function for that, `A.export()`, and here we show what it can do.

# %load_ext autoreload
# %autoreload 2

# # Incantation
#
# The ins and outs of installing Text-Fabric, getting the corpus, and initializing a notebook are
# explained in the [start tutorial](start.ipynb).

import os
from tf.app import use

A = use('bhsa', hoist=globals())
# A = use("bhsa:clone", checkout="clone", hoist=globals())

# # Inspect the contents of a file
# We write a function that can peek into file on your system, and show the first few lines.
# We'll use it to inspect the exported files that we are going to produce.

# +
EXPORT_FILE = os.path.expanduser("~/Downloads/results.tsv")
UPTO = 10


def checkout():
    with open(EXPORT_FILE, encoding="utf_16") as fh:
        for (i, line) in enumerate(fh):
            if i >= UPTO:
                break
            print(line)


# -

# # Encoding
#
# Our exported `.tsv` files open in Excel without hassle, even if they contain non-latin characters.
# That is because TF writes such files in an
# encoding that works well with Excel: `utf_16_le`.
# You can just open them in Excel, there is no need for conversion before or after opening these files.
#
# Should you want to process these files by means of a (Python) program,
# take care to read them with encoding `utf_16`.

# # Example query
#
# We first run a query in order to export the results.

query = """
book book=Samuel_I
  clause
    word sp=nmpr
"""
results = A.search(query)

# # Bare export
#
# You can export the table of results to Excel.
#
# The following command writes a tab-separated file `results.tsv` to your downloads directory.
#
# You can specify arguments `toDir=directory` and `toFile=file name` to write to a different file.
# If the directory does not exist, it will be created.
#
# We stick to the default, however.

A.export(results)

# Check out the contents:

checkout()

# You see the following columns:
#
# * **R** the sequence number of the result tuple in the result list
# * **S1 S2 S3** the section as book, chapter, verse, in separate columns
# * **NODEi TYPEi** the node and its type, for each node **i** in the result tuple
# * **TEXTi** the full text of node **i**, if the node type admits a concise text representation
# * **sp3** the value of feature **3**, since our query mentions the feature `sp` on node 3

# # Richer exports
#
# If we want to see the clause type (feature `typ`) and the word gender (feature `gn`) as well, we must mention them
# in the query.
#
# We can do so as follows:

query = """
book book=Samuel_I
  clause typ*
    word sp=nmpr gn*
"""
results = A.search(query)

# The same number of results as before.
# The `*` is a trivial condition, it is always true.
#
# We do the export again and peek at the results.

A.export(results)
checkout()

# As you see, you have an extra column **typ2** and **gn3**.
#
# This gives you a lot of control over the generation of spreadsheets.

# # Not from queries
#
# You can also export lists of node tuples that are not obtained by a query:

# +
tuples = (
    tuple(results[0][1:3]),
    tuple(results[1][1:3]),
)

tuples
# -

# Two rows, each row has a clause node and a word node.
#
# Let's do a bare export:

A.export(tuples)
checkout()

# Wait a minute: why is the `typ2` there?
#
# It is because we have run a query before where we asked for `typ`.
#
# If we do not want to be influenced by previous things we've run, we need to reset the display:

A.displayReset("tupleFeatures")

# Again:

A.export(tuples)
checkout()

# # Display setup
#
# We can get richer exports by means of
# `A.displaySetup()`, using the parameter `tupleFeatures`:

A.displaySetup(
    tupleFeatures=(
        (0, "typ rela"),
        (1, "sp gn nu pdp"),
    )
)

# We assign extra features per member of the tuple.
#
# In the above case:
#
# * the first (`0`) member (the clause node), gets feature `typ`;
# * the second (`1`) member (the word node), gets features `sp` and `gn`.

A.export(tuples)
checkout()

# Talking about display setup: other parameters also have effect, e.g. the text format.
#
# Let's change it to the phonetic representation.

A.export(tuples, fmt="text-phono-full")
checkout()

# # Chained queries
#
# You can chain queries like this:

results = (
    A.search(
        """
book book=Samuel_I
  chapter chapter=1
    verse verse=1
      clause
        word sp=nmpr
"""
    )
    + A.search(
        """
book book=Samuel_I
  chapter chapter=1
    verse verse=1
      clause
        word sp=verb nu=pl
"""
    )
)

# In such cases, it is better to setup the features yourself:

A.displaySetup(
    tupleFeatures=(
        (3, "typ rela"),
        (4, "sp gn vt vs"),
    ),
    fmt="text-phono-full",
)

# Now we can do a fine export:

A.export(results)
checkout()

# # All steps
#
# Now you now how to escape from Text-Fabric.
#
# We hope that this makes your stay in TF more comfortable.
# It's not a *Hotel California*.
#
# * **[start](start.ipynb)** your first step in mastering the bible computationally
# * **[display](display.ipynb)** become an expert in creating pretty displays of your text structures
# * **[search](search.ipynb)** turbo charge your hand-coding with search templates
# * **exportExcel** make tailor-made spreadsheets out of your results
# * **[share](share.ipynb)** draw in other people's data and let them use yours
# * **[export](export.ipynb)** export your dataset as an Emdros database
# * **[annotate](annotate.ipynb)** annotate plain text by means of other tools and import the annotations as TF features
# * **[volumes](volumes.ipynb)** work with selected books only
# * **[trees](trees.ipynb)** work with the BHSA data as syntax trees
#
# CC-BY Dirk Roorda
