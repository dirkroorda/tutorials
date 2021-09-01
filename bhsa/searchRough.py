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

# %load_ext autoreload
# %autoreload 2

from tf.app import use

VERSION = "2021"

A = use('bhsa', hoist=globals())
# A = use("bhsa:clone", checkout="clone", hoist=globals())

# ## Rough edges
#
# It might be helpful to peek under the hood, especially when exploring searches that go slow.
#
# If you went through the previous parts of the tutorial you have encountered cases where things come
# to a grinding halt.
#
# Yet we can get a hunch of what is going on, even in those cases.
# For that, we use the lower-level search api `S` of Text-Fabric, and not the
# wrappers that the high level `A` api provides.
#
# The main difference is, that `S.search()` returns a *generator* of the results,
# whereas `A.search()` returns a list of the results.
# In fact, `A.search()` calls the generator function delivered by `S.search()` as often as needed.
#
# For some queries, the fetching of results is quite costly, so costly that we do not want to fetch
# all results up-front. Rather we want to fetch a few, to see how it goes.
# In these cases, directly using `S.search()` is preferred over `A.search()`.

query = """
book
  chapter
    verse
      phrase det=und
        word lex=>LHJM/
"""

# ### Study
#
# First we call `S.study(query)`.
#
# The syntax will be checked, features loaded, the search space will be set up, narrowed down,
# and the fetching of results will be prepared, but not yet executed.
#
# In order to make the query a bit more interesting, we lift the constraint that the results must be in Genesis 1-2.

S.study(query)

# Before we rush to the results, lets have a look at the *plan*.

S.showPlan()

# Here you see already what your results will look like.
# Each result `r` is a *tuple* of nodes:
# ```
# (R0, R1, R2, R3, R4)
# ```
# that instantiate the objects in your template.
#
# In case you are curious, you can get details about the search space as well:

S.showPlan(details=True)

# The part about the *nodes* shows you how many possible instantiations for each object in your template
# has been found.
# These are not results yet, because only combinations of instantiations
# that satisfy all constraints are results.
#
# The constraints come from the relations between the objects that you specified.
# In this case, there is only an implicit relation: embedding `[[`.
# Later on we'll examine all
# [spatial relations](https://annotation.github.io/text-fabric/tf/about/searchusage.html#relational-operators).
#
# The part about the *edges* shows you the constraints,
# and in what order they will be computed when stitching results together.
# In this case the order is exactly the order by which the relations appear in the template,
# but that will not always be the case.
# Text-Fabric spends some time and ingenuity to find out an optimal *stitch plan*.
# Fetching results is like selecting a node, stitching it to another node with an edge,
# and so on, until a full stitch of nodes intersects with all the node sets from which they
# must be chosen (the yarns).
#
# Fetching results may take time.
#
# For some queries, it can take a large amount of time to walk through all results.
# Even worse, it may happen that it takes a large amount of time before getting the *first* result.
# During stitching, many stitchings will be tried and fail before they can be completed.
#
# This has to do with search strategies on the one hand,
# and the very likely possibility to encounter *pathological* search patterns,
# which have billions of results, mostly unintended.
# For example, a simple query that asks for 5 words in the Hebrew Bible without further constraints,
# will have 425,000 to the power of 5 results.
# That is 10-e28 (a one with 28 zeros),
# roughly the number of molecules in a few hundred liters of air.
# That may not sound much, but it is 10,000 times the amount of bytes
# that can be currently stored on the whole Internet.
#
# Text-Fabric search is not yet done with finding optimal search strategies,
# and I hope to refine its arsenal of methods in the future, depending on what you report.

# ### Counting results
# It is always a good idea to get a feel for the amount of results, before you dive into them head-on.

S.count(progress=1, limit=5)

# We asked for 5 results in total, with a progress message for every one.
# That was a bit conservative.

S.count(progress=100, limit=500)

# Still pretty quick, now we want to count all results.

S.count(progress=200, limit=-1)

# ### Fetching results
#
# It is time to see something of those results.

S.fetch(limit=10)

# Not very informative.
# Just a quick observation: look at the last column.
# These are the result nodes for the `word` part in the query, indicated as `R7` by `showPlan()` before.
# And indeed, they are all below 425,000, the number of words in the Hebrew Bible.
#
# Nevertheless, we want to glean a bit more information off them.

for r in S.fetch(limit=10):
    print(S.glean(r))

# ##### Caution
# > It is not possible to do `len(S.fetch())`.
# Because `fetch()` is a *generator*, not a list.
# It will deliver a result every time it is being asked and for as long as there are results,
# but it does not know in advance how many there will be.
#
# >Fetching a result can be costly, because due to the constraints, a lot of possibilities
# may have to be tried and rejected before a the next result is found.
#
# > That is why you often see results coming in at varying speeds when counting them.

# We can also use `A.table()` to make a list of results.
# This function is part of the `Bhsa` API, not of the generic Text-Fabric machinery, as opposed to `S.glean()`.
#
# So, you can use `S.glean()` for every Text-Fabric corpus, but the output is still not very nice.
# `A.table()` gives much nicer output.

A.table(S.fetch(limit=5))

# ## Slow queries
#
# The search template above has some pretty tight constraints on one of its objects,
# so the amount of data to deal with is pretty limited.
#
# If the constraints are weak, search may become slow.
#
# For example, here is a query that looks for pairs of phrases in the same clause in such a way that
# one is engulfed by the other.

query = """
% test
% verse book=Genesis chapter=2 verse=25
verse
  clause

    p1:phrase
      w1:word
      w3:word
      w1 < w3

    p2:phrase
      w2:word
      w1 < w2
      w3 > w2

    p1 < p2
"""

# A couple of remarks you may have encountered before.
#
# * some objects have got a name
# * there are additional relations specified between named objects
# * `<` means: *comes before*, and `>`: *comes after* in the canonical order for nodes,
#   which for words means: comes textually before/after, but for other nodes the meaning
#   is explained [here](https://annotation.github.io/text-fabric/tf/core/nodes.html)
# * later on we describe those relations in more detail
#
# > **Note on order**
# Look at the words `w1` and `w3` below phrase `p1`.
# Although in the template `w1` comes before `w3`, this is not
# translated in a search constraint of the same nature.
#
# > Order between objects in a template is never significant, only embedding is.
#
# Because order is not significant, you have to specify order yourself, using relations.
#
# It turns out that this is better than the other way around.
# In MQL order *is* significant, and it is very difficult to
# search for `w1` and `w2` in any order.
# Especially if your are looking for more than 2 complex objects with lots of feature
# conditions, your search template would explode if you had to spell out all
# possible permutations. See the example of Reinoud Oosting below.
#
# > **Note on gaps**
# Look at the phrases `p1` and `p2`.
# We do not specify an order here, only that they are different.
# In order to prevent duplicated searches with `p1` and `p2` interchanged, we even
# stipulate that `p1 < p2`.
# There are many spatial relationships possible between different objects.
# In many cases, neither the one comes before the other, nor vice versa.
# They can overlap, one can occur in a gap of the other, they can be completely disjoint
# and interleaved, etc.

# +
# ignore this
# S.tweakPerformance(yarnRatio=2)
# -

S.study(query)

# Text-Fabric knows that narrowing down the search space in this case would take ages,
# without resulting in a significantly shrunken space.
# So it skips doing so for most constraints.
#
# Let us see the plan, with details.

S.showPlan(details=True)

# As you see, we have a hefty search space here.
# Let us play with the `count()` function.

S.count(progress=10, limit=100)

# We can be bolder than this!

S.count(progress=100, limit=1000)

# OK, not too bad, but note that it takes a big fraction of a second to get just 100 results.
#
# Now let us go for all of them by the thousand.

S.count(progress=1000, limit=-1)

# See? This is substantial work.

A.table(S.fetch(limit=5))

# ## Hand-coding
#
# As a check, here is some code that looks for basically the same phenomenon:
# a phrase within the gap of another phrase.
# It does not use search, and it gets a bit more focused results, in half the time compared
# to the search with the template.
#
# > **Hint**
# If you are comfortable with programming, and what you look for is fairly generic,
# you may be better off without search, provided you can translate your insight in the
# data into an effective procedure within Text-Fabric.
# But wait till we are completely done with this example!

TF.indent(reset=True)
TF.info("Getting gapped phrases")
results = []
for v in F.otype.s("verse"):
    for c in L.d(v, otype="clause"):
        ps = L.d(c, otype="phrase")
        first = {}
        last = {}
        slots = {}
        # make index of phrase boundaries
        for p in ps:
            words = L.d(p, otype="word")
            first[p] = words[0]
            last[p] = words[-1]
            slots[p] = set(words)
        for p1 in ps:
            for p2 in ps:
                if p2 < p1:
                    continue
                if len(slots[p1] & slots[p2]) != 0:
                    continue
                if first[p1] < first[p2] and last[p2] < last[p1]:
                    results.append(
                        (v, c, p1, p2, first[p1], first[p2], last[p2], last[p1])
                    )
TF.info("{} results".format(len(results)))

# ## Pretty printing
#
# We can use the pretty printing of `A.table()` and `A.show()` here as well, even though we have
# not used search!
#
# Not that you can show the node numbers. In this case it helps to see where the gaps are.

A.table(results, withNodes=True, end=5)
A.show(results, start=1, end=1)

# **NB**
# Gaps are a tricky phenomenon. In [gaps](searchGaps.ipynb) we will deal with them cruelly.

# # Performance tuning
#
# Here is an example by Yanniek van der Schans (2018-09-21).

query = """
c:clause
  PreGap:phrase_atom
  LastPhrase:phrase_atom
  :=

Gap:clause_atom
  :: word

PreGap < Gap
Gap < LastPhrase
c || Gap
"""

# Here are the current settings of the performance parameters:

S.tweakPerformance()

S.study(query)
S.showPlan(details=True)

S.count(progress=1, limit=3)

# Can we do better?
#
# The performance parameter `yarnRatio` can be used to increase the amount of preprocessing, and we can
# increase to number of random samples that we make by `tryLimitFrom` and `tryLimitTo`.
#
# We start with increasing the amount of up-front edge-spinning.

S.tweakPerformance(yarnRatio=0.2, tryLimitFrom=10000, tryLimitTo=10000)

S.study(query)
S.showPlan(details=True)

# It seems to be the same plan.

S.count(progress=1, limit=3)

# No improvement.

# What if we decrease the amount of edge spinning?

S.tweakPerformance(yarnRatio=5, tryLimitFrom=10000, tryLimitTo=10000)

S.study(query)
S.showPlan(details=True)

S.count(progress=1, limit=3)

# Again, no improvement.

# We'll look for queries where the parameters matter more in the future.

# Here is how to reset the performance parameters:

S.tweakPerformance(yarnRatio=None, tryLimitFrom=None, tryLimitTo=None)

# # Next
#
# You have seen cases where the implementation is to blame.
#
# Now I want to point to gaps in your understanding:
# [gaps](searchGaps.ipynb)
#
# ---
#
# [basic](search.ipynb)
# [advanced](searchAdvanced.ipynb)
# [sets](searchSets.ipynb)
# [relations](searchRelations.ipynb)
# [quantifiers](searchQuantifiers.ipynb)
# rough
# [gaps](searchGaps.ipynb)

# # All steps
#
# * **[start](start.ipynb)** your first step in mastering the bible computationally
# * **[display](display.ipynb)** become an expert in creating pretty displays of your text structures
# * **[search](search.ipynb)** turbo charge your hand-coding with search templates
#
# ---
#
# [advanced](searchAdvanced.ipynb)
# [sets](searchSets.ipynb)
# [relations](searchRelations.ipynb)
# [quantifiers](searchQuantifiers.ipynb)
# [fromMQL](searchFromMQL.ipynb)
# rough
#
# You have seen cases where the implementation is to blame.
#
# Now I want to point to gaps in your understanding:
#
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
