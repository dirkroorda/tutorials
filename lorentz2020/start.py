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

# # Hands On with the fabric of an ancient text
#
#
# Before the hands-on session, install all of the following:
#
# ## Python
#
# Make sure Python 3.6 or higher is installed.
#
# Then install Text-Fabric and Jupyter.
#
# Do it by following the instructions in the
# [Text-Fabric docs](https://annotation.github.io/text-fabric/tf/about/install.html)
#
# ## More  libraries
#
# Install `seaborn`, a python library for graphic plots:
#
# ```
# pip install seaborn
# ```
#
# or
#
# ```
# pip3  install seaborn
# ```
#
# (if you have installed Text-Fabric you know  which)
#
# ## This tutorial
#
# If you followed the link to this tutorial, then you see its Jupyter notebooks in readonly mode.
# You cannot execute code cells.
#
# In order to compute with these notebooks, you have to download them.
#
# Here is the
#
# [zip file](https://github.com/annotation/tutorials/releases/download/v2.1/lorentz2020.zip).
#
# Unzip it, open a terminal or command prompt, navigate to the new folder, and give the command
#
# ```
# jupyter notebook
# ```
#
# Your browser starts up and presents you a local computing environment where you can run Python programs.
# You see this start notebook and several notebooks dedicated to a specific corpus.
# Click such a notebook.
#
# You see cells like the one below, where you can type programming statements and execute them by pressing `Shift Enter`.


# # Corpus
#
# The list of available corpora is [here](https://annotation.github.io/text-fabric/tf/about/corpora.html).
#
# There are hands-on guides for
#
# * [`oldbabylonian` Old Babylonian Letters](oldbabylonian.ipynb)
# * [`dss` Dead Sea Scrolls](dss.ipynb)
# * [`quran` Q'uran](quran.ipynb)
#
# Each hands-on guide takes you through the activities of browsing the corpus, searching it, and collecting
# information that cannot easily expressed as a search instruction.
#
# These three corpora differ in data features, section structure, granularity, richness of data features.
# That is why the toy problems in these hands on are different. It is worth studying all three of them.
#
# Head over to the hands-on guide corpus of your prime interest by clicking one of the three links above.
#
# These guides will let you download the corpus data.
#
# Please do that before the hands-on session.

# # Problems?
#
# If things are not going as expected, you can ask around on our Slack team
# [ancient-data](https://join.slack.com/t/ancient-data/shared_invite/enQtODk0ODUxNDE2NTc5LTZmYzlkOWI3NmVmYzEwY2RkYWRmNGMyMzQ5MzYzMTA1MDAxMDM4YTY3OWE0MDdkYzFiZGFhMjJiNjdmNWQzOWU).
