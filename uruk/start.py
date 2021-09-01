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
# # Start
#
# This notebook gets you started with using
# [Text-Fabric](https://github.com/Nino-cunei/uruk/blob/master/docs/textfabric.md) for coding in cuneiform tablet transcriptions.
#
# Familiarity with the underlying
# [data model](https://annotation.github.io/text-fabric/tf/about/datamodel.html)
# is recommended.
#
# For provenance, see the documentation:
# [about](https://github.com/Nino-cunei/uruk/blob/master/docs/about.md).

# ## Overview
#
# * we tell you how to get Text-Fabric on your system;
# * we tell you how to get the Uruk IV-III corpus on your system.

# ## Installing Text-Fabric
#
# ### Python
#
# You need to have Python on your system. Most systems have it out of the box,
# but alas, that is python2 and we need at least python **3.6**.
#
# Install it from [python.org](https://www.python.org) or from
# [Anaconda](https://www.anaconda.com/download).
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
#
# ### TF itself
#
# ```
# pip3 install text-fabric
# ```

# ### Get the data
#
# Text-Fabric will get the data for you and store it on your system.
#
# If you have cloned the github repo with the data,
# [Nino-cunei/uruk](https://github.com/Nino-cunei/uruk),
# your data is already in place, and nothing will be downloaded.
#
# Otherwise, on first run, Text-Fabric will load the data and store it in the folder
# `text-fabric-data` in your home directory.
# This only happens if the data is not already there.
#
# Not only transcription data will be downloaded, also linearts and photos.
# These images are contained in a zipfile of 550 MB,
# so take care that you have a good internet connection when it comes to downloading the images.

# ## Start the engines
#
# Navigate to this directory in a terminal and say
#
# ```
# jupyter notebook
# ```
#
# (just literally).
#
# Your browser opens with a directory view, and you'll see `start.ipynb`.
# Click on it. A new browser tab opens, and a Python engine has been allocated to this
# notebook.
#
# Now we are ready to compute .
# The next cell is a code cell that can be executed if you have downloaded this
# notebook and have issued the `jupyter notebook` command.
#
# You execute a code cell by standing in it and press `Shift Enter`.

# ### The code

# %load_ext autoreload
# %autoreload 2

import sys, os
from tf.app import use

# View the next cell as an *incantation*.
# You just have to say it to get things underway.

# For the very last version, use `hot`.
#
# For the latest release, use `latest`.
#
# If you have cloned the repos (TF app and data), use `clone`.
#
# If you do not want/need to upgrade, leave out the checkout specifiers.

A = use("uruk:clone", checkout="clone", hoist=globals())
# A = use('uruk:hot', checkout="hot", hoist=globals())
# A = use('uruk:latest', checkout="latest", hoist=globals())
# A = use('uruk', hoist=globals())

# ### The output
#
# The output shows some statistics about the images found in the Uruk data.
#
# Then there are links to the documentation.
#
# **Tip:** open them, and have a quick look.
#
# Every notebook that you set up with `Cunei` will have such links.
#
# **GitHub and NBViewer**
#
# If you have made your own notebook, and used this incantation,
# and pushed the notebook to GitHub, links to the online version
# of *your* notebook on GitHub and NBViewer will be generated and displayed.
#
# By the way, GitHub shows notebooks nicely.
# Sometimes NBViewer does it better, although it fetches exactly the same notebook from GitHub.
#
# NBViewer is handy to navigate all the notebooks of a particular organization.
# Try the [Nino-cunei starting point](http://nbviewer.jupyter.org/github/Nino-cunei/).
#
# These links you can share with colleagues.

# ## Test
#
# We perform a quick test to see that everything works.
#
# ### Count the signs
#
# We count how many signs there are in the corpus.
# In a next notebook we'll explain code like this.

len(F.otype.s("sign"))

# ### Show photos and lineart
#
# We show the photo and lineart of a tablet, to whet your appetite.

example = T.nodeFromSection(("P005381",))

A.photo(example)

# Note that you can click on the photo to see a better version on CDLI.
#
# Here comes the lineart:

A.lineart(example)

# A pretty representation of the transcription with embedded lineart for quads and signs:

A.pretty(example, withNodes=True)

# We can suppress the lineart:

A.pretty(example, showGraphics=False)

# The transliteration:

A.getSource(example)

# Now the lines ans cases of this tablet in a table:

table = []
for sub in L.d(example):
    if F.otype.v(sub) in {"line", "case"}:
        table.append((sub,))

A.table(table, showGraphics=False)

# We can include the lineart in plain displays:

A.table(table, showGraphics=True)

# This is just the beginning.
#
# In the next chapters we show you how to
# * fine-tune tablet displays,
# * step and jump around in the corpus,
# * search for patterns,
# * drill down to quads and signs,
# * and study frequency distributions of signs in subcases.

# # Next
#
# [imagery](imagery.ipynb)
#
# *Get the big picture ...*
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
