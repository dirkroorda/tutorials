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

A = use('bhsa', hoist=globals())
# A = use("bhsa:clone", checkout="clone", hoist=globals())

# + [markdown] tags=[]
# # Relationships
#
# There are relationship between objects that are about their identities, the way they
# occupy space, and the way they are connected.
#
# Are two objects the same, do they occupy the same slots, do they overlap, is one embedded in the other,
# does one come before the other? Is there an edge from one to another?
#
# Although these relationships are easy to define, and even easy to implement,
# they may be very costly to use.
# When searching, most of them have to be computed very many times.
#
# Some of them have been precomputed and stored in an index, e.g. the embedding relationships.
# They can be used without penalty.
#
# Other relations are not suitable for pre-computing: most inequality relations are of that kind.
# It would require an enormous amount of storage to pre-compute for each node the set of nodes that
# occupy different slots. This type of relation will not be used in narrowing down the search space,
# which means that it may take more time to get the results.
#
# We are going to test all of our relationships here.
#
# Let us first see what relationships we have:
# -

S.relationsLegend()

# The top of the list are identity and spatial relationships.
# We are going to dicuss them. They are documented in
# [relationships](https://annotation.github.io/text-fabric/tf/about/searchusage.html#relational-operators)
#
# The bottom of the list are relationships defined by the edge features of your dataset.
# We have discussed them in [advanced](searchAdvanced.ipynb).

# # Identity and order
#
# ## = equal as node
#
# The `=` means that both parts are the same node. Left and right are not two things with similar properties,
# no, they are one and the same thing.
#
# Useful if the thing you search for it part of two wildly different patterns.

query = """
v1:verse
  sentence
    clause rela=Objc
      phrase
        word sp=verb gn=f nu=pl
v2:verse
  sentence
    c1:clause
    c2:clause
    c3:clause
    c1 < c2
    c2 < c3
v1 = v2
"""
results = A.search(query)

# We show the results with the first clause in magenta and the second sentence in cyan.
#
# Note that the first and the second sentence may be the same sentence!
#
# **And observe that the last clause is the same one as the first one, hence they have the same color.**

skipCols = "1 6"  # the verses
colorMap = {2: "magenta", 6: "cyan"}
A.table(results, end=1, colorMap=colorMap, skipCols=skipCols)

A.show(results, end=1, colorMap=colorMap, skipCols=skipCols)

# ## # unequal as node
#
# `n # m` if `n` and `m` are not the same node.
#
# If you write a template, and you know that one node should come before another one,
# consider using `<` or `>`, which will constrain the results better.
#
# We have seen this in action in the search for gapped phrases.

# ## < and > canonical order
#
# `n < m` if `n` comes before `m` in the
# [canonical ordering](https://annotation.github.io/text-fabric/tf/core/nodes.html)
# of nodes.
#
# We have seen them in action before.

# # Space occupation
#
# We show that the following relationships also work with custom sets, as introduced in the
# [searchAdvanced tutorial](searchAdvanced.ipynb).
#
# We make two custom sets, `common` and `rare`, consisting of nodes whose contained slots have all
# common lexemes or some rare lexemes, like we did in
# [searchAdvanced](searchAdvanced.ipynb).

# +
COMMON_RANK = 100
RARE_RANK = 500

common = set()
rare = set()

for n in N.walk():
    nTp = F.otype.v(n)
    if nTp == "lex":
        continue
    if nTp == "word":
        ranks = [F.rank_lex.v(n)]
    else:
        ranks = [F.rank_lex.v(w) for w in L.d(n, otype="word")]
    maxRank = max(ranks)
    minRank = min(ranks)
    if maxRank < COMMON_RANK:
        common.add(n)
    if maxRank > RARE_RANK:
        rare.add(n)

print(f"{len(common):>6} members in set common")
print(f"{len(rare):>6} members in set rare")
# -

# Now we can do all kinds of searches within the domain of `common` and `rare` things.
#
# We give the names to all the sets and put them in a dictionary.

customSets = dict(
    common=common,
    rare=rare,
)

# **Expert remark**
#
# Note that these sets contain both slot nodes and non-slot nodes.
# The code that implements the basic relationship is heavily optimized and contains case distinctions as to whether nodes are slot
# or non-slot.
# For ordinary node types, it is clear on beforehand whether its nodes are slot or non-slot, but custom sets may contain both.
#
# So our `frequent` and `infrequent` sets are good tests whether the basic relationships are correctly implemented.

# ## == same slots
#
# Two objects are extensionally equal if they occupy exactly the same slots.

query = """
v:verse
    s:sentence
v == s
"""
results = A.search(query)

A.table(results, end=7, skipCols="1")
A.show(results, start=1, end=1, skipCols="1")

# Now a similar query with the custom sets:

query = """
v:common otype=verse
    s:common otype=sentence
v == s
"""
resultsCustom = A.search(query, sets=customSets)
A.table(resultsCustom, end=10, skipCols="1")
A.show(resultsCustom, start=1, end=1, skipCols="1")

# As a check we compute manually the maximum rank of the lexemes in the clauses yielded by the query without the custom sets:

# +
rejected = 0
for (verse, sentence) in results:
    maxRank = max(F.rank_lex.v(w) for w in L.d(verse, otype="word"))
    if maxRank >= COMMON_RANK:
        rejected += 1

print(f"Rejected {rejected} non-common results, leaving {len(results) - rejected} ones")
# -

# ## && overlap
#
# Two objects overlap if and only if they share at least one slot.
# This is quite costly to use in some cases.
#
# We are going to find the sentences that overlap with two verses.

query = """
sentence
/with/
v1:verse
&& ..
v2:verse
&& ..
v1 < v2
/-/
"""

# Explanation: the query looks for sentences and delivers results that are tuples with only a sentence node.
#
# This is because the stuff within the `/with/` quantifier does not contribute to the result tuples.
#
# The `/with/` quantifier poses a few restrictions on its parent, the `sentence`.
#
# From within the quantifier you can refer to the parent by `..`.
#
# The condition is that there are verses `v1` and `v2` that have overlap with the sentence, and that `v1` comes before `v2`.
#
# The result is a tuple of exactly the sentences that span multiple verses.

results = A.search(query)

A.table(results, end=5)
A.show(results, condensed=False, baseTypes="clause", start=1, end=3)

# Now with custom sets:

query = """
common otype=sentence
/with/
v1:verse
&& ..
v2:verse
&& ..
v1 < v2
/-/
"""

resultsCommon = A.search(query, sets=customSets)

A.table(resultsCommon)

# The following query has the same results but is less insightful.

query = """
sentence
  =: w1:word
  w2:word
  :=

v1:verse
  wv1:word

v2:verse
  wv2:word

w1 = wv1
w2 = wv2
v1 < v2
"""

fastResults = A.search(query)

sorted((x[0],) for x in fastResults) == sorted(results)

# ## ## not the same slots
#
# True when the two objects in question do not occupy exactly the same set of slots.
# This is a very loose relationship.
#
# We look for sentences that start with a sentence atom that is not co-extensive with its sentence.

query = """
s:sentence
=: sa:sentence_atom
s ## sa
"""
results = A.search(query)
A.table(results, end=5)
A.show(results, baseTypes="phrase", start=1, end=1)

# Now in the common domain.

query = """
s:common otype=sentence
=: sa:sentence_atom
s ## sa
"""
resultsCustom = A.search(query, sets=customSets)
A.table(resultsCustom, end=5)
A.show(resultsCustom, baseTypes="phrase", start=1, end=1)

# ## || disjoint slots
#
# True when the two objects in question do not share any slots.
# This is a rather loose relationship.
#
# This can be used for locating gaps: a textual object that lies inside a gap of another object.
# See also [gaps](searchGaps.ipynb).
#
# Here we check whether there are phrases with disjoint subphrases.

query = """
p:phrase
  s1:subphrase
  < s2:subphrase
s1 || s2
"""
results = A.search(query)
A.table(results, end=7)
A.show(results, start=1, end=1)

# Now in the common domain.

query = """
p:common otype=phrase
  s1:subphrase
  < s2:subphrase
s1 || s2
"""
resultsCustom = A.search(query, sets=customSets)
A.table(resultsCustom, end=7)
A.show(resultsCustom, start=1, end=1)

# We see that Genesis 1:1 has fallen out. Let's check the ranks of the lexemes of its last phrase:

firstSentence = F.otype.s("sentence")[0]
lastPhrase = L.d(firstSentence, otype="phrase")[-1]
[(F.g_word_utf8.v(w), F.rank_lex.v(w)) for w in L.d(lastPhrase, otype="word")]

# There you have it: the heavens are rare!

# ## [[ and ]] embedding
#
# `n [[ m` if object `n` embeds `m`.
#
# `n ]] m` if object `n` lies embedded in `m`.
#
# These relations are used implicitly in templates when there is indentation:
#
# ```
# s:sentence
#   p:phrase
#     w1:word gn=f
#     w2:word gn=m
# ```
#
# The template above implicitly states the following embeddings:
#
# * `s ]] p`
# * `p ]] w1`
# * `p ]] w2`
#
# We have seen these relations in action.

# # Positioning
#
# ## << and >> before and after (slot-wise)
#
# These relations test whether one object comes before or after an other,
# in the sense that the slots
# occupied by the one object lie completely
# before or after the slots occupied by the other object.

query = """
sentence
  c1:clause
  p:phrase
  c2:clause
  c1 << p
  c2 >> p
"""
results = A.search(query)
colorMap = {2: "lightyellow", 3: "cyan", 4: "magenta", 5: "blue"}
A.table(results, end=5, baseTypes="phrase", colorMap=colorMap)
A.show(results, condensed=False, baseTypes="phrase", start=1, end=1, colorMap=colorMap)

# In the common domain:

query = """
sentence
  c1:common otype=clause
  p:rare otype=phrase
  c2:common otype=clause
  c1 << p
  c2 >> p
"""
resultsCustom = A.search(query, sets=customSets)
A.table(resultsCustom, end=5, baseTypes="phrase", colorMap=colorMap)
A.show(
    resultsCustom,
    condensed=False,
    baseTypes="phrase",
    start=1,
    end=1,
    colorMap=colorMap,
)

# ## =: same start slots
# This relation holds when the left and right hand sides are nodes that have the same first slot.
# It serves to enforce the the children of a parent are textually the first things inside that
# parent. We have seen it in action before.
#
# ## := same end slots
# This relation holds when the left and right hand sides are nodes that have the same last slot
# It serves to enforce the the children of a parent are textually the last things inside that
# parent. We have seen it in action before.
#
# ## :: same boundary slots
# This relation holds when `=:` and `:=` both hold between the left and right hand sides.
# It serves to look for parents with single children, or at least, where the parent is textually spanned by a single child.

# Let us look for a phrase, whose start and end slots coincide with its containing clause.
# But only if the phrase does not conincide with its parent clause.

query = """
c:clause
  :: p:phrase
c ## p
"""
results = A.search(query)
A.table(results, start=1, end=5, baseTypes="phrase")
A.show(results, start=1, end=5, condenseType="clause", baseTypes="phrase")

# Here you see an extra phrase in such clauses, lying embedded in the clause-spanning phrase.
#
# A nice case of **Mind the gap!**.

# In the common domain:

query = """
c:common otype=clause
  :: p:common otype=phrase
c ## p
"""
resultsCustom = A.search(query, sets=customSets)
A.table(resultsCustom, start=1, end=10, baseTypes="phrase")
A.show(resultsCustom, start=1, end=5, condenseType="clause", baseTypes="phrase")

# ## <: adjacent before
# This relation holds when the left hand sides ends in a slot that lies before the first slot of the right hand side.
# It serves to enforce an ordering between siblings of a parent.
#
# ## :> adjacent after
# This relation holds when the left hand sides starts in a slot that lies after the last slot of the right hand side.

query = """
clause
  phrase
  <: phrase
"""
results = A.search(query)
A.table(results, start=1, end=3, baseTypes="phrase")

query = """
clause
  phrase
  :> phrase
"""
results = A.search(query)
A.table(results, start=1, end=3, baseTypes="phrase")

# Playing with common and rare:

query = """
clause
  common otype=phrase
  <: rare otype=phrase
"""
resultsCommon = A.search(query, sets=customSets)
A.table(resultsCommon, start=1, end=3, baseTypes="phrase")

query = """
clause
  common otype=phrase
  :> rare otype=phrase
"""
resultsCommon = A.search(query, sets=customSets)
A.table(resultsCommon, start=1, end=3, baseTypes="phrase")

# Another example: are there clauses with multiple clause atoms without a gap between the two?

query = """
clause
  clause_atom
  <: clause_atom
"""
results = A.search(query)
A.table(results, start=1, end=10, baseTypes="clause_atom")

# Conclusion: there is always textual material between clause_atoms of the same clause.
# If we lift the adjacency to sequentially before (`<<`) we do get results:

query = """
clause
  clause_atom
  << clause_atom
"""
results = A.search(query)
A.table(results, start=1, end=5, baseTypes="clause_atom")
A.show(results, start=1, end=1, baseTypes="clause_atom")

# # Nearness
#
# The relations with `:` in their name always have a requirement somewhere that a slot of the
# left hand node equals a slot of the right hand node, or that the two are adjacent.
#
# All these relationships can be relaxed by a **nearness number**.
# If you put a number *k* inside the relationship symbols, those restrictions will be relaxed to
# *the one slot and the other slot should have a mutual distance of at most k*.
#
# ## =k: same start within k slots
#
# Here is an example.
#
# First we look for clauses, with a phrase in it that starts at the
# same slot as the clause.

results = A.search(
    """
chapter book=Genesis chapter=1
  clause
    =: phrase
"""
)

# Now we add a bit of freedom, but not much: 0. Indeed, this is no extra
# freedom, and it should give the same number of results.

results = A.search(
    """
chapter book=Genesis chapter=1
  clause
    =0: phrase
"""
)

# Now we add real freedom: 1 and 2

results = A.search(
    """
chapter book=Genesis chapter=1
    clause
      =1: phrase
"""
)

results = A.search(
    """
chapter book=Genesis chapter=1
    clause
      =2: phrase
"""
)

# Let us see some cases:

A.table(results, start=1, end=10, baseTypes="phrase", skipCols="1")
A.show(
    results,
    condensed=False,
    start=1,
    end=4,
    colorMap={2: "yellow", 3: "cyan"},
    baseTypes="phrase",
    skipCols="1",
)

# The first and second result show the same clause, with its first and second phrase respectively.
#
# Note that we look for phrases that lie embedded in their clause.
# So we do not get phrases of a preceding clause.
#
# But if we want, we can get those as well.

results = A.search(
    """
chapter book=Genesis chapter=1
  c:clause
  p:phrase

  c =2: p
"""
)

# We have more results now. Here is a closer look:

A.table(results, start=1, end=5, baseTypes="phrase", skipCols="1")
A.show(
    results,
    condensed=False,
    start=12,
    end=14,
    colorMap={2: "yellow", 3: "cyan"},
    baseTypes="phrase",
    skipCols="1",
)

# Here you see in results 13 and 14 a phrase of the previous clause.

# Lets also play with common and rare:

resultsCommon = A.search(
    """
verse
  clause
    =: rare otype=phrase
""",
    sets=customSets,
)

resultsCommon = A.search(
    """
verse
  clause
    =0: rare otype=phrase
""",
    sets=customSets,
)

resultsCommon = A.search(
    """
verse
  clause
    =1: rare otype=phrase
""",
    sets=customSets,
)

resultsCommon = A.search(
    """
verse
  clause
    =2: rare otype=phrase
""",
    sets=customSets,
)

# ## :k= same end within k slots
#
# ## :k: same start and end within k slots

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
# relations
#
# You are comfortable in space now.
#
# Ready to enter a whole new dimension?
#
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
