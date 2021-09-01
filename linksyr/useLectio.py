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

# <img align="right" src="images/tf.png" width="128"/>
# <img align="right" src="images/etcbc.png" width="128"/>
# <img align="right" src="images/syrnt.png" width="128"/>
# <img align="right" src="images/peshitta.png" width="128"/>
#
# # Use lectionaries in the Peshitta (OT and NT)
#
# This notebook shows just one way to use the Syriac Lectionary data by Geert Jan Veldman
# together with the Peshitta texts, OT and NT.
#
# It has been used in the Syriac Bootcamp at the ETCBC, VU Amsterdam, on 2019-01-18.
#
# ## Provenance
#
# The lectionary data can be downloaded from the
# [DANS archive](https://dans.knaw.nl/en/front-page?set_language=en)
# through this DOI:
# [10.17026/dans-26t-hhv7](https://doi.org/10.17026/dans-26t-hhv7).
#
# The Peshitta (OT) and (NT) text sources in text-fabric format are on GitHub:
#
# * OT: [etcbc/peshitta](https://github.com/ETCBC/peshitta)
# * NT: [etcbc/syrnt](https://github.com/ETCBC/syrnt)
#
# The program that generated the text-fabric features linking the lectionaries with the text is in 
# a Jupyter notebook:
#
# * [makeLectio](https://nbviewer.jupyter.org/github/etcbc/linksyr/blob/master/programs/lectionaries/makeLectio.ipynb)
#
# ## Run it yourself!
#
# Make sure you have installed 
#
# * Python (3.6.3 or higher)
# * Jupyter
#
#   ```pip3 install jupyter```
# * Text-Fabric
#
#   ```pip3 install text-fabric```
#
# If you have already installed text-fabric before, make sure to do
#
# ```pip3 install --upgrade text-fabric```
#
# because Text-Fabric is in active development every now and then.

# %load_ext autoreload
# %autoreload 2

import os
import re
from tf.app import use

# # Context
#
# We will be working with two TF data sources,
#
# * the `peshitta`, (OT Peshitta) which name we store in variable `P`
# * the `syrnt`, (NT Peshitta) which name we store in variable `S`
#
# They both contain Syriac text and transcriptions, but the SyrNT has linguistic annotations and lexemes, while the
# Peshitta (OT) lacks them.

P = 'peshitta'
S = 'syrnt'
A = {P: None, S: None}

# # Text-Fabric browser
#
# Let's first look at the data in your own browser.
#
# What you need to do is to open a command prompt.
# If you do not know what that is: on Windows it is the program `cmd.exe`, on the Mac it is the app called `Terminal`, 
# and on Linux you know what it is.
#
# You can use it from any directory.
#
# If one of the commands below do not work, you have installed things differently than I assume here, or the installation was not succesful.
# For more information, consult 
# [Install](https://annotation.github.io/text-fabric/tf/about/install.html) and/or
# [FAQ](https://annotation.github.io/text-fabric/tf/about/faq.html)

# Start the TF browser as follows:
#
# ### Old Testament
#
# ```
# text-fabric peshitta -c --mod=etcbc/linksyr/data/tf/lectio/peshitta
# ```
#
# ### New Testament
#
# Open a new command prompt and say there:
#
# ```
# text-fabric syrnt -c --mod=etcbc/linksyr/data/tf/lectio/syrnt
# ```
#
# ### Example queries
#
# In both cases, issue a query such as
#
# ```
# verse taksa link
# ```
#
# or a more refined one:
#
# ```
# verse taksa link
#   word word_etcbc=LLJ>
# ```
#
#
# You will see all verses that are associated with a lectionary that has a `taksa` and a `link` value.

# After playing around with the browsing interface on both testaments, return to this notebook.

# We are going to load both texts here in our program:

for volume in A:
  A[volume] = use(volume+':clone', mod=f'etcbc/linksyr/data/tf/lectio/{volume}')

# Above you can see that we have loaded the `peshitta` and `syrnt` data sources but also additional data from
#
# * **etcbc/linksyr/data/tf/lectio/peshitta**
# * **etcbc/linksyr/data/tf/lectio/syrnt**

# From both additional sources we have loaded several features: `lectio`, `mark1`, `mark2`, `siglum`, `taksa`, `taksaTr`.
#
# Every lectionary has a number. A lectionary is linked to several verses.
#
# Here is what kind of information the features contain:
#
# feature | description
# --- | ---
# **lectio** | comma separated list of numbers of lectionaries associated with this verse
# **mark1** | comma separated list of words which mark the precise location of where the lectionaries start
# **taksa** | newline separated list of liturgical events associated with the lectionaries (in Syriac)
# **taksaTr** | same as **taksa**, but now in English
# **siglum** | newline separated list of document references that mention specify the lectionary
# **link** | newline separated list of links to the *sigla*
# **mark2** | same as **mark2**, but the word is in a different language

# When you work with TF, you usually have handy variables called `F`, `L`, `T` ready with which you access all data in the text.
#
# Since we use two TF resources in this program, we make a double set of these variables, and instead of just `F`, we'll say
# `F[P]` for accessing the Peshitta (OT) and `F[S]` for accessing the SyrNT. Same pattern for `L` and `T`.
#
# For the meaning of these variables, consult
#
# * [F Features](https://annotation.github.io/text-fabric/tf/core/nodefeature.html)
# * [L Locality](https://annotation.github.io/text-fabric/tf/core/locality.html)
# * [T Text](https://annotation.github.io/text-fabric/tf/core/text.html)

# +
Fs = {}
F = {}
T = {}
L = {}

for volume in A:
  thisApi = A[volume].api
  F[volume] = thisApi.F
  Fs[volume] = thisApi.Fs
  T[volume] = thisApi.T
  L[volume] = thisApi.L
# -

extraFeatures = '''
  lectio
  mark1 mark2
'''.strip().split()


# # Liturgicalness
#
# We measure the *liturgicalness* of a word by counting the number of lectionaries it is involved in.
#
# As a first step, we collect for each words the set of lectionaries it is involved in.
#
# In the Peshitta OT we use the word form, since we do not have lemmas.
# The word form is in the feature `word`.
#
# In the SyrNT we use the word lemma, which is in the feature `lexeme`.
#
# We collect the information in the dictionary `liturgical`, which maps each word form unto the set of lectionaries it is involved in.

# +
# this function can do the collection in either Testament

def getLiturgical(volume):
  wordRep = 'word' if volume == P else 'lexeme'
  mapping = {}

  # we traverse all verse nodes
  for verseNode in F[volume].otype.s('verse'):
    # we retrieve the value of feature 'lectio' for that verse node
    lectioStr = F[volume].lectio.v(verseNode)
    if lectioStr:
      # we split the lectio string into a set of individual lectio numbers
      lectios = lectioStr.split(',')
      
      # we descend into the words of the verse
      for wordNode in L[volume].d(verseNode, otype='word'):
        # we use either the feature 'word' or 'lexeme', depending on the volume
        word = Fs[volume](wordRep).v(wordNode)
        
        # if this is the first time we encounter the word,
        # we add it to the mapping and give it a start value: the empty set 
        if word not in mapping:
          mapping[word] = set()
        # in any case, we add the new found lectio numbers to the existing set for this word
        mapping[word] |= set(lectios)
        
  # we report how many words we have collected
  print(f'Found {len(mapping)} words in {volume}')
  
  # we return the mapping as result
  return mapping


# -

# Before we call the function above for Peshitta and SyrNT, we make a place where the results can land:

liturgical = {}

for volume in A:
  liturgical[volume] = getLiturgical(volume)

# Remember that we count word occurrences in the Peshitta, and lemmas in the SyrNT, so we get much smaller numbers for the NT.

# Let's show some mapping members for each volume:

for volume in liturgical:
  print(f'IN {volume}:')
  for (word, lectios) in list(liturgical[volume].items())[0:10]:
    print(f'\t{word}')
    print(f'\t\t{",".join(sorted(lectios)[0:5])} ...')

# We are not done yet, because we are not interested in the actual lectionaries, but in their number.
# So we make a new mapping `liturgicalNess`, which maps each word to the number of lectionaries it is associated with.

# +
liturgicalNess = {}

for volume in liturgical:
  for word in liturgical[volume]:
    nLectio = len(liturgical[volume][word])
    liturgicalNess.setdefault(volume, {})[word] = nLectio
# -

# Lets print the top twenty of each volume

for volume in liturgicalNess:
  print(f'IN {volume}:')
  for (word, lNess) in sorted(
    liturgicalNess[volume].items(),
    key=lambda x: (-x[1], x[0]),
  )[0:20]:
    print(f'\t{lNess:>5} {word}')


# # Frequency lists
#
# Here is how to get a frequency list of a volume.
#
# We can produce the frequency of any feature, but let us do it here for words in the Peshitta (OT) and
# lexemes in the SyrNY.
#
# There is a hidden snag: in the SyrNT we do not have only word nodes, but also lexeme nodes.
# When we count frequencies, we have to take care to count word nodes only.
#
# The function [freqList](https://annotation.github.io/text-fabric/tf/core/nodefeature.html#tf.core.nodefeature.NodeFeature.freqList)
# can do that.
#
# Lets use it and produce the top twenty list of frequent words in both sources, and also the number of hapaxes.

# +
# first we define a function to generate the table per volume

def showFreqList(volume):
  print(f'IN {volume}:')
  wordRep = 'word' if volume == P else 'lexeme'
  freqs = Fs[volume](wordRep).freqList(nodeTypes={'word'})
  
  # now the members of freqs are pairs (word, freqency)
  
  # we print the top frequent words
  for (word, freq) in freqs[0:10]:
    print(f'\t{freq:>5} x {word}')
    
  # we collect all hapaxes: the items with frequency 1
  hapaxes = [word for (word, freq) in freqs if freq == 1]
  print(f'{len(hapaxes)} hapaxes')
  for hapax in hapaxes[100:105]:
    print(f'\t{hapax}')


# +
# then we execute it on both volumes

for volume in A:
  showFreqList(volume)
# -

# # Queries
#
# First a simple query with all verses with a lectionary (with taksa and link)

query = '''
verse taksa link
'''

# We run them in both the Old and the New Testament

results = {}
for volume in A:
  results[volume] = A[volume].search(query)

# Let's show some results from the New Testament:

A[S].show(results[S], start=1, end=1)

# Let's show some results from the New Testament:

A[P].show(results[P], start=1, end=1)

# # Word study: CJN>
#
# We want to study a word, in both volumes.
# First we show a verse where the word occurs: James 3:18.
#
# It is in the New Testament.
#
# The 
# [`T.nodeFromSection()`](https://annotation.github.io/text-fabric/tf/core/text.html#tf.core.text.Text.nodeFromSection)
# function can find the node (bar code) for a verse specified by a passage reference.

# +
# we have to pass the section reference as a triple:
section = ('James', 3, 18)

# we retrieve the verse node
verseNode = T[S].nodeFromSection(('James', 3, 18))

# in case you're curious: here is the node, but it should not be meaningful to you,
# only to the program

print(verseNode)
# -

# Finally we show the corresponding verse by means of the function
# [pretty()](https://annotation.github.io/text-fabric/tf/advanced/display.html#tf.advanced.display.pretty)

A[S].pretty(verseNode)

# Now we use a query to find this word in the New Testament

queryS = '''
word lexeme_etcbc=CJN>
'''

resultsS = A[S].search(queryS)

# We show them all:

A[S].show(resultsS)

# For the OT, we do not have the lexeme value, so we try looking for word forms that *match* `CJN>` rather than those that are exactly equal to it.
#
# Note that we have replaced '=' by '~' in the query below

queryP = '''
word word_etcbc~CJN>
'''

resultsP = A[P].search(queryP)

# +
# We show only 20 results

A[P].show(resultsP, end=20)
# -

# Here ends the bootcamp session.
#
# Interested? Send [me](mailto:dirk.roorda@dans.knaw.nl) a note.
