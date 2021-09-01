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
# # Load
#
# This notebook shows you how to load a work into Text-Fabric.
# See [start](start.ipynb) for preliminaries.
#
# ## About
#
# Ernst Boogert, while at the [PThU](https://www.pthu.nl/en/) has mass-converted Greek Literature from
# high quality libraries such as Perseus to the Text-Fabric format.
#
# He has delivered the outcome to the [greek_literature](https://github.com/pthu/greek_literature) repository on GitHub.
#
# It consists of nearly 1800 works by over 250 authors.

# %load_ext autoreload
# %autoreload 2

from tf.app import use
from catalog import makeCatalog, ORG, REPO, VERSION

# # Selection
#
# We use the catalog (see [start](start.ipynb) ) to pick a work.

works = makeCatalog()

# The catalog is a dict of authors, and for each author a dict of hist titles.
#
# Let's have a look at the first 12 authors:

sorted(works)[0:12]

# We pick a work by Aesop.

# +
AUTHOR = "Aeschylus"

works[AUTHOR]

# +
TITLE = "Eumenides"

dataSource = works[AUTHOR][TITLE][0]

dataSource
# -

# ## Use
#
# With the location of the dataset in hand, we can load the text into Text-Fabric:

A = use(f"{ORG}/{REPO}/{dataSource}:clone", version=VERSION, hoist=globals())

# ## Explanation:
#
# The first argument of `use()` is `f"{ORG}/{REPO}/{dataSource}:clone"`.
#
# This string specifies which dataset to use.
#
# For some [corpora](https://annotation.github.io/text-fabric/tf/about/corpora.html),
# such as the Hebrew Bible, there is a Text-Fabric app, and we can just mention the name of the app,
# e.g. `bhsa` for the Hebrew Bible.
#
# For corpora without app, we have to specify a location on your local computer or on GitHub from
# which the data can be fetched.
#
# Text-Fabric knows that we specify a location instead of an app if there is a `/` somewhere in the string.
#
# Text-Fabric knows that we specify a location on GitHub, because there is a `:` near the end of the name.
#
# In this case we specify a GitHub location, which is `pthu/greek_literature/First1KGreek/tlg0096/tlg002/First1K-grc1/1/tf`.
#
# The specifier `:clone` means: locate it in the clone of this repo on your local computer.
# If we had specified `:hot`, Text-Fabric would have downloaded the latest commit straight from the online GitHub.
#
#
# ### Use corpora without cloning repos
#
# If you know the location of a work of interest on github, you can use the `:hot` variant to download
# the corpus data on-the-fly, without any need to clone the whole repository beforehand.
#
# ## Versions
#
# There is also the `version=VERSION` argument.
#
# Ernst Boogert has delivered all these corpora as version `1.0`.
# When Text-Fabric is instructed to find `.tf` files somewhere, and it is given a version, it will look for
# a subdirectory named as that version, and get the actual files from there.
#
# Later, when Ernst has made some improvements, he can make an new version, and we can use that to retrieve the new files.
# We only have to pass `version="2.0"` or something like that.
#
# ## Information
#
# If you expand the little triangle before `pthu/greek_literature ...`, you'll get a list of features
# that are loaded.
# If you need to know what they mean, consult the
# [repo](https://github.com/pthu/greek_literature)
# where all this data resides.
#
# At the moment, there is very little documentation there, Ernst and/or I hope to write docs soon.
#
# But even without documentation we can do quite a bit, as we shall see in one of the next chapters:
# [compute](compute.ipynb).

# # Text-Fabric browser
#
# Text-Fabric comes with an off-line webinterface by which you can inspect your corpus.
#
# You can start it from the command line:

# !text-fabric pthu/greek_literature/{dataSource}:clone --version=1.0

# # All steps
#
# * **[start](start.ipynb)** catalogue of Greek Literature
# * **load** load a Greek work
# * (later) ~[display](display.ipynb)~ create pretty displays of your text structures
# * **[compute](compute.ipynb)** compute with text and features
# * (later) ~[search](search.ipynb)~ turbo charge your hand-coding with search templates
# * (later) ~[exportExcel](exportExcel.ipynb)~ make tailor-made spreadsheets out of your results
# * (later) ~[share](share.ipynb)~ draw in other people's data and let them use yours
#
# CC-BY Ernst Boogert, Dirk Roorda
