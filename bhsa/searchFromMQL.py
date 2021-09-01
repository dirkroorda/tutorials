# -*- coding: utf-8 -*-
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

# # Search from MQL
#
# Maybe you know MQL.
# It is the search template language implemented by Ulrik Sandborg-Petersen in Emdros, and used
# by [SHEBANQ](https://shebanq.ancient-data.org).
#
# TF search templates have been inspired by MQL, but they are different.
#
# This notebook shows examples of real-life
# [MQL](https://github.com/ETCBC/shebanq/wiki/Documents/MQL-Query-Guide.pdf)
# queries on
# [SHEBANQ](https://shebanq.ancient-data.org/hebrew/queries).
# and
# expresses them
# as Text-Fabric [search templates](https://annotation.github.io/text-fabric/tf/about/searchusage.html).
#
# See also the
# [SHEBANQ tutorial by Bas Meeuse translated to TF](https://nbviewer.jupyter.org/github/ETCBC/bhsa/blob/master/primer/tfVersusMql.ipynb).

# %load_ext autoreload
# %autoreload 2

from tf.app import use
from tf.core.helpers import project

# We want to use a fixed data version, not a changing one, for the purposes of this notebook.

VERSION = "2017"
A = use('bhsa', hoist=globals(), version=VERSION)
# A = use("bhsa:clone", checkout="clone", hoist=globals(), version=VERSION)

# # By Oliver Glanz
#
# ## MQL
#
# [Oliver Glanz: PP with adjective followed by noun](https://shebanq.ancient-data.org/hebrew/query?version=4b&id=547)
# ```
# select all objects where
# [phrase FOCUS typ = PP
#   [word sp= prep]
#   [word sp=adjv]
#   [word sp=subs]
# ]
# ```
# 64 results having 251 words.

# ## TF

query = """
phrase typ=PP
  word sp=prep
  <: word sp=adjv
  <: word sp=subs
"""
results = A.search(query)

# ## Comparison
#
# The number of results is right. The number of words that SHEBANQ reports
# is the number of words in the phrases of the result. Let us count them:

print(sum([len(L.d(r[0], otype="word")) for r in results]))

# # Inspired by Oliver Glanz
#
# ## MQL
#
# [Dirk Roorda: Anapher](https://shebanq.ancient-data.org/hebrew/query?version=2017&id=3455)
#
# ```
# select all objects where
# [phrase
#   [word AS samelex FOCUS FIRST]
#   [word FOCUS lex = samelex.lex]
# ]
# ```
# 220 results having 458 words.

# This means: 220 verses, with 458 result words, and since there are exactly 2 words in each result, we expect 229 results.
#
# ## TF

queryTight = """
phrase
  =: w1:word
  <: w2:word

w1 .lex. w2
"""

resultsTight = A.search(queryTight)

# We miss 23 results. How can that be?
#
# Well, in MQL
#
# ```
# [phrase]
#   [word]
#   [word]
# ```
#
# means that the two words are adjacent in the phrase.
# If the phrase has gaps, words around a gap are still adjacent.
#
# In TF it is different, there such words are not adjacent.
#
# Let's lift the requirement of adjacency from the TF query:

queryLoose = """
phrase
  =: w1:word
  < w2:word

w1 .lex. w2
"""

resultsLoose = A.search(queryLoose)


# Way to many results.
#
# Let's filter these results and only retain those where `w1` and `w2` are adjacent in the MQL sense.


def filterTight(results):
    good = []
    for (p, w1, w2) in results:
        phraseWords = set(L.d(p, otype="word"))
        if all(w not in phraseWords for w in range(w1 + 1, w2)):
            good.append((p, w1, w2))
    return good


len(filterTight(resultsLoose))

# So it looks like we have the same set in our hands.
#
# There must be 23 cases of phrases with an intervening phrase after the first word,
# after which the phrase resumes with a word
# of the same lexeme. Let's identify those.
#
# From [searchGaps](searchGaps.ipynb) we pick the query that finds all gapped phrases, and we store it in a set.

queryGap = """
p:phrase
  wPreGap:word
  wLast:word
  :=

wGap:word
wPreGap <: wGap
wGap < wLast

p || wGap
"""

gaps = A.search(queryGap, shallow=True)

# Now we modify our loose query to run over gapped phrases only:

queryLooseGap = """
phrasegap
  =: w1:word
  < w2:word

w1 .lex. w2
"""

resultsLooseGap = A.search(queryLooseGap, sets=dict(phrasegap=gaps))

# And apply the filter again:

resultsGap = filterTight(resultsLooseGap)
len(resultsGap)

# Now we have one more than expected. It could be that one of the gapped phrases has an adjacent pair that
# does not lie around a gap.
#
# Indeed, result 9 is such a case.

A.show(resultsGap, start=8, end=10, condenseType="clause")

# ## An other example by Oliver Glanz
#
# We look for words with the same value for the `g_cons` feature but with a different `lex` feature.
# There is a word pair in Jeremiah 1:11-12 that has this.
#
# An obvious query to try is the following:

query = """
verse book=Jeremia chapter=1 verse=11|12
    w1:word lex*
    < w2:word
w1 .g_cons=g_cons. w2
w1 .lex#lex. w2
"""

results = A.search(query)

# But the thing is, one of those words is in verse 11, and the other in verse 12. The query as it stands, requires both
# words to be in the same verse.
#
# We could write a bit more intricate query, that requires the word pair between the last word of verse 10 and the first one of
# verse 13, but this query turns out to be inefficient. It finds a result in a few seconds (that is already way to slow) and then it spends
# ages to search a vast space where no results are to be found.

query = """
verse book=Jeremia chapter=1 verse=10
  start:word
  :=
verse book=Jeremia chapter=1 verse=13
  =: end:word

start
< w1:word
< w2:word
< end

w1 .g_cons=g_cons. w2
w1 .lex#lex. w2
"""

S.study(query)

firstResult = next(S.fetch())

A.prettyTuple(firstResult, 1, condenseType="clause", skipCols="1 3")

# An alternative is to look in a whole chapter, and to require the words not to be too far apart, e.g. at most 20.

query = """
chapter book=Jeremia chapter=1
  w1:word
  <20: w2:word

w1 < w2
w1 .g_cons=g_cons. w2
w1 .lex#lex. w2
"""

# Note that `<20:` relaxes to adjacency condition `<:` with 20 slots in both directions.
# If there is a pair of words within a slot distance of 20, then the reversed pair also satisfies that condition.
#
# Hence we put in an extra `w1 < w2`, so that every pair occurs only once.

results = A.search(query)

A.show(results, condenseType="clause", skipCols="1")

# We can do so for the whole book of Jeremiah.

query = """
book book=Jeremia
  w1:word
  <20: w2:word

w1 < w2
w1 .g_cons=g_cons. w2
w1 .lex#lex. w2
"""

results = A.search(query)

A.show(results, condenseType="clause", end=3, skipCols="1")

# Let's try the whole Bible in this way:

query = """
w1:word
<20: w2:word

w1 < w2
w1 .g_cons=g_cons. w2
w1 .lex#lex. w2
"""

results = A.search(query)

# TF is struggling with it, but it delivers!

A.show(results, condenseType="clause", end=3)

# # By Martijn Naaijer
# ## MQL
#
# [Martijn Naaijer: Object clauses with >CR](https://shebanq.ancient-data.org/hebrew/query?version=4b&id=997)
#
# ```
# Select all objects where
#
# [clause rela = Objc
#    [word focus first lex = '>CR']
# ]
# ```
#
# 157 results

# ## TF

query = """
verse
    clause rela=Objc
        =: word lex=>CR
"""
results = A.search(query)
A.table(results, end=10)

# ## Comparison
#
# We have fewer cases: 96 instead of 157.
# We are working on the ETCBC version 2017, and the query has been executed against 4b.
# There have been coding updates that are relevant to this query, e.g. in Genesis 43:27, which is in the results
# on SHEBANQ, but not here. In 2017 the `rela` is `Attr`, and not `Objc`:

query = """
verse book=Genesis chapter=43 verse=27
    clause
        =: word lex=>CR
"""
results = A.search(query)
A.show(results)

# # By Cody Kingham
# ## MQL
#
# [Cody Kingham: MI Hierarchies. p.18n49. First Person Verbs in Narrative](https://shebanq.ancient-data.org/hebrew/query?version=4b&id=1050)
#
# ```
# SELECT ALL OBJECTS WHERE
#
# [book
#    [clause txt = 'N'
#       [word FOCUS sp = verb
#         [word ps = p1
#          ]
#       ]
#    ]
# ]
# OR
# [book
#    [clause txt = '?N'
#       [word FOCUS sp = verb
#         [word ps = p1
#          ]
#       ]
#    ]
# ]
# ```
#
# 273 results.

# ## TF

query = """
book
    clause txt=N|?N
        word sp=verb ps=p1
"""
results = A.search(query)
A.table(results, end=5)

# ## Comparison
#
# One result less. Again, a coding difference between versions.
# Exercise: find out where that happened.

# # By Reinoud Oosting
# ## MQL
#
# [Reinoud Oosting: to go + object marker](https://shebanq.ancient-data.org/hebrew/query?version=4b&id=755)
#
# ```
# Select all objects
# where
#  [clause
#    [phrase function = Pred OR function = PreC
#      [word FOCUS sp = verb AND vs = qal AND lex = "HLK[" ]
#          ]
#     ..
#     [phrase FOCUS
#     [word First lex = ">T"]
#    ]
#  ]
# OR
#  [clause
#     [phrase FOCUS
#       [word First lex = ">T" ]
#     ]
# ..
#    [phrase function = Pred OR function = PreC
#      [word FOCUS sp = verb AND vs = qal AND lex = "HLK["]
#    ]
#  ]
#  ```
#
#  4 results.
#

# ## TF
#
# This is a case where we can simplify greatly because we are not hampered
# by automatic constraints on the order of the phrases.

# +
query = """
clause
  p1:phrase function=Pred|PreC
    word sp=verb vs=qal lex=HLK[
  p2:phrase
    =: word lex=>T
  p1 # p2
"""

results = A.search(query)
A.show(sorted(results), condensed=False, condenseType="clause")
# -

# # By Reinoud Oosting (ii)
# ## MQL
#
# [Reinoud Oosting: To establish covenant](https://shebanq.ancient-data.org/hebrew/query?version=4b&id=1485)
#
# ```
# select all objects
# where
#
#  [clause
#    [phrase function = Pred OR function = PreC
#      [word FOCUS sp = verb AND vs = hif AND lex = "QWM[" ]
#          ]
#     ..
#     [phrase function = Objc
#     [word FOCUS lex = "BRJT/" ]
#    ]
#  ]
# OR
#  [clause
#     [phrase function = Objc
#       [word FOCUS lex = "BRJT/" ]
#     ]
# ..
#    [phrase function = Pred OR function = PreC
#      [word FOCUS sp = verb AND vs = hif AND lex = "QWM["]
#    ]
#
# ]
# ```
#
# 13 results

# ## TF

# +
query = """
clause
  phrase function=Pred|PreC
    word sp=verb vs=hif lex=QWM[
  phrase function=Objc
    word lex=BRJT/
"""

results = A.search(query)
resultsx = sorted(
    (L.u(r[0], otype="verse") + r for r in results), key=lambda r: N.sortKey(r[0])
)
A.table(sorted(resultsx))
A.show(resultsx, start=4, end=4)
# -

# # By Reinoud Oosting (iii)
# ## MQL
#
# [Reinoud Oosting: To find grace in sight of](https://shebanq.ancient-data.org/hebrew/query?version=4b&id=1484)
#
# ```
# select all objects
# where
#
#  [clause
#    [phrase FOCUS function = Pred OR function = PreC
#      [word sp = verb AND vs = qal AND lex = "MY>[" ]
#          ]
#     ..
#     [phrase function = Objc
#     [word FOCUS lex = "XN/" ]
#    ]
# [phrase function = Cmpl
# [word FOCUS lex = "B"]
# [word FOCUS lex = "<JN/"]
# ]
#  ]
# OR
#  [clause
#     [phrase function = Objc
#       [word FOCUS lex = "XN/" ]
#     ]
# [phrase function = Cmpl
# [word FOCUS lex = "B"]
# [word FOCUS lex = "<JN/"]
# ..
#    [phrase function = Pred OR function = PreC
#      [word FOCUS sp = verb AND vs = qal AND lex = "MY>["]
#    ]
#  ]
# ]
#
# ```
#
# 38 results

# ## TF

# +
query = """
clause
  p1:phrase function=Pred|PreC
    word sp=verb vs=qal lex=MY>[
  p2:phrase function=Objc
    word lex=XN/
  p3:phrase function=Cmpl
    word lex=B
    <: word lex=<JN/
  p2 << p3
"""

results = A.search(query)
resultsx = sorted(
    (L.u(r[0], otype="verse") + r for r in results), key=lambda r: N.sortKey(r[0])
)
A.table(resultsx)
# -

# ## Comparison
#
# Two results more. Spot the differences.

# # By Stephen Ku
# ## MQL
#
# [Stephen Ku: Verbless Clauses](https://shebanq.ancient-data.org/hebrew/query?version=4&id=1314)
#
# ```
# SELECT ALL OBJECTS WHERE
#
# [clause
#  [phrase function IN (Subj)
#     [phrase_atom NOT rela IN (Appo,Para,Spec)
#       [word FOCUS pdp IN (subs,nmpr,prps,prde,prin,adjv)
#       ]
#     ]
#   ]
#  NOTEXIST [phrase function IN (Pred)]
#  ..
#  NOTEXIST [phrase function IN (Pred)]
#  [phrase function IN (PreC)
#      NOTEXIST [word pdp IN (prep)]
#      [word FOCUS pdp IN (subs,nmpr,prin,adjv) AND ls IN (card,ordn)]
#  ]
# ]
# ```
#
# 2303 results with 2129 words in those results.

# ## TF
#
# We can deal with `NOTEXIST` by means of the quantifier `/without/`.
# We can also state that features do *not* have certain values.
# And we play with the spatial relations.

query = """
clause
  phrase function=Subj
  /without/
  <: phrase function=Pred
  /-/
    phrase_atom rela#Appo|Para|Spec
      word pdp=subs|nmpr|prps|prde|prin|adjv
  << phrase function=PreC
  /without/
  :> phrase function=Pred
  /-/
  /without/
    word pdp=prep
  /-/
    word pdp=subs|nmpr|prin|adjv ls=card|ordn
"""

results = A.search(query)
clauses = project(results, 1)
print(f"{len(clauses)} clauses in results")

# ## Comparison
#
# We have 15 results less than the MQL query on SHEBANQ.
#
# Let us have a look at some results words and compare them with the result words on SHEBANQ.
# It is handy to fetch from SHEBANQ the CSV file with query results.
#
# We have fetched them and stored them in `fromShebanq.csv` in the same directory.
# It is a list of words occurring in results, so let's see which clauses are in the SHEBANQ results.

# ```
# book,chapter,verse,monad,text,ktv,phtext,phsep
# Genesis,5,4,2169,יְמֵי־,,yᵊmê-,
# Genesis,5,4,2170,אָדָ֗ם ,,ʔāḏˈām,
# Genesis,5,4,2175,שְׁמֹנֶ֥ה ,,šᵊmōnˌeh,
# Genesis,5,4,2176,מֵאֹ֖ת ,,mēʔˌōṯ,
# Genesis,5,5,2185,כָּל־,,kol-,
# Genesis,5,5,2186,יְמֵ֤י ,,yᵊmˈê,
# Genesis,5,5,2187,אָדָם֙ ,,ʔāḏˌām,
# Genesis,5,5,2190,תְּשַׁ֤ע ,,tᵊšˈaʕ,
# Genesis,5,5,2191,מֵאֹות֙ ,,mēʔôṯ,
# Genesis,5,5,2194,שְׁלֹשִׁ֖ים ,,šᵊlōšˌîm,
# ```

shebanqClauses = set()
with open("fromShebanq.csv") as fh:
    for (i, line) in enumerate(fh):
        if i == 0:
            continue
        fields = line.split(",")
        word = int(fields[3])
        clause = L.u(word, otype="clause")[0]
        shebanqClauses.add(clause)
len(shebanqClauses)

# That looks good: both methods yield the same amount of clauses.
#
# But we need to be thorough.

clauses == shebanqClauses

# See? They are not the same clauses.
#
# Let's spot the differences.

tfNotMql = clauses - shebanqClauses
mqlNotTf = shebanqClauses - clauses
print(f"Results of TF  but not MQL: {sorted(tfNotMql)}")
print(f"Results of MQL but not TF : {sorted(mqlNotTf)}")

# ## TF yes - MQL no
#
# First we do the results that TF provides, but not MQL.

A.displaySetup(extraFeatures="ls")

newResults = [r for r in results if r[0] in tfNotMql]
newResults

# We are going to inspect them clause by clause.
# Note that we have two results per clause, the only difference between the two results is
# in column 4, which corresponds to the word in the Subj phrase.

A.show(newResults, condensed=True, withNodes=True, condenseType="clause")


# In all three cases we see a Pred phrase somewhere after the PreC phrase.
#
# The `NOTEXIST` of MQL works a bit subtle: the not-exists claim holds from the place where it appears till the end
# of the surrounding context.
#
# So, in fact, the second `NOTEXIST` is redundant. Following the MQL query, the clause cannot have a Pred phrase beyond
# the Subj phrase.

# ## TF no - MQL yes
#
# Before we remedy our TF query to match this effect, let us inspect the clauses delivered by MQL, but not by TF.
#
# Most of the effort in the code below is to furnish appropriate highlighting.


def showClause(clause):
    highlights = {}
    for phrase in L.d(clause, otype="phrase"):
        pf = F.function.v(phrase)
        if pf == "Subj":
            highlights[phrase] = "cyan"
            for phraseAtom in L.d(phrase, otype="phrase_atom"):
                rela = F.rela.v(phraseAtom)
                if rela in {"Appo", "Para", "Spec"}:
                    continue
                words = L.d(phraseAtom, otype="word")
                for word in words:
                    pdp = F.pdp.v(word)
                    if pdp in {"subs", "nmpr", "prps", "prde", "prin", "adjv"}:
                        highlights[word] = "yellow"
        elif pf == "PreC":
            highlights[phrase] = "lightskyblue"
            words = L.d(phrase, otype="word")
            if any(F.pdp.v(word) == "prep" for word in words):
                continue
            for word in words:
                pdp = F.pdp.v(word)
                ls = F.ls.v(word)

                if ls in {"card", "ord"} and pdp in {"subs", "nmpr", "prin", "adjv"}:
                    highlights[word] = "yellow"
        elif pf == "Pred":
            highlights[phrase] = "coral"
    A.pretty(clause, withNodes=True, highlights=highlights)


mqlClauses = sorted(mqlNotTf)

# We inspect the cases one by one:

showClause(mqlClauses[0])

# What could be wrong here? The only violation could be in the *gap*. What happens before the PreC phrase?
# If there is an adjacent Pred phrase, it explains why this does not show up in the TF query results.
# Let's find out.

xPhrase = L.u(2189, otype="phrase")[0]
A.pretty(
    xPhrase,
    withNodes=True,
    highlights={xPhrase: "coral" if F.function.v(xPhrase) == "Pred" else "lightyellow"},
)

# Clearly, this is the culprit.
# it is in the same clause.

showClause(mqlClauses[1])

# Again, a gap just before the Prec phrase. Indeed:

xPhrase = L.u(132678, otype="phrase")[0]
A.pretty(
    xPhrase,
    withNodes=True,
    highlights={xPhrase: "coral" if F.function.v(xPhrase) == "Pred" else "lightyellow"},
)

showClause(mqlClauses[2])

# We are getting used to it!

xPhrase = L.u(403004, otype="phrase")[0]
A.pretty(
    xPhrase,
    withNodes=True,
    highlights={xPhrase: "coral" if F.function.v(xPhrase) == "Pred" else "lightyellow"},
)

# But no, here we have a different cause. Probably a Pred phrase right after the Subj phrase.

xPhrase = L.u(402999, otype="phrase")[0]
A.pretty(
    xPhrase,
    withNodes=True,
    highlights={xPhrase: "coral" if F.function.v(xPhrase) == "Pred" else "lightyellow"},
)

# ## Remedy
#
# We have seen all the causes why the TF search and the MQL query produced different results.
#
# Now we are going to remedy the TF query, such that it produces the same results as the MQL.
#
# Let us start with what we just saw: when we stipulate the non-existence of a Pred phrase, we only claim that such
# a phrase does not occur in the same clause.
#
# Then we remove the second non-existence claim of a Pred phrase, since the MQL query just stipulates that there is
# no Pred phrase after the Subj phrase.
#
# But then we can make the quantifier much simpler. Instead of applying it to the Subj phrase,
# we apply it to the enclosing clause. That will solve the problem of phrases outside the clause in one go!

query = """
c:clause
/without/
  phrase function=Subj
  << phrase function=Pred
/-/
  p:phrase function=Subj
    phrase_atom rela#Appo|Para|Spec
      word pdp=subs|nmpr|prps|prde|prin|adjv
  << phrase function=PreC
  /without/
    word pdp=prep
  /-/
    word pdp=subs|nmpr|prin|adjv ls=card|ordn
"""

# +
results = A.search(query)
clauses = project(results, 1)
print(f"{len(clauses)} clauses in results")

clauses == shebanqClauses
# -

# And this is in exact agreement with the MQL query.

# As a bonus, let's study this query in order to see what the quantifiers are doing.

S.study(query)

# # By Dirk Roorda
# ## MQL
#
# [Dirk Roorda: Yesh](https://shebanq.ancient-data.org/hebrew/query?version=4b&id=556)
#
# ```
# select all objects where
# [book [chapter [verse
# [clause
#     [clause_atom
#         [phrase
#             [phrase_atom
#                 [word focus lex="JC/" OR lex=">JN/"]
#             ]
#         ]
#     ]
# ]
# ]]]
# ```
#
# 926 results

# ## TF

# +
query = """
verse
  clause
    clause_atom
      phrase
        phrase_atom
          word lex=JC/|>JN/
"""

results = A.search(query)
A.table(sorted(results), end=7)
# -

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
# fromMQL
#
# You master the theory.
#
# In practice, there are pitfalls:
#
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
