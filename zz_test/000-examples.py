# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Examples
#
# This is a collection of examples and illustrations of Text-Fabric in general

# %load_ext autoreload
# %autoreload 2

from tf.app import use

# # Type levels
#
# When Text-Fabric precomputes corpus data, it ranks the node types according to the average size of nodes of that type.
#
# The *size* of a node is the size of the set of slots attached to that node.
# Slots are attached to nodes by means of the `oslots` feature, which is a standard part of each TF data set.
#
# From within Text-Fabric, we can ask for this ranking, by means of
#
# * `C.levels.data`: inspecting the precomputed data
# * `F.otype.all`: the resulting node types
# * `N.otypeRank`: the resulting ranking
#
# We load the BHSA and Uruk
# ([here](https://annotation.github.io/text-fabric/tf/about/corpora.html) is more info on these corpora)
# and have a look at their node type ranking.

As = {}

for corpus in ("bhsa", "uruk"):
    print(f"Loading {corpus} ...")
    As[corpus] = use(f"{corpus}:clone", silent="deep")
    As[corpus].info("done")


# We have loaded both datasets.
#
# We want to be able to put them into the foreground, i.e. make it so that the global variables `A N F E L T S C TF` become bound to the
# forground data set. We write a function for that.


def foreground(corpus, hoist):
    thisA = As[corpus]
    hoist["A"] = thisA
    thisTf = thisA.TF
    thisTf.makeAvailableIn(hoist)
    thisA.showContext("corpus")


foreground("bhsa", globals())

foreground("uruk", globals())

# That works.
#
# Back to the BHSA!

foreground("bhsa", globals())

C.levels.data

# The second column is the average length of nodes in slots.

# Here you see just the types, in the same order:

F.otype.all

# And here are the ranks:

N.otypeRank

# Now the same for oldbabylonian:

foreground("uruk", globals())

C.levels.data

F.otype.all

# And here are the ranks:

N.otypeRank

# Note that `cluster` is ranked higher than `quad` although `cluster` is smaller than `quad` on average.
#
# This is what we want, and we have achieved it by specifying this order under the `@levels` key in the
# [otext](https://github.com/Nino-cunei/uruk/blob/51f495fbaa94e4faa9f7dc06482548dfdf10bd87/tf/uruk/1.0/otext.tf#L10)
# feature of this dataset.

# # Relevance for display
#
# When we display, we want to display smaller nodes inside bigger nodes.
#
# In the BHSA, sentences are bigger than clauses.
#
# But what if a sentence happens to be exactly as big as its only clause?
#
# We want to guarantee that even then the clause is displayed in the sentence, and not the other way around.

foreground("bhsa", globals())

query = """
sentence
    := clause
    =:
"""
results = A.search(query)

s = results[0][0]
F.otype.v(s)

A.pretty(s)
