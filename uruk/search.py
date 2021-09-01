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

# <img align="right" src="images/ninologo.png" width="150"/>
# <img align="right" src="images/tf-small.png" width="125"/>
# <img align="right" src="images/dans.png" width="150"/>
#
# # Search
#
# Search is essential to get around in the corpus, and it is convenient as well.
# Whereas the whole point of Text-Fabric is to move around in the corpus programmatically,
# we show that
# [template based search](https://annotation.github.io/text-fabric/tf/about/searchusage.html)
# makes everything a lot more convenient ...
#
# Along with showing how search works, we also point to pretty ways to display your search results.
# The good news is that `search` and `pretty` work well together.

# %load_ext autoreload
# %autoreload 2

from IPython.display import display, Markdown
from tf.app import use

A = use("uruk:clone", checkout="clone", hoist=globals())
# A = use('uruk', hoist=globals())

# # The basics
#
# Here is a very simple query: we look for tablets containing a numeral sign.

# +
query = """
tablet
  sign type=numeral
"""

results = A.search(query)
# -

# We can display the results in a table (here are the first 5):

A.table(results, end=5, condenseType="line")

# We can combine all results that are on the same tablet:

A.table(results, condensed=True, condenseType="line", end=5)

# And we can show them inside the face they occur in:

A.show(results, condenseType="face", end=2, skipCols="1")

# The feature *type* is displayed because it occurs in the query.
# We can make the display a bit more compact by suppressing those features:

A.show(results, condenseType="face", end=2, queryFeatures=False, skipCols="1")

# ## Finding a tablet
#
# Suppose we have the *p-number* of a tablet.
# How do we find that tablet?
# Remembering from the feature docs that the p-numbers are stored in the feature
# `catalogId`, we can write a *search template*.

query = """
tablet catalogId=P005381
"""
results = A.search(query)
A.table(results)

# The function `A.table()` gives you a tabular overview of the results,
# with a link to the tablet on CDLI.
#
# But we can also get more information by using `A.show()`:

A.show(results)

# Several things to note here
#
# * if you want to see the tablet on CDLI, you can click on the tablet header;
# * the display matches the layout on the tablet:
#   * faces and columns are delineated with red lines
#   * lines and cases are delineated with blue lines
#   * cases and subcases alternate their direction of division between horizontal and vertical:
#     lines are horizontally divided into cases, they are vertically divided into subcases, and they
#     in turn are horizontally divided in subsubcases, etc.
#   * quads and signs are delineated with grey lines
#   * clusters are delineated with brown lines (see further on)
#   * lineart is given for top-level signs and quads; those that are part of a bigger quad do not
#     get lineart;
#
# It is possible to switch off the lineart.

# ## More info in the results
# You can show the line numbers that correspond to the ATF source files as well.
# Let us also switch off the lineart.

query = """
tablet catalogId=P005381
"""
results = A.search(query)
A.table(results, lineNumbers=True)
A.show(results, lineNumbers=True, showGraphics=False)

# There is a big quad in `obverse:2 line 1`. We want to call up the lineart for it separately.
# First step: make the nodes visible.

query = """
tablet catalogId=P005381
"""
results = A.search(query)
A.table(results, withNodes=True)
A.show(results, withNodes=True, showGraphics=False)

# We read off the node number of that quad and fetch the lineart.

A.lineart(143015)

# ## Search templates
# Let's highlight all numerals on the tablet.
#
# We prefer our results to be condensed per tablet for the next few shows.
#
# We make that the temporary default:

A.displaySetup(condensed=True)

query = """
tablet catalogId=P005381
  sign type=numeral
"""
results = A.search(query)
A.show(results, queryFeatures=False)

# We can do the same for multiple tablets. But now we highlight the undivided lines,
# just for variation.

query = """
tablet catalogId=P003581|P000311
  line terminal
"""
results = A.search(query)

A.table(results, showGraphics=False, withPassage=False)

A.show(results, showGraphics=False, condenseType="tablet")

# In an other chapter of this tutorial, [steps](steps.ipynb) we encounter a grapheme with a double prime.
# There is only one, and we showed the tablet on which it occurs, without highlighting the grapheme in question.
# Now we can do the highlight:

results = A.search(
    """
sign prime=2
"""
)

A.show(results)

# ## Search for spatial patterns
# A few words on the construction of search templates.
#
# The idea is that you mimick the things you are looking for
# in your search template.
# Embedded things are mimicked by indentation.
#
# Let's search for a line with a case in it that is not further divided,
# in which there is a numeral and an ideograph.
#
# Here is our first attempt, and we show the first tablet only.
# Note that you can have comments in a search template.
# Lines that start with `#` are ignored.

query = """
line
  case terminal=1
% order is not important
    sign type=ideograph
    sign type=numeral
"""
results = A.search(query)

# First a glance at the first 3 items in tabular view.

A.table(results, end=2, showGraphics=False)

# Ah, we were still in condensed mode.
#
# For this query the table is more perspicuous in normal mode, so we tell not to condense.

A.table(results, condensed=False, end=7, showGraphics=False)

# Now the results on the first tablet, condensed by line.

A.show(results, end=1, condenseType="line")

# The order between the two signs is not defined by the template,
# despite the fact that the line with the ideograph
# precedes the line with the numeral.
# Results may have the numeral and the ideograph in any order.
#
# In fact, the highlights above represent multiple results.
# If a case has say 2 numerals and 3 ideographs, there are 6 possible
# pairs.
#
# By default, results are shown in *condensed* mode.
# That means that results are shown per tablet, and on the result tablets
# everything that is in some result is being highlighted.
#
# It is also possible to see the uncondensed results.
# That gives you an exact picture of each real result constellation.
#
# In order to illustrate the difference, we focus on one tablet and one case.
# This case has 3 numerals and 2 ideographs, so we expect 6 results.

query = """
tablet catalogId=P448702
  line
    case terminal=1 number=2a
      sign type=ideograph
      sign type=numeral
"""
results = A.search(query)

# We show them condensed (by default), so we expect 1 line with all ideographs and numerals in case `2a'` highlighted.

A.show(results, showGraphics=False, condenseType="line")

# Now the same results in uncondensed mode. Expect 6 times the same line with
# different highlighted pairs of signs.
#
# Note that we can apply different highlight colors to different parts of the result.
# The words in the pair are member 4 and 5.
#
# The members that we do not map, will not be highlighted.
# The members that we map to the empty string will be highlighted with the default color.
#
# **NB:** Choose your colors from the
# [CSS specification](https://developer.mozilla.org/en-US/docs/Web/CSS/color_value).

A.displaySetup(
    condensed=False,
    skipCols="1",
    colorMap={2: "", 3: "cyan", 4: "magenta"},
    showGraphics=False,
    condenseType="line",
    queryFeatures=False,
)

A.show(results)

# Color mapping works best for uncondensed results. If you condense results, some nodes may occupy
# different positions in different results. It is unpredictable which color will be used
# for such nodes:

A.show(results, condensed=True)

A.displayReset()

# You can enforce order.
# We modify the template a little to state a
# relational condition, namely that the ideograph follows the numeral.

query = """
tablet catalogId=P448702
  line
    case terminal=1 number=2a
      sign type=ideograph
      > sign type=numeral
"""
results = A.search(query)
A.table(results, condensed=False, showGraphics=False)

# Still six results.
# No wonder, because the case has first three numerals in a row and then 2 ideographs.
#
# Do you want the ideograph and the numeral to be *adjacent* as well?
# We only have to add 1 character to the template to make it happen.

query = """
tablet catalogId=P448702
  line
    case terminal=1 number=2a
      sign type=ideograph
      :> sign type=numeral
"""
results = A.search(query)

A.table(results, condensed=False, showGraphics=False)

A.displaySetup(
    condensed=False,
    skipCols="1",
    colorMap={2: "", 3: "cyan", 4: "magenta"},
    showGraphics=False,
    condenseType="line",
    queryFeatures=False,
)

A.show(results, condensed=False)

A.displayReset()

# By now it pays off to study the possibilities of
# [search templates](https://annotation.github.io/text-fabric/tf/about/searchusage.html).
#
# If you want a reminder of all possible spatial relationships between nodes, you can call it up
# here in your notebook:

S.relationsLegend()

# ## Comparisons in templates: cases
#
# Cases have a feature depth which indicate their nesting depth within a line.
# It is not the depth *of* that case, but the depth *at* which that case occurs.
#
# Comparison queries are handy to select cases of a certain minimum or maximum depth.

# We'll work a lot with `condensed=False`, and `lineart` likewise, so let's make that the default:

A.displaySetup(condensed=False, showGraphics=False)

query = """
case depth=3
"""
results = A.search(query)
A.table(results, end=10)

# Are there deeper cases?

query = """
case depth>3
"""
results = A.search(query)
A.table(results, end=10)

# Still deeper?

query = """
case depth>4
"""
results = A.search(query)
A.table(results, end=10)

# As a check: the cases with depth 4 should be exactly the cases with depth > 3:

query = """
case depth=4
"""
results = A.search(query)
A.table(results, end=10)
tc4 = len(results)

# Terminal cases at depth 1 are top-level divisions of lines that are not themselves divided further.

query = """
case depth=1 terminal
"""
results = A.search(query)
A.table(results, end=10)
tc1 = len(results)

# Now let us select both the terminal cases of level 1 and 4.
# They are disjunct, so the amounts should add up.

query = """
case depth=1|4 terminal
"""
results = A.search(query)
A.table(results, end=10)
tc14 = len(results)
print(f"{tc1} + {tc4} = {tc1 + tc4} = {tc14}")

# ## Relational patterns: quads
#
# Quads are compositions of signs by means of *operators*, such as `.` and `x`.
# The operators are coded as an *edge* feature with values. The `op`-edges are between the signs/quads that are combined,
# and the values of the `op` edges are the names of the operators in question.
#
# Which operators do we have?

for (op, freq) in E.op.freqList():
    print(f"{op} : {freq:>5}x")

# Between how many sign pairs do we have an operator?

query = """
sign
-op> sign
"""
results = A.search(query)

# Lets specifically ask for the `x` operator:

query = """
sign
-op=x> sign
"""
results = A.search(query)


# Less than expected?
#
# We must not forget the combinations between quads and between quads and signs.
#
# We write a function that gives all pairs of sign/quads connected by a specific operator.
#
# This is a fine illustration of how you can use programming to compose search templates,
# instead of writing them out yourself.


def getCombi(op):
    types = ("sign", "quad")
    allResults = []
    for type1 in types:
        for type2 in types:
            query = f"""
{type1}
-op{op}> {type2}
"""
            results = A.search(query, silent=True)
            print(f"{len(results):>5} {type1} {op} {type2}")
            allResults += results
    print(f"{len(allResults):>5} {op}")


# Now we can count all combinations with `x`:

getCombi("=x")

getCombi("=.")

getCombi("=&")

getCombi("=+")

# In exact agreement with the results of `E.op.freqList()` above.
# But we are more flexible!
#
# We can ask for more operators at the same time.

getCombi("=x|+")

getCombi("~[^a-z]")

# Finally, we zoom in on the rare cases where the operator is `x` used between a quad and a sign.
# We want to see the show the lines where they occur.

query = """
line
  quad
  -op=x> sign
"""
results = A.search(query)
A.show(results, withNodes=True, showGraphics=True, condenseType="line")

# Hint: if you want to see where these lines come from, hover over the line indicator, or click on it.
#
# Alternatively, you can set the condense type to tablet.
# And note that we have set the base type to `quad`, so that the pretty display does not unravel the quads.

A.show(
    results, withNodes=True, showGraphics=True, condenseType="tablet", baseTypes="quad"
)

# ## Regular expressions in templates
# We can use regular expressions in our search templates.
#
# ### Digits in graphemes
# We search for non-numeral signs whose graphemes contains digits.

A.displaySetup(condensed=True)

query = """
sign type=ideograph grapheme~[0-9]
"""
results = A.search(query)
A.table(results, withNodes=True, end=5)

# We can add a bit more context easily:

query = """
tablet
  face
    column
      line
        sign type=ideograph grapheme~[0-9]
"""
results = A.search(query)
A.table(results, condensed=False, end=10)

# ### Pit numbers
#
# The feature `excavation` gives you the number of the pit where a tablet is found.
# The syntax of pit numbers is a bit involved, here are a few possible values:
#
# ```
# W 20497
# W 20335,3
# W 19948,10
# W 20493,26
# W 17890,b
# W 17729,o
# W 15920,b5
# W 17729,aq
# W 19548,a + W 19548,b
# W 17729,cn + W 17729,eq
# W 14337,a + W 14337,b + W 14337,c + W 14337,d + W 14337,e
# Ashm 1928-445b
# ```
#
# Let's assume we are interested in `SZITA~a1` signs occurring in cases of depth 1.
# The following query finds them all:

query = """
tablet
  case depth=1
    sign grapheme=SZITA variant=a1
"""
results = A.search(query)

# Now we want to organize them by excavation number:

# +
signPerPit = {}

for (tablet, case, sign) in sorted(results):
    pit = F.excavation.v(tablet) or "no pit information"
    signPerPit.setdefault(pit, []).append(sign)

for pit in sorted(signPerPit):
    print(f"{pit:<30} {len(signPerPit[pit]):>2}")
# -

# We can restrict results to those on tablets found in certain pits by constraining the search template.
# If we are interested in pit `20274` we can use a regular expression that matches all 4 detailed pit numbers
# based on `20274`.
# So, we do not say
#
# ```
# excavation=20274
# ```
# but
#
# ```
# excavation~20274
# ```

query = """
tablet excavation~20274
  case depth=1
    sign grapheme=SZITA variant=a1
"""
results = A.search(query)
A.table(results, condensed=False, showGraphics=False)

# Or if we want to restrict ourselves to pit numbers with a `W`, we can say:

query = """
tablet excavation~W
  case depth=1
    sign grapheme=SZITA variant=a1
"""
results = A.search(query)

# ## Quantifiers in templates
#
# So far we have seen only very positive templates.
# They express what you want to see in the result.
#
# It is also possible to state conditions about what you do not want to see in the results.

# ### Tablets without case divisions
#
# Let's find all tablets in which all lines are undivided, i.e. lines without cases.

query = """
tablet
/without/
  case
/-/
"""

# The expression
#
# ```
# /without/
# template
# /-/
# ```
#
# is a [quantifier](https://annotation.github.io/text-fabric/tf/about/searchusage.html#quantifiers).
#
# It poses a condition on the preceding line in the template, in this case the `tablet`.
# And the condition is that the template
#
# ```
# tablet
#   case
# ```
#
# does not have results.

results = A.search(query)

A.show(results, end=2)

# Now let's find cases without numerals.

query = """
case
/without/
  sign type=numeral
/-/
"""
results = A.search(query)

# We show a few.

A.show(results, end=2)

# Now we can use this to get something more sophisticated: the tablets that do not have numerals in their cases. So only undivided lines may contain numerals.
#
# Let's find tablets that do have cases, but just no cases with numerals.

query = """
tablet
/where/
  case
/have/
  /without/
    sign type=numeral
  /-/
/-/
/with/
  case
/-/
"""

results = A.search(query)

A.show(results, end=2)

# Can we find such tablet which do have numerals on their undivided lines.
#
# We show here a way to use the results of one query in another one:
# *custom sets*.
#
# We put the set of tablets with cases but without numerals in cases in a set called `cntablet`.
#
# We run the query again, but now in shallow mode, so that the result is a set.
#
# By the way: read more about custom sets and shallow mode in the description of
# [`A.search()`](https://annotation.github.io/text-fabric/tf/search/search.html#tf.search.search.Search.search).

results = A.search(query, shallow=True)
customSets = dict(cntablet=results)

# Now we can perform a very simple query for numerals on this set: we want tablets with numerals.
# By restricting ourselves to this set, we now that these numerals must occur on undivided lines.

query = """
cntablet
  sign type=numeral
"""
results = A.search(query, sets=customSets)

A.show(results, end=2, queryFeatures=False)

# We could have found these results by one query as well.
# Judge for yourself which method causes the least friction.

query = """
tablet
/without/
  case
    sign type=numeral
/-/
/with/
  case
/-/
  sign type=numeral
"""
results = A.search(query)
A.show(results, end=2, queryFeatures=False)

# ## Search and hand-coding
#
# Now we want to find all the ShinPP numerals.

# +
shinPP = dict(
    N41=0.2,
    N04=1,
    N19=6,
    N46=60,
    N36=180,
    N49=1800,
)

shinPPPat = "|".join(shinPP)
# -

# We make use of the fact that we can construct our template.

query = f"""
tablet
  sign grapheme={shinPPPat}
"""
results = A.search(query)
A.table(results, end=20, showGraphics=True)

# Let's see a few tablets in more detail:

A.show(results, end=5, queryFeatures=False)

# ### A tablet calculator
#
# Rather than displaying search results, you can also *process* them in your program.
#
# Search results come as tuples of nodes that correspond directly to the elements
# of your search template.
#
# We query for shinPP numerals on the faces of tablets.
# The result of the query is a list of tuples `(t, f, s)` consisting of
# a tablet node, a face node and a node for a sign of a shinPP numeral.
#
# #### Rationale
# This task will require a higher level of programming skills and a deeper knowledge of how
# Python works.
# We include it in this tutorial to get the message across that Text-Fabric is not
# a black box that shields you from your data. Everything you handle in Text-Fabric is
# open to further programming and processing of your own design and choosing.

# #### Data collection

query = f"""
tablet
    face
        sign type=numeral grapheme={shinPPPat}
"""
results = A.search(query)

# We are going to put all these numerals in buckets: for each face on each tablet a separate bucket.

numerals = {}
pNums = {}
for (tablet, face, sign) in results:
    pNums[F.catalogId.v(tablet)] = tablet
    numerals.setdefault(tablet, {}).setdefault(face, []).append(sign)
print(f"{len(pNums)} tablets")
print("\n".join(list(pNums)[0:10]))
print("...")


# #### The calculator
# We define a function that given a tablet, adds the shinPP numerals by its faces.
# We also show the line art and a pretty transcription.
#
# The function is a bit involved.

# +
# we generate Markdown strings and send them to the notebook formatter


def dm(x):
    display(Markdown(x))


def calcTablet(pNum):  # pNum identifies the tablet in question
    # show a horizontal line in Markdown
    dm("---\n")
    tablet = pNums.get(pNum, None)  # look up the node for this p-number
    if tablet is None:
        dm(f"**no results for {pNum}**")
        return  # if not found the tablet has no ShinPP numerals: quit

    A.lineart(tablet, withCaption="top", width="200")  # show lineart
    faces = numerals[tablet]  # get the buckets for the faces
    mySigns = []
    for (face, signs) in faces.items():  # work per face
        mySigns.extend(signs)
        dm(f"##### {F.type.v(face)}")  # show the name of the face
        distinctSigns = {}  # collect the distinct numerals
        for s in signs:
            distinctSigns.setdefault(A.atfFromSign(s), []).append(s)
        A.lineart(distinctSigns)  # display the list of signs
        total = 0  # start adding up
        for (signAtf, signs) in distinctSigns.items():
            value = 0
            for s in signs:
                value += F.repeat.v(s) * shinPP[F.grapheme.v(s)]
            total += value
            amount = len(signs)  # we report our calculation
            shinPPval = shinPP[F.grapheme.v(signs[0])]
            repeat = F.repeat.v(signs[0])
            print(f"{amount} x {signAtf} = {amount} x {repeat} x {shinPPval} = {value}")
        dm(f"**total** = **{total}**")
    A.prettyTuple(
        [tablet] + mySigns, 1, queryFeatures=False
    )  # show pretty transcription


# -

# #### Calculate once

calcTablet("P006377")

# #### Calculate ad lib
# Now the first 5 tablets.

for tablet in sorted(pNums)[0:5]:
    calcTablet(tablet)

# ## More ...
#
# The capabilities of search are endless.
# Often it is the quickest way to focus on a phenomenon, quicker than hand coding all the logic
# to retrieve your patterns.
#
# That said, it is not a matter of either-or. You can use coding to craft your templates,
# and you can use coding to process your results.
#
# It's an explosive mix. A later chapter in this tutorial shows
# even more [cases](cases.ipynb).
#
# Have another look at
# [the manual](https://annotation.github.io/text-fabric/tf/about/searchusage.html).

# # Next
#
# [signs](signs.ipynb)
#
# *Back to the basics ...*
#
# All chapters:
# [start](start.ipynb)
# [imagery](imagery.ipynb)
# [steps](steps.ipynb)
# [search](search.ipynb)
# [signs](signs.ipynb)
# [quads](quads.ipynb)
# [jumps](jumps.ipynb)
# [cases](cases.ipynb)
#
# ---
#
# CC-BY Dirk Roorda
