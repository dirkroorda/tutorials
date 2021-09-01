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

# # Quantifiers

# Quantifiers add considerable power to search templates.
#
# Quantifiers consist of full-fledged search templates themselves, and give rise to
# auxiliary searches being performed.
#
# The use of quantifiers may prevent the need to resort to hand-coding in many cases.
# That said, they can also be exceedingly tricky, so that it is advisable to check the results
# by hand-coding anyway, until you are perfectly comfortable with them.

# # Examples

# ## Lexemes
#
# It is easy to find the lexemes that occur in a specific book only.
# Because the `lex` node of such a lexeme is contained in the node of that specific book.
#
# Lets get the lexemes specific to Ezra and then those specific to Nehemiah.

# +
query = """
book book@en=Ezra
    lex
"""
ezLexemes = A.search(query)
ezSet = {r[1] for r in ezLexemes}

query = """
book book@en=Nehemiah
    lex
"""
nhLexemes = A.search(query)
nhSet = {r[1] for r in nhLexemes}

print(f"Total {len(ezSet | nhSet)} lexemes")
# -

# What if we want to have the lexemes that occur only in Ezra and Nehemia?
#
# If such a lexeme occurs in both books, it will not be contained by either book.
# So we have missed them by the two queries above.
#
# We have to find a different way. Something like: search for lexemes of which all words occur either in Ezra or in Nehemia.
#
# With the template constructions you have seen so far, this is impossible to say.
#
# This is where [*quantifiers*](https://annotation.github.io/text-fabric/tf/about/searchusage.html#quantifiers) come in.

# ## /without/
#
# First we are going to query for these lexemes by means of a `no:` quantifier.

query = """
lex
/without/
book book@en#Ezra|Nehemiah
  w:word
  w ]] ..
/-/
"""
query1results = A.search(query, shallow=True)

# ## /where/
#
# Now the `/without/` quantifier is a bit of a roundabout way to say what you really mean.
# We can also employ the more positive `/where/` quantifier.

query = """
lex
/where/
  w:word
/have/
b:book book@en=Ezra|Nehemiah
w ]] b
/-/
"""
query2results = A.search(query, shallow=True)

# Check by hand coding:

A.silentOff()
A.indent(reset=True)
universe = F.otype.s("lex")
wordsEzNh = set(
    L.d(T.bookNode("Ezra", lang="en"), otype="word")
    + L.d(T.bookNode("Nehemiah", lang="en"), otype="word")
)
handResults = set()
for lex in universe:
    occs = set(L.d(lex, otype="word"))
    if occs <= wordsEzNh:
        handResults.add(lex)
A.info(len(handResults))

# Looks good, but we are thorough:

print(query1results == handResults)
print(query2results == handResults)

# ## Verb phrases
#
# Let's look for clauses with where all `Pred` phrases contain only verbs and look for `Subj`
# phrases in those clauses.

query = """
clause
/where/
  phrase function=Pred
/have/
  /without/
    word sp#verb
  /-/
/-/
  phrase function=Subj
"""
queryResults = A.search(query)

A.show(queryResults, end=5, condenseType="sentence")

# Note that the pieces of template that belong to a quantifier, do not correspond to nodes in the result tuples!

# Check by hand:

A.indent(reset=True)
handResults = []
for clause in F.otype.s("clause"):
    phrases = L.d(clause, otype="phrase")
    preds = [p for p in phrases if F.function.v(p) == "Pred"]
    good = True
    for pred in preds:
        if any(F.sp.v(w) != "verb" for w in L.d(pred, otype="word")):
            good = False
    if good:
        subjs = [p for p in phrases if F.function.v(p) == "Subj"]
        for subj in subjs:
            handResults.append((clause, subj))
A.info(len(handResults))

queryResults == handResults

# ### Inspection
#
# We can see which templates are being composed in the course of interpreting the quantifier.
# We use the good old `S.study()`:

query = """
clause
/where/
  phrase function=Pred
/have/
  /without/
    word sp#verb
  /-/
/-/
  phrase function=Subj
"""
S.study(query)

# Observe the stepwise unraveling of the quantifiers, and the auxiliary templates that are distilled
# from your original template.
#
# If you ever get syntax errors, run `S.study()` to find clues.

# ## Subject at start or at end
#
# We want the clauses that consist of at least two adjacent phrases, has a Subj phrase, which is either at the beginning or at the end.

# +
query = """
c:clause
/with/
  =: phrase function=Subj
/or/
  := phrase function=Subj
/-/
  phrase
  <: phrase
"""

queryResults = sorted(A.search(query, shallow=True))
# -

# Check by hand:

A.indent(reset=True)
handResults = []
for clause in F.otype.s("clause"):
    clauseWords = L.d(clause, otype="word")
    phrases = set(L.d(clause, otype="phrase"))
    if any(
        L.n(p, otype="phrase") and (L.n(p, otype="phrase")[0] in phrases)
        for p in phrases
    ):
        # handResults.append(clause)
        # continue
        subjPhrases = [p for p in phrases if F.function.v(p) == "Subj"]
        if any(L.d(p, otype="word")[0] == clauseWords[0] for p in subjPhrases) or any(
            L.d(p, otype="word")[-1] == clauseWords[-1] for p in subjPhrases
        ):
            handResults.append(clause)
A.info(len(handResults))

# A nice case where the search template performs better than this particular piece of hand-coding.

queryResults == handResults

# Let's also study this query:

S.study(query)

# ## Verb-containing phrases
#
# Suppose we want to collect all phrases with the condition that if they
# contain a verb, their `function` is `Pred`.
#
# This is a bit theoretical, but it shows two powerful constructs to increase readability
# of quantifiers.

# ### Unreadable
#
# First we express it without special constructs.

query = """
p:phrase
/where/
  w:word pdp=verb
/have/
q:phrase function=Pred
q = p
/-/
"""
results = A.search(query, shallow=True)

# We check the query by means of hand-coding:
#
# 1. is every result a phrase: either without verbs, or with function Pred?
# 2. is every phrase without verbs or with function Pred contained in the results?

# +
allPhrases = set(F.otype.s("phrase"))

ok1 = all(
    F.function.v(p) == "Pred" or all(F.pdp.v(w) != "verb" for w in L.d(p, otype="word"))
    for p in results
)
ok2 = all(
    p in results
    for p in allPhrases
    if (
        F.function.v(p) == "Pred"
        or all(F.pdp.v(w) != "verb" for w in L.d(p, otype="word"))
    )
)

print(f"Check 1: {ok1}")
print(f"Check 2: {ok2}")
# -

# Ok, we are sure that the query does what we think it does.

# ### Readable
#
# Now let's make it more readable.

query = """
phrase
/where/
  w:word pdp=verb
/have/
.. function=Pred
/-/
"""

# +
results2 = A.search(query, shallow=True)

print(f"Same results as before? {results == results2}")
# -

# Try to see how search is providing the name `parent` to the phrase atom and how it resolves the name `..`:

S.study(query)

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
# quantifiers
#
# You have come far.
#
# Time to have a look at prior work.
#
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
