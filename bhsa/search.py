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
# You might want to consider the [start](search.ipynb) of this tutorial.
#
# Short introductions to other TF datasets:
#
# * [Dead Sea Scrolls](https://nbviewer.jupyter.org/github/annotation/tutorials/blob/master/lorentz2020/dss.ipynb),
# * [Old Babylonian Letters](https://nbviewer.jupyter.org/github/annotation/tutorials/blob/master/lorentz2020/oldbabylonian.ipynb),
# or the
# * [Q'uran](https://nbviewer.jupyter.org/github/annotation/tutorials/blob/master/lorentz2020/quran.ipynb)
#

# # Search Introduction
#
# *Search* in Text-Fabric is a template based way of looking for structural patterns in your dataset.
#
# It is inspired by the idea of
# [topographic query](http://books.google.nl/books?id=9ggOBRz1dO4C),
# as worked out in
# [MQL](https://github.com/ETCBC/shebanq/wiki/Documents/MQL-Query-Guide.pdf)
# which has been implemented in
# [Emdros](http://emdros.org).
# See also [pitfalls of MQL](https://etcbc.github.io/bhsa/mql#pitfalls-of-mql)
#
# Within Text-Fabric we have the unique possibility to combine the ease of formulating search templates for
# complicated syntactical patterns with the power of programmatically processing the results.
#
# This notebook will show you how to get up and running.
#
# See the notebook
# [searchFromMQL](searchFromMQL.ipynb)
# for examples how MQL queries can be expressed in Text-Fabric search.
#
# ## Alternative for hand-coding
#
# Search is a powerful feature for a wide range of purposes.
#
# Quite a bit of the implementation work has been dedicated to optimize performance.
# Yet I do not pretend to have found optimal strategies for all
# possible search templates.
# Some search tasks may turn out to be somewhat costly or even very costly.
#
# That being said, I think search might turn out helpful in many cases,
# especially by reducing the amount of hand-coding needed to work with special subsets of your data.
#
# ## Easy command
#
# Search is as simple as saying (just an example)
#
# ```python
# results = A.search(template)
# A.show(results)
# ```
#
# See all ins and outs in the
# [search template docs](https://annotation.github.io/text-fabric/tf/about/searchusage.html).

# %load_ext autoreload
# %autoreload 2

# # Incantation
#
# The ins and outs of installing Text-Fabric, getting the corpus, and initializing a notebook are
# explained in the [start tutorial](start.ipynb).

from tf.app import use

A = use('bhsa', hoist=globals())
# A = use("bhsa:clone", checkout="clone", hoist=globals())

# # Basic search command
#
# We start with the most simple form of issuing a query.
# Let's look for the proper nouns in 1 Samuel.
# We also want to show the clauses in which they occur.
#
# All work involved in searching takes place under the hood.

query = """
book book=Samuel_I
  clause
    word sp=nmpr
"""
results = A.search(query)

# We have the results. We only need to display them. Here are the first few in a table:

A.table(results, end=3)

# The hyperlinks in the `p` column point to SHEBANQ, to the verse most relevant to the individual results.
#
# The columns with the book is not very informative. We can leave it out.
# You can leave columns out by passing `skipCols=xxx` where `xxx` is a set of numbers, which may also be passed as
# a space-separated string of numbers.
#
# Note that the book column is the first column (starting after the `p` column, coounting starts at 1).

A.table(results, end=10, skipCols="1")

# Here is the first one in a pretty display:

A.show(results, end=1)

# We are going to do some more work where we want to skip column 1, so we make that the temporary default:

A.displaySetup(skipCols="1")

# Now we show a few results without the book column:

A.show(results, end=2)

# or, stopping at the clause level:

A.show(results, end=2, baseTypes={"clause"})

# We can view result in phonetic representation as well:

A.table(results, end=3, fmt="text-phono-full")

A.show(results, end=1, fmt="text-phono-full")

# We are done with this query and its results. We reset the `skipCols` parameter.

A.displayReset("skipCols")

# # Condense results
#
# There are two fundamentally different ways of presenting the results: condensed and uncondensed.
#
# In **uncondensed** view, all results are listed individually.
# You can keep track of which parts belong to which results.
# The display can become unwieldy.
#
# This is the default view, because it is the straightest, most logical, answer to your query.
#
# In **condensed** view all nodes of all results are grouped in containers first (e.g. verses), and then presented
# container by container.
# You loose the information of what parts belong to what result.
#
# Here is an example of the difference.

query = """
book book=Genesis
  chapter chapter=1
    verse verse=1
      sentence
% order is not important!
        word nu=sg
        word nu=pl
"""

# Note that you can have comments in a search template. Comment lines start with a `%`.

results = A.search(query)

# The book, chapter, verse columns are completely uninformative, so:

A.displaySetup(skipCols="1 2 3")

A.table(results, withPassage=True)

# There are two plural and three singular words in Genesis 1:1.
# Search templates do not specify order, so all six combinations qualify as results.
#
# Let's expand the results display:

A.show(results)

# As you see, the results are listed per result tuple, even if they occur all in the same verse.
# This way you can keep track of what exactly belongs to each result.
#
# Now in condensed mode:

A.show(results, condensed=True)

# Here we have all words of all results in one display. But we cannot see that each results has two words, let alone which ones.

# # Custom highlighting
#
# Note that we can apply different highlight colors to different parts of the result.
# The words in the pair are member 5 and 6 of the result tuples.
# The members that we do not map, will not be highlighted.
# The members that we map to the empty string will be highlighted with the default color.
#
# **NB:** Choose your colors from the
# [CSS specification](https://developer.mozilla.org/en-US/docs/Web/CSS/color_value).

A.show(results, condensed=False, colorMap={1: "", 2: "cyan", 3: "magenta"})

# Color mapping works best for uncondensed results. If you condense results, some nodes may occupy
# different positions in different results. It is unpredictable which color will be used
# for such nodes:

A.show(results, condensed=True, colorMap={1: "", 2: "cyan", 3: "magenta"})

# You can specify to what container you want to condense. By default, everything is condensed to verses.
#
# Let's change that to phrases:

A.show(
    results,
    condensed=True,
    condenseType="phrase",
    colorMap={4: "", 5: "cyan", 6: "magenta"},
)

# # Constraining order
# You can stipulate an order on the words in your template.
# You only have to put a relational operator between them.
# Say we want only results where the plural follows the singular.

query = """
book book=Genesis
  chapter chapter=1
    verse verse=1
      sentence
        word nu=sg
        < word nu=pl
"""

# Note that we keep the `skipCols="1 2 3"` display setting in force, since it is relevant for this query as well.

results = A.search(query)
A.table(results)

# We can also require the words to be adjacent.

query = """
book book=Genesis
  chapter chapter=1
    verse verse=1
      sentence
        word nu=sg
        <: word nu=pl
"""

results = A.search(query)
colorMap = {2: "lightsalmon", 3: "mediumaquamarine"}
A.table(results, colorMap=colorMap)
A.show(results, condensed=False, colorMap=colorMap)

# # Custom feature display
#
# We would like to see the gender, number and person for words.
# The way to do that, is to perform a `A.prettySetup(features)` first.

A.displaySetup(
    extraFeatures="ps gn nu", colorMap={2: "lightsalmon", 3: "mediumaquamarine"}
)

A.show(results, condensed=False)

# The features without meaningful values have been left out. We can also change that by passing a set of values
# we think are not meaningful. The default set is
#
# ```python
# {None, 'NA', 'none', 'unknown'}
# ```

A.displaySetup(noneValues=set())
A.show(results, condensed=False)

# This makes clear that it is convenient to keep `None` in the `noneValues`:

A.displaySetup(noneValues={None})
A.show(results, condensed=False)

# We can even choose to suppress other values, e.g. the male gender values and the singular number values.

A.displaySetup(noneValues={None, "NA", "unknown", "none", "m", "sg"})
A.show(results, condensed=False)

# In the rest of the notebook we stick to our normal setup, so we reset the extra features.

A.displayReset("extraFeatures")
A.show(results, condensed=False)

# Now we completely reset the display customization.

A.displayReset()

# # Show your own tuples
#
# So far we have `show()`n the results of searches.
# But you can also construct your own tuples and show them.
#
# Whereas you can use search to get a pretty good approximation of what you want, most of the times
# you do not arrive precisely at your destination.
#
# Here is an example where we use search to come close, and then work our way to produce the end result.
#
# ## Disagreement in number
#
# We look for clauses with a one-word subject that does not agree in number with its predicate.
#
# In our search templates we cannot formulate that a feature has different values on two nodes in the template.
# We could spell out all possible combinations of values and make a search template for each of them,
# but that is needlessly complex.
#
# Let's first use search to find all clauses containing a one word subject and a predicate.
# And, to narrow down it further, we require that the word in the subject and the verb in the predicate are
# marked for number.
#
# (You may want to consult the feature docs, see the link at the start of the notebook, where `Bhsa()` is called).
#
# Note that the order of the phrases does not matter.

query = """
clause
    phrase function=Subj
        =: word nu=sg|pl
        :=
    phrase function=Pred|PreO
        word sp=verb
             nu=sg|pl
"""
results = A.search(query)

# Now the hand coding begins. We are going to extract the tuples we want.

wantedResults = tuple(
    (subj, pred)
    for (clause, phraseS, subj, phraseV, pred) in results
    if F.nu.v(subj) != F.nu.v(pred)
)
print(f"{len(wantedResults)} filtered results")

# And now we can show them:

wantedResults[0:4]

A.table(
    wantedResults, start=1, end=4, colorMap={1: "lightsalmon", 2: "mediumaquamarine"}
)

A.show(
    wantedResults, start=1, end=4, colorMap={1: "lightsalmon", 2: "mediumaquamarine"}
)

# Now suppose that we want to highlight the non-qal verb forms with a different color.
#
# We have to assing colors to the members of our tuples:

highlights = {}
for (subj, pred) in wantedResults:
    highlights[subj] = "lightsalmon"
    highlights[pred] = "mediumaquamarine" if F.vs.v(pred) == "qal" else "yellow"

# Now we can call show with the `highlights` parameter instead of the `colorMap` parameter.

A.table(wantedResults, start=1, end=4, highlights=highlights)

# Or in condensed pretty display:

A.show(
    wantedResults,
    condensed=True,
    start=3,
    end=3,
    highlights=highlights,
    extraFeatures="vs",
    withNodes=True,
)

# As you see, you have total control.

# # All steps
#
# * **[start](start.ipynb)** your first step in mastering the bible computationally
# * **[display](display.ipynb)** become an expert in creating pretty displays of your text structures
# * **search** turbo charge your hand-coding with search templates
#
# ---
#
# You know how to run queries and show off with their results.
#
# The next thing is to dive deeper into the power of templates:
#
# [advanced](searchAdvanced.ipynb)
# [sets](searchSets.ipynb)
# [relations](searchRelations.ipynb)
# [quantifiers](searchQuantifiers.ipynb)
# [fromMQL](searchFromMQL.ipynb)
# [rough](searchRough.ipynb)
# [gaps](searchGaps.ipynb)
#
# ---
#
# * **[exportExcel](exportExcel.ipynb)** make tailor-made spreadsheets out of your results
# * **[share](share.ipynb)** draw in other people's data and let them use yours
# * **[export](export.ipynb)** export your dataset as an Emdros database
# * **[annotate](annotate.ipynb)** annotate plain text by means of other tools and import the annotations as TF features
# * **[volumes](volumes.ipynb)** work with selected books only
# * **[trees](trees.ipynb)** work with the BHSA data as syntax trees
#
# CC-BY Dirk Roorda
