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

# %load_ext autoreload
# %autoreload 2

from tf.app import use

# # Cluster display in Old Babylonian
#
# We show some details of the display logic by following an example: cluster nodes in the Old Babylonian corpus.
#
# Clusters are difficult, because
#
# * they do not necessarily respect proper embedding
# * material can be part of several clusters
#
# We show how we deal with the second part and prevent multiple display of members of multiple clusters.
# As an illustration, we'll show the effect of an earlier bug and indicate the fix.
#
# We start with loading the corpus.

A = use("oldbabylonian:clone", checkout="clone", hoist=globals())

A.reuse()

# # An example line
#
# Here is a line with some nested clusters.
# In fact, it is the first line of the corpus.
#
# The node number is stored in the variable `ln`.
#
# We show the raw ATF source of the line, and the text according to several text formats.

ln = F.otype.s("line")[0]
ln

F.srcLn.v(ln)

T.text(ln)

T.text(ln, fmt="text-orig-rich")

T.text(ln, fmt="text-orig-unicode")

# N.B: These are the right unicodes but not the right signs, we need another font for that.
#
# We can get the right signs by using `plain`:

A.plain(ln, fmt="text-orig-unicode")

# even better, we translate the effect of clusters into layout:

A.plain(ln, fmt="layout-orig-unicode")

# Click on the passage link in order to go to the page for this tablet on CDLI, where you can read off the
# exact source:
#
# ```
# 1. [a-na] _{d}suen_-i-[din-nam]
# ```

# ## The clusters
#
# By means of the
# [`L` API](https://annotation.github.io/text-fabric/tf/core/locality.html)
# the clusters of this line can be found.
#
# They are returned as a tuple of nodes.

cls = L.d(ln, otype="cluster")
cls

# We'll give each cluster its own highlight color:

# +
colors = """
    cyan
    yellow
    lightsalmon
    lightgreen
    goldenrod
    cornflowerblue
    forestgreen
    burlywood
    orange
    indianred
""".strip().split()

highlights = dict(zip(cls, colors))
highlights
# -

A.plain(ln, highlights=highlights)

# In this corpus, `pretty` displays unfold until the word level, by default.
#
# But first we want it to unfold to the very end, to the sign level.

A.pretty(ln, highlights=highlights, baseTypes="sign")


# Let's see some more examples.
# We have written a function to quickly execute examples.
# The first example is the index of the line in the list of all lines produces by `F.otype.s('line')`.


def example(nLine, extraHighlights={}, **options):
    ln = F.otype.s("line")[nLine]
    print(ln)
    print(F.srcLn.v(ln))
    print(T.text(ln))
    A.plain(ln, fmt="layout-orig-unicode")
    cls = L.d(ln, otype="cluster")
    highlights = dict(zip(cls, colors[0 : len(cls)]))
    print(highlights)
    A.plain(ln, highlights={**highlights, **extraHighlights}, **options)
    A.pretty(
        ln,
        highlights={**highlights, **extraHighlights},
        baseTypes="sign",
        **options,
        explain=True
    )
    A.pretty(ln, highlights={**highlights, **extraHighlights}, **options)


example(0, withNodes=True)

example(22, withNodes=True, extraHighlights={258252: "lightsalmon"})

# # More examples
#
# We finish off with some more examples.

# Something peculiar  is going on.
# In order to talk  about it, we add node numbers.

example(2553, withNodes=True, extraHighlights={265903: "lightsalmon"})

# # More cases

results = (
    (258201, 112),
    (258404, 591),
)

n = results[0][0]
A.pretty(n, highlights=set(results[0]), baseTypes="sign", withNodes=True, explain=False)

n = results[1][0]
A.pretty(n, highlights=set(results[1]), baseTypes="sign", withNodes=True, explain=False)

w = 260817
A.pretty(w, baseTypes="sign", explain=False)

ln = 231650
print(T.text(ln))
print(F.srcLn.v(ln))

A.plain(
    ln,
    withNodes=False,
    baseTypes="sign",
    explain=False,
    highlights={
        204104: "lightsalmon",
        204105: "yellow",
        204106: "lightgreen",
        204107: "lightblue",
    },
)
A.pretty(
    ln,
    withNodes=False,
    baseTypes="sign",
    explain=False,
    highlights={
        204104: "lightsalmon",
        204105: "yellow",
        204106: "lightgreen",
        204107: "lightblue",
    },
)

A.pretty(ln)

# # Developer's cells
#
#
# Use `A.reuse()` if you have changed the `config.yaml` of this corpus and want to reapply the settings.
#
# Inspect the result of the new settings by means of `A.showContext()`.

A.reuse()

A.showContext()
