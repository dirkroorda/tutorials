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
# # Compute
#
# This notebook shows you how to compute with your corpus in Text-Fabric.
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
# We pick the same work as in [load](load.ipynb).

# +
AUTHOR = "Aeschylus"
TITLE = "Eumenides"

works = makeCatalog()
dataSource = works[AUTHOR][TITLE][0]

dataSource
# -

# # Loading
#
# We load the Eumenides:

A = use(f"{ORG}/{REPO}/{dataSource}:clone", version=VERSION, hoist=globals())

# # Exploring
#
# Every TF corpus has an atomic type, the type of the textual `slots`.
#
# We can read it off from the dataset by means of the TF API (see
# [cheatsheet](https://annotation.github.io/text-fabric/tf/cheatsheet.html) ).
#
# We can also find out the number of slots.

F.otype.slotType

F.otype.maxSlot

# This is a small text, only 5629 words.
#
# Now let's see what features we have:

Fall()

# I suspect the actual text is in the feature `orig`.
#
# We can get a bit more information by looking at the metadata:

F.orig.meta

# Indeed. And the [betacode](https://en.wikipedia.org/wiki/Beta_Code)
# representation could be in feature `plain`.

F.plain.meta["description"]

# We call up the `orig` and `plain` features of the second word.

F.orig.v(1)

F.plain.v(1)

# OK, `plain` is not betacode, but accentless greek.

# There is additional configuration in the dataset, coming from feature `otext.tf` (which only has metadata, no data).
#
# That information is about text formats and sections.

T.formats

T.sectionTypes

# We see that we have three ways to represent text.
#
# And the corpus is divided into *cards*, and then in *strophes*, and then in *ephymns*.
#
# Let's pick the first strophe:

s = F.otype.s("strophe")[0]
s

# We get a number. All things in the corpus, words, strophes, cards, etc. are represented by nodes, and nodes are just numbers.
# Treat them as bar codes: you have them, but you do not read them, and you do not remember them. Text-Fabric is your bar code reader.

# Now we display the text of this strophe:

T.text(s)

# And now in all three formats:

for fmt in T.formats:
    print(f"{F.otype.v(s)} {F.strophe.v(s)} in format {fmt}")
    print(T.text(s, fmt=fmt))
    print("")

# We can ask for a frequency distribution of the values of an arbitrary feature.
# Now let's ask for the distribution of the `plain` feature. That will give us a nice frequency list of the
# words in this corpus.
#
# We print the top 20:

F.plain.freqList()[0:20]

# How many strophes are there?

len(F.otype.s("strophe"))

# Here is strophe 36:

s = F.otype.s("strophe")[35]
T.text(s)

# Here is word 5001

w = F.otype.s("word")[5000]
T.text(w)

# Where is it?

T.sectionFromNode(w)

# It is in card 881, in a strophe with number 0, in an ephymn with number 0.
#
# We can get the nodes of these sections:

T.sectionTuple(w)

# Lets print the strophe (the middle element)

s = T.sectionTuple(w)[1]
T.text(s)

# The first slot and the last slot in this strophe are:

words = L.d(s, otype="word")
print(words[0])
print(words[-1])

# We can display this strophe in a prettier way:

A.pretty(s, full=True)

# # All steps
#
# * **[start](start.ipynb)** catalogue of Greek Literature
# * **[load](load.ipynb)** load a Greek work
# * (later) ~[display](display.ipynb)~ create pretty displays of your text structures
# * **compute** compute with text and features
# * (later) ~[search](search.ipynb)~ turbo charge your hand-coding with search templates
# * (later) ~[exportExcel](exportExcel.ipynb)~ make tailor-made spreadsheets out of your results
# * (later) ~[share](share.ipynb)~ draw in other people's data and let them use yours
#
# CC-BY Ernst Boogert, Dirk Roorda
