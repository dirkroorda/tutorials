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
# # Tutorial
#
# This notebook gets you started with using
# [Text-Fabric](https://annotation.github.io/text-fabric/) for coding in the Hebrew Bible.
#
# Familiarity with the underlying
# [data model](https://annotation.github.io/text-fabric/tf/about/datamodel.html)
# is recommended.
#
# Short introductions to other TF datasets:
#
# * [Dead Sea Scrolls](https://nbviewer.jupyter.org/github/annotation/tutorials/blob/master/lorentz2020/dss.ipynb),
# * [Old Babylonian Letters](https://nbviewer.jupyter.org/github/annotation/tutorials/blob/master/lorentz2020/oldbabylonian.ipynb),
# or the
# * [Q'uran](https://nbviewer.jupyter.org/github/annotation/tutorials/blob/master/lorentz2020/quran.ipynb)
#

# ## Installing Text-Fabric
#
# ### Python
#
# You need to have Python on your system. Most systems have it out of the box,
# but alas, that is python2 and we need at least python **3.6.3**.
#
# Install it from [python.org](https://www.python.org) or from
# [Anaconda](https://www.anaconda.com/download).
#
# ### TF itself
#
# ```
# pip3 install text-fabric
# ```
#
# ### Jupyter notebook
#
# You need [Jupyter](http://jupyter.org).
#
# If it is not already installed:
#
# ```
# pip3 install jupyter
# ```

# ## Tip
# If you start computing with this tutorial, first copy its parent directory to somewhere else,
# outside your `bhsa` directory.
# If you pull changes from the `bhsa` repository later, your work will not be overwritten.
# Where you put your tutorial directory is up till you.
# It will work from any directory.

# ## BHSA data
#
# Text-Fabric will fetch a standard set of features for you from the newest github release binaries.
#
# It will fetch version `c`.
#
# The data will be stored in the `text-fabric-data` in your home directory.
#

# # Features
# The data of the BHSA is organized in features.
# They are *columns* of data.
# Think of the Hebrew Bible as a gigantic spreadsheet, where row 1 corresponds to the
# first word, row 2 to the second word, and so on, for all 425,000 words.
#
# The information which part-of-speech each word is, constitutes a column in that spreadsheet.
# The BHSA contains over 100 columns, not only for the 425,000 words, but also for a million more
# textual objects.
#
# Instead of putting that information in one big table, the data is organized in separate columns.
# We call those columns **features**.

# %load_ext autoreload
# %autoreload 2

import os
import collections
from itertools import chain

# # Incantation
#
# The simplest way to get going is by this *incantation*:

from tf.app import use

# For the very last version, use `hot`.
#
# For the latest release, use `latest`.
#
# If you have cloned the repos (TF app and data), use `clone`.
#
# If you do not want/need to upgrade, leave out the checkout specifiers.

# A = use("bhsa:clone", checkout="clone", hoist=globals())
# A = use('bhsa:hot', checkout="hot", hoist=globals())
# A = use('bhsa:latest', checkout="latest", hoist=globals())
A = use('bhsa', hoist=globals())

# You can see which features have been loaded, and if you click on a feature name, you find its documentation.
# If you hover over a name, you see where the feature is located on your system.
#
# Edge features are marked by **_bold italic_** formatting.
#
# There are ways to tweak the set of features that is loaded. You can load more and less.
#
# See [share](share.ipynb) for examples.

# # Modules

# Note that we have `phono` features.
# The  BHSA data has a special 1-1 transcription from Hebrew to ASCII,
# but not a *phonetic* transcription.
#
# I have made a
# [notebook](https://github.com/etcbc/phono/blob/master/programs/phono.ipynb)
# that tries hard to find phonological representations for all the words.
# The result is a *module* in text-fabric format.
# We'll encounter that later.
#
# This module, and the module [etcbc/parallels](https://github.com/etcbc/parallels)
# are standard modules of the BHSA app.

# See the [share](share.ipynb) tutorial or [Data](https://annotation.github.io/text-fabric/tf/about/datasharing.html) how you can add and invoke additional data.

# ## API
#
# The result of the incantation is that we have a bunch of special variables at our disposal
# that give us access to the text and data of the Hebrew Bible.
#
# At this point it is helpful to throw a quick glance at the text-fabric API documentation
# (see the links under **API Members** above).
#
# The most essential thing for now is that we can use `F` to access the data in the features
# we've loaded.
# But there is more, such as `N`, which helps us to walk over the text, as we see in a minute.
#
# The **API members** above show you exactly which new names have been inserted in your namespace.
# If you click on these names, you go to the API documentation for them.

# ## Search
# Text-Fabric contains a flexible search engine, that does not only work for the BHSA data,
# but also for data that you add to it.
#
# **Search is the quickest way to come up-to-speed with your data, without too much programming.**
#
# Jump to the dedicated [search](search.ipynb) search tutorial first, to whet your appetite.
# And if you already know MQL queries, you can build from that in
# [searchFromMQL](searchFromMQL.ipynb).
#
# The real power of search lies in the fact that it is integrated in a programming environment.
# You can use programming to:
#
# * compose dynamic queries
# * process query results
#
# Therefore, the rest of this tutorial is still important when you want to tap that power.
# If you continue here, you learn all the basics of data-navigation with Text-Fabric.

# + [markdown] tags=[]
# # Counting
#
# In order to get acquainted with the data, we start with the simple task of counting.
#
# ## Count all nodes
# We use the
# [`N.walk()` generator](https://annotation.github.io/text-fabric/tf/core/nodes.html#tf.core.nodes.Nodes.walk)
# to walk through the nodes.
#
# We compared the BHSA data to a gigantic spreadsheet, where the rows correspond to the words.
# In Text-Fabric, we call the rows `slots`, because they are the textual positions that can be filled with words.
#
# We also mentioned that there are also 1,000,000 more textual objects.
# They are the phrases, clauses, sentences, verses, chapters and books.
# They also correspond to rows in the big spreadsheet.
#
# In Text-Fabric we call all these rows *nodes*, and the `N()` generator
# carries us through those nodes in the textual order.
#
# Just one extra thing: the `info` statements generate timed messages.
# If you use them instead of `print` you'll get a sense of the amount of time that
# the various processing steps typically need.

# +
A.indent(reset=True)
A.info("Counting nodes ...")

i = 0
for n in N.walk():
    i += 1

A.info("{} nodes".format(i))
# -

# Here you see it: 1,4 M nodes!

# ## What are those million nodes?
# Every node has a type, like word, or phrase, sentence.
# We know that we have approximately 425,000 words and a million other nodes.
# But what exactly are they?
#
# Text-Fabric has two special features, `otype` and `oslots`, that must occur in every Text-Fabric data set.
# `otype` tells you for each node its type, and you can ask for the number of `slot`s in the text.
#
# Here we go!

F.otype.slotType

F.otype.maxSlot

F.otype.maxNode

F.otype.all

C.levels.data

# This is interesting: above you see all the textual objects, with the average size of their objects,
# the node where they start, and the node where they end.

# ## Count individual object types
# This is an intuitive way to count the number of nodes in each type.
# Note in passing, how we use the `indent` in conjunction with `info` to produce neat timed
# and indented progress messages.

# +
A.indent(reset=True)
A.info("counting objects ...")

for otype in F.otype.all:
    i = 0

    A.indent(level=1, reset=True)

    for n in F.otype.s(otype):
        i += 1

    A.info("{:>7} {}s".format(i, otype))

A.indent(level=0)
A.info("Done")
# -

# # Viewing textual objects
#
# We use the A API (the extra power) to peek into the corpus.

# First some words.
# Node 15890 is a word with a dotless shin.
#
# Node 1002 is a word with a yod after a seqhol hataf.
#
# Node 100,000 is just a word slot.
#
# Let's inspect them and see where they are.
#
# First the plain view:

F.otype.v(1)

wordShows = (15890, 1002, 100000)
for word in wordShows:
    A.plain(word, withPassage=True)

# You can leave out the passage reference:

for word in wordShows:
    A.plain(word, withPassage=False)

# Now we show other objects, both with and without passage reference.

# +
normalShow = dict(
    wordShow=wordShows[0],
    phraseShow=700000,
    clauseShow=500000,
    sentenceShow=1200000,
    lexShow=1437667,
)

sectionShow = dict(
    verseShow=1420000,
    chapterShow=427000,
    bookShow=426598,
)
# -

for (name, n) in normalShow.items():
    A.dm(f"**{name}** = node `{n}`\n")
    A.plain(n)
    A.plain(n, withPassage=False)
    A.dm("\n---\n")

# Note that for section nodes (except verse and half-verse) the `withPassage` has little effect.
# The passage is the thing that is hyperlinked. The node is represented as a textual reference to the piece of text
# in question.

for (name, n) in sectionShow.items():
    if name == "verseShow":
        continue
    A.dm(f"**{name}** = node `{n}`\n")
    A.plain(n)
    A.plain(n, withPassage=False)
    A.dm("\n---\n")

# We can also dive into the structure of the textual objects, provided they are not too large.
#
# The function `pretty` gives a display of the object that a node stands for together with the structure below that node.

for (name, n) in normalShow.items():
    A.dm(f"**{name}** = node `{n}`\n")
    A.pretty(n)
    A.dm("\n---\n")

# Note
# * if you click on a word in a pretty display
#   you go to a page in SHEBANQ that shows a list of all occurrences of this lexeme;
# * if you click on the passage, you go to SHEBANQ, to exactly this verse.

# If you need a link to shebanq for just any node:

million = 1000000
A.webLink(million)

# We can show some standard features in the display:

for (name, n) in normalShow.items():
    A.dm(f"**{name}** = node `{n}`\n")
    A.pretty(n, standardFeatures=True)
    A.dm("\n---\n")

for (name, n) in normalShow.items():
    A.dm(f"**{name}** = node `{n}`\n")
    A.pretty(n, standardFeatures=True)
    A.dm("\n---\n")

# For more display options, see [display](display.ipynb).

# # Feature statistics
#
# `F`
# gives access to all features.
# Every feature has a method
# `freqList()`
# to generate a frequency list of its values, higher frequencies first.
# Here are the parts of speech:

F.sp.freqList()

# # Lexeme matters
#
# ## Top 10 frequent verbs
#
# If we count the frequency of words, we usually mean the frequency of their
# corresponding lexemes.
#
# There are several methods for working with lexemes.
#
# ### Method 1: counting words

# +
verbs = collections.Counter()
A.indent(reset=True)
A.info("Collecting data")

for w in F.otype.s("word"):
    if F.sp.v(w) != "verb":
        continue
    verbs[F.lex.v(w)] += 1

A.info("Done")
print(
    "".join(
        "{}: {}\n".format(verb, cnt)
        for (verb, cnt) in sorted(verbs.items(), key=lambda x: (-x[1], x[0]))[0:10]
    )
)
# -

# ### Method 2: counting lexemes
#
# An alternative way to do this is to use the feature `freq_lex`, defined for `lex` nodes.
# Now we walk the lexemes instead of the occurrences.
#
# Note that the feature `sp` (part-of-speech) is defined for nodes of type `word` as well as `lex`.
# Both also have the `lex` feature.

verbs = collections.Counter()
A.indent(reset=True)
A.info("Collecting data")
for w in F.otype.s("lex"):
    if F.sp.v(w) != "verb":
        continue
    verbs[F.lex.v(w)] += F.freq_lex.v(w)
A.info("Done")
print(
    "".join(
        "{}: {}\n".format(verb, cnt)
        for (verb, cnt) in sorted(verbs.items(), key=lambda x: (-x[1], x[0]))[0:10]
    )
)

# This is an order of magnitude faster. In this case, that means the difference between a third of a second and a
# hundredth of a second, not a big gain in absolute terms.
# But suppose you need to run this a 1000 times in a loop.
# Then it is the difference between 5 minutes and 10 seconds.
# A five minute wait is not pleasant in interactive computing!

# ### A frequency mapping of lexemes
#
# We make a mapping between lexeme forms and the number of occurrences of those lexemes.

lexeme_dict = {F.lex_utf8.v(n): F.freq_lex.v(n) for n in F.otype.s("word")}

list(lexeme_dict.items())[0:10]

# ### Real work
#
# As a primer of real world work on lexeme distribution, have a look at James Cuénod's notebook on
# [Collocation MI Analysis of the Hebrew Bible](https://nbviewer.jupyter.org/github/jcuenod/hebrewCollocations/blob/master/Collocation%20MI%20Analysis%20of%20the%20Hebrew%20Bible.ipynb)
#
# It is a nice example how you collect data with TF API calls, then do research with your own methods and tools, and then use TF for presenting results.
#
# In case the name has changed, the enclosing repo is
# [here](https://nbviewer.jupyter.org/github/jcuenod/hebrewCollocations/tree/master/).

# ## Lexeme distribution
#
# Let's do a bit more fancy lexeme stuff.
#
# ### Hapaxes
#
# A hapax can be found by inspecting lexemes and see to how many word nodes they are linked.
# If that is number is one, we have a hapax.
#
# We print 10 hapaxes with their glosses.

# +
A.indent(reset=True)

hapax = []
zero = set()

for lx in F.otype.s("lex"):
    occs = L.d(lx, otype="word")
    n = len(occs)
    if n == 0:  # that's weird: should not happen
        zero.add(lx)
    elif n == 1:  # hapax found!
        hapax.append(lx)

A.info("{} hapaxes found".format(len(hapax)))

if zero:
    A.error("{} zeroes found".format(len(zero)), tm=False)
else:
    A.info("No zeroes found", tm=False)
for h in hapax[0:10]:
    print("\t{:<8} {}".format(F.lex.v(h), F.gloss.v(h)))
# -

# ### Small occurrence base
#
# The occurrence base of a lexeme are the verses, chapters and books in which occurs.
# Let's look for lexemes that occur in a single chapter.
#
# If a lexeme occurs in a single chapter, its slots are a subset of the slots of that chapter.
# So, if you go *up* from the lexeme, you encounter the chapter.
#
# Normally, lexemes occur in many chapters, and then none of them totally includes all occurrences of it,
# so if you go up from such lexemes, you don not find chapters.
#
# Let's check it out.
#
# Oh yes, we have already found the hapaxes, we will skip them here.

# +
A.indent(reset=True)
A.info("Finding single chapter lexemes")

singleCh = []
multipleCh = []

for lx in F.otype.s("lex"):
    chapters = L.u(lx, "chapter")
    if len(chapters) == 1:
        if lx not in hapax:
            singleCh.append(lx)
    elif len(chapters) > 0:  # should not happen
        multipleCh.append(lx)

A.info("{} single chapter lexemes found".format(len(singleCh)))

if multipleCh:
    A.error(
        "{} chapter embedders of multiple lexemes found".format(len(multipleCh)),
        tm=False,
    )
else:
    A.info("No chapter embedders of multiple lexemes found", tm=False)
for s in singleCh[0:10]:
    print(
        "{:<20} {:<6}".format(
            "{} {}:{}".format(*T.sectionFromNode(s)),
            F.lex.v(s),
        )
    )
# -

# ### Confined to books
#
# As a final exercise with lexemes, lets make a list of all books, and show their total number of lexemes and
# the number of lexemes that occur exclusively in that book.

# +
A.indent(reset=True)
A.info("Making book-lexeme index")

allBook = collections.defaultdict(set)
allLex = set()

for b in F.otype.s("book"):
    for w in L.d(b, "word"):
        lx = L.u(w, "lex")[0]
        allBook[b].add(lx)
        allLex.add(lx)

A.info("Found {} lexemes".format(len(allLex)))

# +
A.indent(reset=True)
A.info("Finding single book lexemes")

singleBook = collections.defaultdict(lambda: 0)
for lx in F.otype.s("lex"):
    book = L.u(lx, "book")
    if len(book) == 1:
        singleBook[book[0]] += 1

A.info("found {} single book lexemes".format(sum(singleBook.values())))

# +
print(
    "{:<20}{:>5}{:>5}{:>5}\n{}".format(
        "book",
        "#all",
        "#own",
        "%own",
        "-" * 35,
    )
)
booklist = []

for b in F.otype.s("book"):
    book = T.bookName(b)
    a = len(allBook[b])
    o = singleBook.get(b, 0)
    p = 100 * o / a
    booklist.append((book, a, o, p))

for x in sorted(booklist, key=lambda e: (-e[3], -e[1], e[0])):
    print("{:<20} {:>4} {:>4} {:>4.1f}%".format(*x))
# -

# The book names may sound a bit unfamiliar, they are in Latin here.
# Later we'll see that you can also get them in English, or in Swahili.

# # Locality API
# We travel upwards and downwards, forwards and backwards through the nodes.
# The Locality-API (`L`) provides functions: `u()` for going up, and `d()` for going down,
# `n()` for going to next nodes and `p()` for going to previous nodes.
#
# These directions are indirect notions: nodes are just numbers, but by means of the
# `oslots` feature they are linked to slots. One node *contains* an other node, if the one is linked to a set of slots that contains the set of slots that the other is linked to.
# And one if next or previous to an other, if its slots follow or precede the slots of the other one.
#
# `L.u(node)` **Up** is going to nodes that embed `node`.
#
# `L.d(node)` **Down** is the opposite direction, to those that are contained in `node`.
#
# `L.n(node)` **Next** are the next *adjacent* nodes, i.e. nodes whose first slot comes immediately after the last slot of `node`.
#
# `L.p(node)` **Previous** are the previous *adjacent* nodes, i.e. nodes whose last slot comes immediately before the first slot of `node`.
#
# All these functions yield nodes of all possible otypes.
# By passing an optional parameter, you can restrict the results to nodes of that type.
#
# The result are ordered according to the order of things in the text.
#
# The functions return always a tuple, even if there is just one node in the result.
#
# ## Going up
# We go from the first word to the book it contains.
# Note the `[0]` at the end. You expect one book, yet `L` returns a tuple.
# To get the only element of that tuple, you need to do that `[0]`.
#
# If you are like me, you keep forgetting it, and that will lead to weird error messages later on.

firstBook = L.u(1, otype="book")[0]
print(firstBook)

# And let's see all the containing objects of word 3:

w = 3
for otype in F.otype.all:
    if otype == F.otype.slotType:
        continue
    up = L.u(w, otype=otype)
    upNode = "x" if len(up) == 0 else up[0]
    print("word {} is contained in {} {}".format(w, otype, upNode))

# ## Going next
# Let's go to the next nodes of the first book.

afterFirstBook = L.n(firstBook)
for n in afterFirstBook:
    print(
        "{:>7}: {:<13} first slot={:<6}, last slot={:<6}".format(
            n,
            F.otype.v(n),
            E.oslots.s(n)[0],
            E.oslots.s(n)[-1],
        )
    )
secondBook = L.n(firstBook, otype="book")[0]

# ## Going previous
#
# And let's see what is right before the second book.

for n in L.p(secondBook):
    print(
        "{:>7}: {:<13} first slot={:<6}, last slot={:<6}".format(
            n,
            F.otype.v(n),
            E.oslots.s(n)[0],
            E.oslots.s(n)[-1],
        )
    )

# ## Going down

# We go to the chapters of the second book, and just count them.

chapters = L.d(secondBook, otype="chapter")
print(len(chapters))

# ## The first verse
# We pick the first verse and the first word, and explore what is above and below them.

for n in [1, L.u(1, otype="verse")[0]]:
    A.indent(level=0)
    A.info("Node {}".format(n), tm=False)
    A.indent(level=1)
    A.info("UP", tm=False)
    A.indent(level=2)
    A.info("\n".join(["{:<15} {}".format(u, F.otype.v(u)) for u in L.u(n)]), tm=False)
    A.indent(level=1)
    A.info("DOWN", tm=False)
    A.indent(level=2)
    A.info("\n".join(["{:<15} {}".format(u, F.otype.v(u)) for u in L.d(n)]), tm=False)
A.indent(level=0)
A.info("Done", tm=False)

# # Text API
#
# So far, we have mainly seen nodes and their numbers, and the names of node types.
# You would almost forget that we are dealing with text.
# So let's try to see some text.
#
# In the same way as `F` gives access to feature data,
# `T` gives access to the text.
# That is also feature data, but you can tell Text-Fabric which features are specifically
# carrying the text, and in return Text-Fabric offers you
# a Text API: `T`.
#
# ## Formats
# Hebrew text can be represented in a number of ways:
#
# * fully pointed (vocalized and accented), or consonantal,
# * in transliteration, phonetic transcription or in Hebrew characters,
# * showing the actual text or only the lexemes,
# * following the ketiv or the qere, at places where they deviate from each other.
#
# If you wonder where the information about text formats is stored:
# not in the program text-fabric, but in the data set.
# It has a feature `otext`, which specifies the formats and which features
# must be used to produce them. `otext` is the third special feature in a TF data set,
# next to `otype` and `oslots`.
# It is an optional feature.
# If it is absent, there will be no `T` API.
#
# Here is a list of all available formats in this data set.

sorted(T.formats)

# Note the `text-phono-full` format here.
# It does not come from the main data source `bhsa`, but from the module `phono`.
# Look in your data directory, find `~/github/etcbc/phono/tf/2017/otext@phono.tf`,
# and you'll see this format defined there.

# ## Using the formats
#
# We can pretty display in other formats:

for word in wordShows:
    A.pretty(word, fmt="text-phono-full")

# ## T.text()
#
# This function is central to get text representations of nodes. Its most basic usage is
#
# ```python
# T.text(nodes, fmt=fmt)
# ```
# where `nodes` is a list or iterable of nodes, usually word nodes, and `fmt` is the name of a format.
# If you leave out `fmt`, the default `text-orig-full` is chosen.
#
# The result is the text in that format for all nodes specified:

T.text([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], fmt="text-orig-plain")

# There is also another usage of this function:
#
# ```python
# T.text(node, fmt=fmt)
# ```
#
# where `node` is a single node.
# In this case, the default format is *ntype*`-orig-full` where *ntype* is the type of `node`.
# So for a `lex` node, the default format is `lex-orig-full`.
#
# If the format is defined in the corpus, it will be used. Otherwise, the word nodes contained in `node` will be looked up
# and represented with the default format `text-orig-full`.
#
# In this way we can sensibly represent a lot of different nodes, such as chapters, verses, sentences, words and lexemes.
#
# We compose a set of example nodes and run `T.text` on them:

exampleNodes = [
    1,
    F.otype.s("sentence")[0],
    F.otype.s("verse")[0],
    F.otype.s("chapter")[0],
    F.otype.s("lex")[1],
]
exampleNodes

for n in exampleNodes:
    print(f"This is {F.otype.v(n)} {n}:")
    print(T.text(n))
    print("")

# ## Using the formats
# Now let's use those formats to print out the first verse of the Hebrew Bible.

for fmt in sorted(T.formats):
    print("{}:\n\t{}".format(fmt, T.text(range(1, 12), fmt=fmt)))

# Note that `lex-default` is a format that only works for nodes of type `lex`.

# If we do not specify a format, the **default** format is used (`text-orig-full`).

T.text(range(1, 12))

firstVerse = F.otype.s("verse")[0]
T.text(firstVerse)

T.text(firstVerse, fmt="text-phono-full")

# The important things to remember are:
#
# * you can supply a list of word nodes and get them represented in all formats (except `lex-default`)
# * you can use `T.text(lx)` for lexeme nodes `lx` and it will give the vocalized lexeme (using format `lex-default`)
# * you can get non-word nodes `n` in default format by `T.text(n)`
# * you can get non-word nodes `n` in other formats by `T.text(n, fmt=fmt, descend=True)`

# + [markdown] tags=[]
# ## Whole text in all formats
# Part of the pleasure of working with computers is that they can crunch massive amounts of data.
# The text of the Hebrew Bible is a piece of cake.
#
# It takes less than ten seconds to have that cake and eat it.
# In nearly a dozen formats.
# -

A.indent(reset=True)
A.info("writing plain text of whole Bible in all formats ...")
text = collections.defaultdict(list)
for v in F.otype.s("verse"):
    for fmt in sorted(T.formats):
        text[fmt].append(T.text(v, fmt=fmt, descend=True))
A.info("done {} formats".format(len(text)))

for fmt in sorted(text):
    print("{}\n{}\n".format(fmt, "\n".join(text[fmt][0:5])))

# ### The full plain text
# We write a few formats to file, in your Downloads folder.

for fmt in """
    text-orig-full
    text-phono-full
""".strip().split():
    with open(os.path.expanduser(f"~/Downloads/{fmt}.txt"), "w") as f:
        f.write("\n".join(text[fmt]))

# ## Book names
#
# For Bible book names, we can use several languages.
#
# ### Languages
# Here are the languages that we can use for book names.
# These languages come from the features `book@ll`, where `ll` is a two letter
# ISO language code. Have a look in your data directory, you can't miss them.

T.languages

# ### Book names in Swahili
# Get the book names in Swahili.

nodeToSwahili = ""
for b in F.otype.s("book"):
    nodeToSwahili += "{} = {}\n".format(b, T.bookName(b, lang="sw"))
print(nodeToSwahili)

# ## Book nodes from Swahili
# OK, there they are. We copy them into a string, and do the opposite: get the nodes back.
# We check whether we get exactly the same nodes as the ones we started with.

# +
swahiliNames = """
Mwanzo
Kutoka
Mambo_ya_Walawi
Hesabu
Kumbukumbu_la_Torati
Yoshua
Waamuzi
1_Samweli
2_Samweli
1_Wafalme
2_Wafalme
Isaya
Yeremia
Ezekieli
Hosea
Yoeli
Amosi
Obadia
Yona
Mika
Nahumu
Habakuki
Sefania
Hagai
Zekaria
Malaki
Zaburi
Ayubu
Mithali
Ruthi
Wimbo_Ulio_Bora
Mhubiri
Maombolezo
Esta
Danieli
Ezra
Nehemia
1_Mambo_ya_Nyakati
2_Mambo_ya_Nyakati
""".strip().split()

swahiliToNode = ""
for nm in swahiliNames:
    swahiliToNode += "{} = {}\n".format(T.bookNode(nm, lang="sw"), nm)

if swahiliToNode != nodeToSwahili:
    print("Something is not right with the book names")
else:
    print("Going from nodes to booknames and back yields the original nodes")
# -

# ## Sections
#
# A section in the Hebrew bible is a book, a chapter or a verse.
# Knowledge of sections is not baked into Text-Fabric.
# The config feature `otext.tf` may specify three section levels, and tell
# what the corresponding node types and features are.
#
# From that knowledge it can construct mappings from nodes to sections, e.g. from verse
# nodes to tuples of the form:
#
#     (bookName, chapterNumber, verseNumber)
#
# You can get the section of a node as a tuple of relevant book, chapter, and verse nodes.
# Or you can get it as a passage label, a string.
#
# You can ask for the passage corresponding to the first slot of a node, or the one corresponding to the last slot.
#
# If you are dealing with book and chapter nodes, you can ask to fill out the verse and chapter parts as well.
#
# Here are examples of getting the section that corresponds to a node and vice versa.
#
# **NB:** `sectionFromNode` always delivers a verse specification, either from the
# first slot belonging to that node, or, if `lastSlot`, from the last slot
# belonging to that node.

# +

for (desc, n) in chain(normalShow.items(), sectionShow.items()):
    for lang in "en la sw".split():
        d = f"{n:>7} {desc}" if lang == "en" else ""
        first = A.sectionStrFromNode(n, lang=lang)
        last = A.sectionStrFromNode(n, lang=lang, lastSlot=True, fillup=True)
        tup = (
            T.sectionTuple(n)
            if lang == "en"
            else T.sectionTuple(n, lastSlot=True, fillup=True)
            if lang == "la"
            else ""
        )
        print(f"{d:<20} {lang} - {first:<30} {last:<30} {tup}")
# -

# And here are examples to get back:

for (lang, section) in (
    ("en", "Ezekiel"),
    ("la", "Ezechiel"),
    ("sw", "Ezekieli"),
    ("en", "Isaiah 43"),
    ("la", "Jesaia 43"),
    ("sw", "Isaya 43"),
    ("en", "Deuteronomy 28:34"),
    ("la", "Deuteronomium 28:34"),
    ("sw", "Kumbukumbu_la_Torati 28:34"),
    ("en", "Job 37:3"),
    ("la", "Iob 37:3"),
    ("sw", "Ayubu 37:3"),
    ("en", "Numbers 22:33"),
    ("la", "Numeri 22:33"),
    ("sw", "Hesabu 22:33"),
    ("en", "Genesis 30:18"),
    ("la", "Genesis 30:18"),
    ("sw", "Mwanzo 30:18"),
    ("en", "Genesis 1:30"),
    ("la", "Genesis 1:30"),
    ("sw", "Mwanzo 1:30"),
    ("en", "Psalms 37:2"),
    ("la", "Psalmi 37:2"),
    ("sw", "Zaburi 37:2"),
):
    n = A.nodeFromSectionStr(section, lang=lang)
    nType = F.otype.v(n)
    print(f"{section:<30} {lang} {nType:<20} {n}")

# ## Sentences spanning multiple verses
# If you go up from a sentence node, you expect to find a verse node.
# But some sentences span multiple verses, and in that case, you will not find the enclosing
# verse node, because it is not there.
#
# Here is a piece of code to detect and list all cases where sentences span multiple verses.
#
# The idea is to pick the first and the last word of a sentence, use `T.sectionFromNode` to
# discover the verse in which that word occurs, and if they are different: bingo!
#
# We show the first 5 of ca. 900 cases.

# By the way: doing this in the `2016` version of the data yields 915 results.
# The splitting up of the text into sentences is not carved in stone!

# +
A.indent(reset=True)
A.info("Get sentences that span multiple verses")

spanSentences = []
for s in F.otype.s("sentence"):
    fs = T.sectionFromNode(s, lastSlot=False)
    ls = T.sectionFromNode(s, lastSlot=True)
    if fs != ls:
        spanSentences.append("{} {}:{}-{}".format(fs[0], fs[1], fs[2], ls[2]))

A.info("Found {} cases".format(len(spanSentences)))
A.info("\n{}".format("\n".join(spanSentences[0:10])))
# -

# A different way, with better display, is:

# +
A.indent(reset=True)
A.info("Get sentences that span multiple verses")

spanSentences = []
for s in F.otype.s("sentence"):
    words = L.d(s, otype="word")
    fw = words[0]
    lw = words[-1]
    fVerse = L.u(fw, otype="verse")[0]
    lVerse = L.u(lw, otype="verse")[0]
    if fVerse != lVerse:
        spanSentences.append((s, fVerse, lVerse))

A.info("Found {} cases".format(len(spanSentences)))
A.table(spanSentences, end=1)
# -

# Wait a second, the columns with the verses are empty.
# In tables, the content of a verse is not shown.
# And by default, the passage that is relevant to a row is computed from one of the columns.
#
# But here, we definitely want the passage of columns 2 and 3, so:

A.table(spanSentences, end=10, withPassage={2, 3})

# We can zoom in:

A.show(spanSentences, condensed=False, start=6, end=6, baseTypes={"sentence_atom"})

# # Ketiv Qere
# Let us explore where Ketiv/Qere pairs are and how they render.

# + tags=[]
qeres = [w for w in F.otype.s("word") if F.qere.v(w) is not None]
print("{} qeres".format(len(qeres)))
for w in qeres[0:10]:
    print(
        '{}: ketiv = "{}"+"{}" qere = "{}"+"{}"'.format(
            w,
            F.g_word.v(w),
            F.trailer.v(w),
            F.qere.v(w),
            F.qere_trailer.v(w),
        )
    )
# -

# ## Show a ketiv-qere pair
# Let us print all text representations of the verse in which the second qere occurs.

refWord = qeres[1]
print(f"Reference word is {refWord}")
vn = L.u(refWord, otype="verse")[0]
print("{} {}:{}".format(*T.sectionFromNode(refWord)))
for fmt in sorted(T.formats):
    if fmt.startswith("text-"):
        print("{:<25} {}".format(fmt, T.text(vn, fmt=fmt, descend=True)))

# # Edge features: mother
#
# We have not talked about edges much. If the nodes correspond to the rows in the big spreadsheet,
# the edges point from one row to another.
#
# One edge we have encountered: the special feature `oslots`.
# Each non-slot node is linked by `oslots` to all of its slot nodes.
#
# An edge is really a feature as well.
# Whereas a node feature is a column of information,
# one cell per node,
# an edge feature is also a column of information, one cell per pair of nodes.
#
# Linguists use more relationships between textual objects, for example:
# linguistic dependency.
# In the BHSA all cases of linguistic dependency are coded in the edge feature `mother`.
#
# Let us do a few basic enquiry on an edge feature:
# [mother](https://etcbc.github.io/bhsa/features/hebrew/2017/mother).
#
# We count how many mothers nodes can have (it turns to be 0 or 1).
# We walk through all nodes and per node we retrieve the mother nodes, and
# we store the lengths (if non-zero) in a dictionary (`mother_len`).
#
# We see that nodes have at most one mother.
#
# We also count the inverse relationship: daughters.

# +
A.indent(reset=True)
A.info("Counting mothers")

motherLen = {}
daughterLen = {}

for c in N.walk():
    lms = E.mother.f(c) or []
    lds = E.mother.t(c) or []
    nms = len(lms)
    nds = len(lds)
    if nms:
        motherLen[c] = nms
    if nds:
        daughterLen[c] = nds

A.info("{} nodes have mothers".format(len(motherLen)))
A.info("{} nodes have daughters".format(len(daughterLen)))

motherCount = collections.Counter()
daughterCount = collections.Counter()

for (n, lm) in motherLen.items():
    motherCount[lm] += 1
for (n, ld) in daughterLen.items():
    daughterCount[ld] += 1

print("mothers", motherCount)
print("daughters", daughterCount)
# -

# # Clean caches
#
# Text-Fabric pre-computes data for you, so that it can be loaded faster.
# If the original data is updated, Text-Fabric detects it, and will recompute that data.
#
# But there are cases, when the algorithms of Text-Fabric have changed, without any changes in the data, that you might
# want to clear the cache of precomputed results.
#
# There are two ways to do that:
#
# * Locate the `.tf` directory of your dataset, and remove all `.tfx` files in it.
#   This might be a bit awkward to do, because the `.tf` directory is hidden on Unix-like systems.
# * Call `TF.clearCache()`, which does exactly the same.
#
# It is not handy to execute the following cell all the time, that's why I have commented it out.
# So if you really want to clear the cache, remove the comment sign below.

# +
# TF.clearCache()
# -

# # All steps
#
# By now you have an impression how to compute around in the Hebrew Bible.
# While this is still the beginning, I hope you already sense the power of unlimited programmatic access
# to all the bits and bytes in the data set.
#
# Here are a few directions for unleashing that power.
#
# * **start** your first step in mastering the bible computationally
# * **[display](display.ipynb)** become an expert in creating pretty displays of your text structures
# * **[search](search.ipynb)** turbo charge your hand-coding with search templates
# * **[exportExcel](exportExcel.ipynb)** make tailor-made spreadsheets out of your results
# * **[share](share.ipynb)** draw in other people's data and let them use yours
# * **[export](export.ipynb)** export your dataset as an Emdros database
# * **[annotate](annotate.ipynb)** annotate plain text by means of other tools and import the annotations as TF features
# * **[volumes](volumes.ipynb)** work with selected books only
# * **[trees](trees.ipynb)** work with the BHSA data as syntax trees
#
# CC-BY Dirk Roorda
