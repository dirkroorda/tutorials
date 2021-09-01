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

# <img align="right" src="images/tf-small.png" width="128"/>
# <img align="right" src="images/phblogo.png" width="128"/>
# <img align="right" src="images/dans.png"/>
#
# ---
# Start with [convert](https://nbviewer.jupyter.org/github/annotation/banks/blob/master/programs/convert.ipynb)
#
# ---

# # Compose
#
# This is about combining multiple TF datasets into one, and then tweaking it further.
#
# In the previous chapters of this tutorial you have learned how to add new features to an existing dataset.
#
# Here you learn how you can combine dozens of slightly heterogeneous TF data sets,
# and apply structural tweaks to the node types and features later on.
#
# The incentive to write these composition functions into Text-Fabric came from Ernst Boogert while he was
# converting between 100 and 200 works by the Church Fathers (Patristics).
# The conversion did a very good job in getting all the information from TEI files with different structures into TF,
# one dataset per work.
#
# Then the challenge became to combine them into one big dataset, and to merge several node types into one type,
# and several features into one.
#
# See [patristics](https://github.com/pthu/patristics).

# %load_ext autoreload
# %autoreload 2

# The new functions are `combine()` and `modify()`.

from tf.fabric import Fabric
from tf.compose import combine, modify

# ## Corpus
#
# We use two copies of our example corpus Banks, present in this repository.

# ## Combine
#
# The combine function takes any number of directory locations, and considers each location to be the
# host of a TF data set.
#
# You can pass this list straight to the `combine()` function as the `locations` parameter,
# or you can add names to the individual corpora.
# In that case, you pass an iterable of (`name`, `location`) pairs into the `locations` parameter.
#
# Here we give the first copy the name `banks`, and the second copy the name `river`.
#
# We also specify the output location.

# +
PREFIX = "combine/input"
SUFFIX = "tf/0.2"

locations = (
    ("banks", f"{PREFIX}/banks1/{SUFFIX}"),
    ("rivers", f"{PREFIX}/banks2/{SUFFIX}"),
)

COMBINED = "combine/_temp/riverbanks"
# -

# We are going to call the `combine()` function.
#
# But first we clear the output location.
#
# Note how you can mix a bash-shell command with your Python code.

# +
output = COMBINED

# !rm -rf {output}

combine(
    locations,
    output,
    componentType="volume",
    componentFeature="title",
    featureMeta=dict(
        otext=dict(
            sectionTypes="volume,chapter,line",
            sectionFeatures="title,number,number",
            **{"fmt:text-orig-full": "{letters} "},
        ),
    ),
)
# -

# This function is a bit verbose in its output, but a lot happens under the hood, and if your dataset is large,
# it may take several minutes. It is pleasant to see the progress under those circumstances.
#
# But for now, we pass `silent=True`, to make everything a bit more quiet.

# +
output = COMBINED

# !rm -rf {output}

combine(
    locations,
    output,
    componentType="volume",
    componentFeature="title",
    featureMeta=dict(
        otext=dict(
            sectionTypes="volume,chapter,line",
            sectionFeatures="title,number,number",
            **{"fmt:text-orig-full": "{letters} "},
        ),
    ),
    silent=True,
)
# -

# There you are, on your file system you see the combined dataset:

# !ls  -l {output}

# If we compare that with one of the input:

# !ls -l {PREFIX}/banks1/{SUFFIX}

# then we see the same sizes but smaller file sizes.
#
# ## Result
#
# Let's have a look inside, and note that we use the new TF function `loadAll()`
# which loads all loadable features.

TF = Fabric(locations=COMBINED)
api = TF.loadAll(silent=False)
docs = api.makeAvailableIn(globals())

# We look up the section of the first word:

TF.loadLog()

T.sectionFromNode(1)

# The component sets had 99 words each. So what is the section of word 100?

T.sectionFromNode(100)

# Right, that's the first word of the second component.
#
# Here is an overview of all the node types in the combined set.
#
# The second field is the average length in words for nodes of that type, the remaining fields give
# the first and last node of that type.

C.levels.data

# The combined data set consists of the concatenation of all slot nodes of the component data sets.
#
# Note that the individual components have got a top node, of type `volume`.
# This is the effect of specifying `componentType='volume'`.
#
# There is also a feature for volumes, named `title`, that contains their name, or if we haven't passed their names
# in the `locations` parameter, their location.
# This is the effect of `componentFeature='title'`.
#
# Let's check.
#
# We use the new `.items()` method on features.

F.title.items()

# We see several things:
#
# * the volume nodes indeed got the component name in the feature `title`
# * the other nodes that already had a title, the `book` nodes, still have the same value for `title` as before.
#
# ### The merging principle
#
# This is a general principle that we see over and over again: when we combine data, we merge as much as possible.
#
# That means that when you  create new features, you may use the names of old features, and the new information for that
# feature will be merged with the old information of that feature.

# ## Modify
#
# Although combining has its complications, the most complex operation is `modify()` because it can do many things.
#
# It operates on a single TF dataset, and it produces a modified dataset as a fresh "copy".
#
# Despite the name, no actual modification takes place on the input dataset.

# +
location = f"{PREFIX}/banks1/{SUFFIX}"

MODIFIED = "_temp/mudbanks"
# -

# Now we take the first local copy of the Banks dataset as  our input, for a lot of different operations.

# Here is the list what `modify()` can do.
# The order is important, because all operations are executed in this order:
#
# 1. **merge features**: several input features are combined into a single output feature and then deleted;
# 2. **delete features**: several features are be deleted
# 3. **add features**: several node/edge features with their data are added to the dataset
# 4. **merge types**: several input node types are combined into a single output node type;
#    the input nodetypes are deleted, but not their nodes: they are now part of the output node type;
# 5. **delete types**: several node types are deleted, *with their nodes*, and all features
#    will be remapped to accomodate for this;
# 6. **add types**: several new node types with additional feature data for them are added after the last node;
#    features do not have to be remapped for this; the new node types may be arbitrary intervals of integers and
#    have no relationship with the existing nodes.
# 7. **modify metadata**: the metadata of all features can be tweaked, including everything that is in the
#    `otext` feature, such as text formats and section structure definitions.
#
# Modify will perform as many sanity checks as possible before it starts working, so that the chances are good that
# the modified dataset will load properly.
# It will adapt the value type of features to the values encountered, and it will deduce whether edges have values or not.
#
# If a modified dataset does not load, while the original dataset did load, it is a bug, and I welcome a
# [GitHub issue](https://github.com/annotation/text-fabric/issues)
# for it.

# ### Only meta data
#
# We start with the last one, the most simple one.

otext = dict(
    sectionTypes="book,chapter",
    sectionFeatures="title,number",
    **{"fmt:text-orig-full": "{letters} "},
)

# We use `silent=True` from now on, but if you work with larger datasets, it is recommended to set `silent=False` or
# to leave it out altogether.

# +
test = "meta"
output = f"{MODIFIED}.{test}"

# !rm -rf {output}

modify(
    location,
    output,
    featureMeta=dict(otext=otext),
    silent=True,
)
# -

# #### Result

TF = Fabric(locations=f"{MODIFIED}.{test}", silent=True)
api = TF.loadAll(silent=True)
docs = api.makeAvailableIn(globals())

# We have now only 2 section levels. If we ask for some sections, we see that we only get 2 components in the tuple.

T.sectionFromNode(1)

T.sectionFromNode(99)

# ### Merge features
#
# We are going to do some tricky mergers on features that are involved in the section structure and the
# text formats, so we take care to modify those by means of the `featureMeta` parameter.

otext = dict(
    sectionTypes="book,chapter",
    sectionFeatures="heading,heading",
    structureTypes="book,chapter",
    structureFeatures="heading,heading",
    **{
        "fmt:text-orig-full": "{content} ",
        "fmt:text-orig-fake": "{fake} ",
        "fmt:line-default": "{content:XXX}{terminator} ",
    },
)

# We want sectional headings in one feature, `heading`, instead of in `title` for books and `number` for chapters.
#
# We also make a `content` feature that gives the `letters` of a word unless there is punctuation: then it gives `punc`.
#
# And we make the opposite: `fake`: it prefers `punc` over `letters`.
#
# Note that `punc` and `letters` will be deleted after the merge as a whole is completed, so that it is indeed
# possible for features to be the input of multiple mergers.

# +
test = "merge.f"
output = f"{MODIFIED}.{test}"

# !rm -rf {output}

modify(
    location,
    output,
    mergeFeatures=dict(
        heading=("title number"), content=("punc letters"), fake=("letters punc")
    ),
    featureMeta=dict(
        otext=otext,
    ),
    silent=True,
)
# -

# #### Result

TF = Fabric(locations=f"{MODIFIED}.{test}", silent=True)
api = TF.loadAll(silent=True)
docs = api.makeAvailableIn(globals())

# We inspect the new `heading` feature for a book and a chapter.

b = F.otype.s("book")[0]
F.heading.v(b)

c = F.otype.s("chapter")[0]
F.heading.v(c)

# And here is an overview of all node features: `title` and `number` are gone, together with `punc` and `letters`.

Fall()

# We have modified the standard text format, `text-orig-full`. It now uses the `content` feature,
# and indeed, we do not see punctuation anymore.

T.text(range(1, 10))

# On the other hand, `text-orig-fake` uses the `fake` feature, and we see that the words in front
# of punctuation have disappeared.

T.text(range(1, 10), fmt="text-orig-fake")

# ### Delete features
#
# We just remove two features from the dataset: `author` and `terminator`.

# +
test = "delete.f"
output = f"{MODIFIED}.{test}"

# !rm -rf {output}

modify(
    location,
    output,
    deleteFeatures="author terminator",
    silent=True,
)
# -

# Oops. `terminator` is used in a text-format, so if we delete it, the dataset will not load properly.
#
# Let's not delete `terminator` but `gap`.

# +
test = "delete.f"
output = f"{MODIFIED}.{test}"

modify(
    location,
    output,
    deleteFeatures="author gap",
    silent=True,
)
# -

# #### Result

TF = Fabric(locations=f"{MODIFIED}.{test}", silent=True)
api = TF.loadAll(silent=True)
docs = api.makeAvailableIn(globals())

Fall()

# Indeed, `gap` is gone.

F.gap.freqList()

# I told you! Sigh ...

# ### Add features
#
# We add a bunch of node features and edge features.
#
# When you add features, you also have to pass their data.
# Here we compute that data in place, which results in a lengthy call, but usually you'll get
# that data from somewhere in a dictionary, and you only pass the dictionary.

# We do not have to explicitly tell the value types of the new features, `modify()` will deduced them.
# We can override that by passing a value type explicitly.
#
# Let's declare `lemma` to be `str`, and `big` `int`:

# +
test = "add.f"
output = f"{MODIFIED}.{test}"

# !rm -rf {output}

modify(
    location,
    output,
    addFeatures=dict(
        nodeFeatures=dict(
            author={101: "Banks Jr.", 102: "Banks Sr."},
            lemma={n: 1000 + n for n in range(1, 10)},
            small={n: chr(ord("a") + n % 26) for n in range(1, 10)},
            big={n: chr(ord("A") + n % 26) for n in range(1, 10)},
        ),
        edgeFeatures=dict(
            link={n: {n + i for i in range(1, 3)} for n in range(1, 10)},
            similarity={
                n: {n + i: chr(ord("a") + (i + n) % 26) for i in range(1, 3)}
                for n in range(1, 10)
            },
        ),
    ),
    featureMeta=dict(
        lemma=dict(
            valueType="str",
        ),
        big=dict(
            valueType="int",
        ),
    ),
    silent=True,
)
# -

# We get away with `lemma` as string, because everything that is written is also a string.
# But not all values of `big` are numbers, so: complaint.
#
# Let's stick to the default:

# +
test = "add.f"
output = f"{MODIFIED}.{test}"

# !rm -rf {output}

modify(
    location,
    output,
    addFeatures=dict(
        nodeFeatures=dict(
            author={101: "Banks Jr.", 102: "Banks Sr."},
            lemma={n: 1000 + n for n in range(1, 10)},
            small={n: chr(ord("a") + n % 26) for n in range(1, 10)},
            big={n: chr(ord("A") + n % 26) for n in range(1, 10)},
        ),
        edgeFeatures=dict(
            link={n: {n + i for i in range(1, 3)} for n in range(1, 10)},
            similarity={
                n: {n + i: chr(ord("a") + (i + n) % 26) for i in range(1, 3)}
                for n in range(1, 10)
            },
        ),
    ),
    silent=True,
)
# -

# #### Result

TF = Fabric(locations=f"{MODIFIED}.{test}", silent=True)
api = TF.loadAll(silent=True)
docs = api.makeAvailableIn(globals())

Fall()

Eall()

# We see the extra features, and let's just enumerate their mappings.
#
# `link` is an edge feature where edges do not have values.
# So for each `n`, the result is a set of nodes.

E.link.items()

# `similarity` assigns values to the edges. So for each `n`, the result is a mapping from nodes to values.

E.similarity.items()

E.similarity.f(1)

# Now the node features.

F.author.items()

F.small.items()

F.big.items()

F.lemma.items()

# ### Merge types
#
# Manipulating features is relatively easy. But when we fiddle with the node types, we need our wits about us.
#
# In this example, we first do a feature merge of `title` and `number` into `nm`.
#
# Then we merge the `line` and `sentence` types into a new type `rule`.
#
# And `book` and `chapter` will merge into `section`.
#
# We adapt our section structure so that it makes use of the new features and types.

# +
test = "merge.t"
output = f"{MODIFIED}.{test}"

# !rm -rf {output}

modify(
    location,
    output,
    mergeFeatures=dict(nm="title number"),
    mergeTypes=dict(
        rule=dict(
            line=dict(
                type="line",
            ),
            sentence=dict(
                type="sentence",
            ),
        ),
        section=dict(
            book=dict(
                type="book",
            ),
            chapter=dict(
                type="chapter",
            ),
        ),
    ),
    featureMeta=dict(
        otext=dict(
            sectionTypes="section,rule",
            sectionFeatures="nm,nm",
            structureTypes="section",
            structureFeatures="nm",
        ),
    ),
    silent=True,
)
# -

# #### Result

TF = Fabric(locations=f"{MODIFIED}.{test}", silent=True)
api = TF.loadAll(silent=True)
docs = api.makeAvailableIn(globals())

# We expect a severy reduced inventory of node types:

C.levels.data

Fall()

# ### Delete types
#
# We delete the `line` and `sentence` types.

# +
test = "delete.t"
output = f"{MODIFIED}.{test}"

# !rm -rf {output}

modify(
    location,
    output,
    deleteTypes="sentence line",
    silent=True,
)
# -

# But, again, we can't do that because they are important for the text API.
#
# This time, we change the text API, so that it does not need them anymore.

# +
test = "delete.t"
output = f"{MODIFIED}.{test}"

modify(
    location,
    output,
    deleteTypes="sentence line",
    featureMeta=dict(
        otext=dict(
            sectionTypes="book,chapter",
            sectionFeatures="title,number",
            structureTypes="book,chapter",
            structureFeatures="title,number",
        ),
    ),
    silent=True,
)
# -

# #### Result

TF = Fabric(locations=f"{MODIFIED}.{test}", silent=True)
api = TF.loadAll(silent=True)
docs = api.makeAvailableIn(globals())

C.levels.data

# As expected.

# ### Add types
#
# Adding types involves a lot of data, because we do not only add nodes, but also features about those nodes.
#
# The idea is this:
#
# Suppose that somewhere in another dataset, you have found lexeme nodes for the words in your data set.
#
# You just take those lexeme features, which may range from 100,000 to 110,000 say, and you find a way to map them to your
# words, by means of a map `nodeSlots`.
#
# Then you can just grab those lexeme functions *as they are*, and pack them into the `addTypes` argument,
# together with the `nodeSlots` and the node boundaries (100,000 - 110,000).
#
# The new feature data is not able to say something about nodes in the input data set, because the new nodes will be shifted
# so that they are past the `maxNode` of your input data set.
# And if your feature data accidentally addresses nodes outside the declared range, those assignments will be ignored.
#
# So all in all, it is a rather clean addition of material.
#
# Maybe a bit too clean, because it is also impossible to add edge features that link the new nodes to the old nodes.
# But then, it would be devilishly hard to make sure that after the necessary remapping of the edge features,
# they address the intended nodes.
#
# If you do want edge features between old and new nodes, it is better to compute them in the new dataset and add them
# as an individual feature or by another call to `modify()`.
#
# Let's have a look at an example where we add a type `bis` consisting of a few bigrams, and a type `tris`,
# consisting of a bunch `trigrams`.
#
# We just furnish a slot mapping for those nodes, and give them a `name` feature.

# +
test = "add.t"
output = f"{MODIFIED}.{test}"

# !rm -rf {output}

modify(
    location,
    output,
    addTypes=dict(
        bis=dict(
            nodeFrom=1,
            nodeTo=5,
            nodeSlots={
                1: {10, 11},
                2: {20, 21},
                3: {30, 31},
                4: {40, 41},
                5: {50, 51},
            },
            nodeFeatures=dict(
                name={
                    1: "b1",
                    2: "b2",
                    3: "b3",
                    4: "b4",
                    5: "b5",
                },
            ),
            edgeFeatures=dict(
                link={
                    1: {2: 100, 3: 50, 4: 25},
                    2: {3: 50, 4: 25, 5: 12},
                    3: {4: 25, 5: 12},
                    4: {5: 12, 1: 6},
                    5: {1: 6, 2: 3, 4: 1},
                },
            ),
        ),
        tris=dict(
            nodeFrom=1,
            nodeTo=4,
            nodeSlots={
                1: {60, 61, 62},
                2: {70, 71, 72},
                3: {80, 81, 82},
                4: {90, 91, 94},
            },
            nodeFeatures=dict(
                name={
                    1: "tr1",
                    2: "tr2",
                    3: "tr3",
                    4: "tr4",
                },
            ),
            edgeFeatures=dict(
                sim={
                    1: {2, 3, 4},
                    2: {3, 4},
                    3: {4},
                    4: {5, 1},
                },
            ),
        ),
    ),
    silent=True,
)
# -

# #### Result

TF = Fabric(locations=f"{MODIFIED}.{test}", silent=True)
api = TF.loadAll(silent=True)
docs = api.makeAvailableIn(globals())

C.levels.data

# There are the `bis` and `tris`!

Fall()

# And there is the new feature `name`:

sorted(F.name.items())

Eall()

# And the new edge features `link` and `sim`:

sorted(E.link.items())

sorted(E.sim.items())

# And that is all for now.
#
# Incredible that you made it till here!

# ---
# All chapters:
#
# * [use](use.ipynb)
# * [share](share.ipynb)
# * [app](app.ipynb)
# * [repo](repo.ipynb)
# * *compose*
#
# ---
