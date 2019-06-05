import os
import collections
from functools import reduce

from tf.lib import writeSets
from tf.applib.helpers import dm

HERE_BASE = '.'
DROPBOX_BASE = '~/Dropbox/obb'

SET_NAME = 'sets.tfx'
MODULE = 'pos'
TF_LOC = f'{MODULE}/tf'


def getCases(caseStr):
  caseLines = caseStr.strip().split('\n')
  result = {}
  for caseLine in caseLines:
    (wordStr, categoryStr) = [x.strip() for x in caseLine.split('=', maxsplit=1)]
    categories = [x.strip() for x in categoryStr.strip().split(',')]
    words = [x.strip() for x in wordStr.strip().split('+')]
    for word in words:
      if word in result:
        print(f'WARNING: word {word} also occurs in another case')
      result[word] = categories
  return result


def getNoccs(data):
  return sum(len(x) for x in data.values())


def getOccs(data):
  return reduce(
      set.union,
      data.values(),
      set(),
  )


class PosTag(object):
  def __init__(self, A):
    self.A = A
    self.api = A.api

    self.sets = collections.defaultdict(set)
    self.pos = {}
    self.subpos = {}
    self.done = set()

  def prepare(self):
    api = self.api
    F = api.F
    L = api.L

    wordFromSigns = {}
    wordsOccs = collections.defaultdict(set)
    wordsWithoutDet = set()
    wordsWithDet = collections.defaultdict(set)
    wordsStrippedDet = collections.defaultdict(set)
    wordsNumeral = set()
    wordsNumeralUnknown = set()
    wordsUnknown = set()

    def usable(s):
      return (
          (F.reading.v(s) or F.grapheme.v(s))
      )

    for w in F.otype.s('word'):
      isNum = False
      noDet = False

      signs = [s for s in L.d(w, otype='sign') if usable(s)]
      if not signs:
        continue

      word = '-'.join(usable(s) for s in signs)
      augWord = f'-{word}-'
      if '-n-' in augWord:
        wordsNumeralUnknown.add(word)
        wordsUnknown.add(word)
      else:
        if 'x' in word or '...' in word:
          wordsUnknown.add(word)

      wordsOccs[word].add(w)
      wordFromSigns[w] = word

      if any(F.reading.v(s) == 'n' or F.type.v(s) == 'numeral' for s in signs):
        wordsNumeral.add(word)
        isNum = True

      signsNonDet = [s for s in signs if not F.det.v(s)]
      if len(signsNonDet) == 0:
        continue

      if len(signsNonDet) == len(signs):
        wordsWithoutDet.add(word)
        noDet = True

      if isNum or noDet:
        continue

      wordStripped = '-'.join(usable(s) for s in signsNonDet)
      wordsStrippedDet[wordStripped].add(word)
      wordsWithDet[word].add(w)
    print(f'Words (all)          : {len(wordsOccs):>5}')
    print(f'Words (nondet)       : {len(wordsWithoutDet):>5}')
    print(f'Words (det)          : {len(wordsWithDet):>5}')
    print(f'Words (det, stripped): {len(wordsStrippedDet):>5}')
    print(f'Words (numeral)      : {len(wordsNumeral):>5}')
    self.wordsOccs = wordsOccs
    self.wordsWithDet = wordsWithDet
    self.wordsWithoutDet = wordsWithoutDet
    self.wordsStrippedDet = wordsStrippedDet
    self.wordsNumeral = wordsNumeral
    self.wordsNumeralUnknown = wordsNumeralUnknown
    self.wordsUnknown = wordsUnknown
    self.wordFromSigns = wordFromSigns

  def doKnownCases(self, caseStr):
    wordsOccs = self.wordsOccs

    cases = getCases(caseStr)

    pos = self.pos
    subpos = self.subpos
    done = self.done
    sets = self.sets

    for (word, occs) in wordsOccs.items():
      cats = cases.get(word, None)
      if cats:
        cat = ''.join(cats)
        done.add(word)
        for w in occs:
          pos[w] = cats[0]
          if len(cats) > 1:
            subpos[w] = cats[1]
          sets[cat].add(w)

    print(f'    distinct words: {len(done):>6}')
    print(f'   pos assignments: {len(pos):>6}')
    print(f'subpos assignments: {len(subpos):>6}')

  def doPreps(self, prepStr):
    api = self.api
    F = api.F
    wordsOccs = self.wordsOccs

    pos = self.pos
    done = self.done
    sets = self.sets

    preps = set(prepStr.strip().split())
    cat = 'prep'
    nPreps = 0
    nOccs = 0
    for (word, occs) in wordsOccs.items():
      if word in preps:
        nPreps += 1
        nOccs += len(occs)
        for w in occs:
          pos[w] = cat
          sets[cat].add(w)
        done.add(word)
    sets['nonprep'] = set(F.otype.s('word')) - sets[cat]
    self.preps = preps

    print(f' distinct words: {nPreps:>6}')
    print(f'pos assignments: {nOccs:>6}')
    print(f'  non-prep occs: {len(sets["nonprep"]):>6}')

  def doNouns(self):
    api = self.api
    S = api.S

    nouns = {}
    nouns[''] = {}
    markedData = None
    unmarkedData = None
    label = None

    wordsOccs = self.wordsOccs
    wordsWithDet = self.wordsWithDet
    wordsWithoutDet = self.wordsWithoutDet
    wordsStrippedDet = self.wordsStrippedDet
    wordsNumeral = self.wordsNumeral
    wordsNumeralUnknown = self.wordsNumeralUnknown
    wordsUnknown = self.wordsUnknown
    wordFromSigns = self.wordFromSigns

    pos = self.pos
    subpos = self.subpos
    done = self.done
    sets = self.sets

    def gather():
      prefix = f'Before step {label}'
      print(f'{prefix:<35}: {len(nouns[""]):>5} words in {getNoccs(nouns[""]):>6} occurrences')
      allData = collections.defaultdict(set)
      for (word, occs) in markedData.items():
        allData[word] = set(occs)
      for (word, occs) in unmarkedData.items():
        allData[word] |= occs

      prefix = f'Due to step {label} marked'
      print(f'{prefix:35}: {len(markedData):>5} words in {getNoccs(markedData):>6} occurrences')
      nouns[f'M{label}'] = markedData

      prefix = f'Due to step {label} unmarked'
      print(f'{prefix:35}: {len(unmarkedData):>5} words in {getNoccs(unmarkedData):>6} occurrences')
      nouns[f'U{label}'] = unmarkedData

      prefix = f'Due to step {label} all'
      print(f'{prefix:35}: {len(allData):>5} words in {getNoccs(allData):>6} occurrences')
      nouns[label] = allData

      nouns[''].update(allData)
      prefix = f'After  step {label}'
      print(f'{prefix:<35}: {len(nouns[""]):>5} words in {getNoccs(nouns[""]):>6} occurrences')

      print('-' * 40)

    # based on determinatives

    label = 'det'

    markedData = {
        word: wordsOccs[word]
        for word in wordsWithDet
        if (
            word not in wordsNumeralUnknown
            and
            word not in done
        )
    }

    unmarkedData = {
        word: wordsOccs[word]
        for word in wordsWithoutDet & set(wordsStrippedDet)
        if word not in wordsUnknown and word not in markedData
    }

    gather()

    # based on prepositions

    label = 'prep'

    query = '''
prep
<: nonprep
    '''

    results = list(S.search(query, sets=sets))

    markedData = collections.defaultdict(set)
    for (p, w) in results:
      word = wordFromSigns[w]
      if word in done:
        continue
      markedData[word].add(w)

    unmarkedData = collections.defaultdict(set)
    for (word, markedOccs) in markedData.items():
      if word in wordsUnknown:
        continue
      unmarkedData[word] = wordsOccs[word] - markedOccs

    gather()

    # based on Sumerian logograms

    label = 'logo'

    query = '''
word
/with/
  sign langalt
/-/
    '''

    results = list(S.search(query))

    markedData = collections.defaultdict(set)
    for (w,) in results:
      word = wordFromSigns[w]
      if word in done:
        continue
      markedData[word].add(w)

    unmarkedData = collections.defaultdict(set)
    for (word, markedOccs) in markedData.items():
      if word in wordsUnknown:
        continue
      unmarkedData[word] = wordsOccs[word] - markedOccs

    gather()

    # based on numerals

    label = 'num'

    markedData = {word: wordsOccs[word] for word in wordsNumeral if word not in done}
    unmarkedData = {}

    gather()

    # deliver to sets

    for (name, data) in sorted(nouns.items()):
      print(f'noun{name:<9} with {len(data):>5} words and {getNoccs(data):>6} occurrences')
      sets[f'noun{name}'] = getOccs(data)

    # deliver to pos and subpos

    for (nkind, occs) in sets.items():
      if nkind.startswith('noun'):
        for n in occs:
          pos[n] = 'noun'
      if nkind == 'nounnum':
        for n in occs:
          subpos[n] = 'numeral'

  def export(self, metaData):
    pos = self.pos
    subpos = self.subpos
    sets = self.sets

    A = self.A
    api = self.api
    F = api.F
    TF = api.TF
    version = A.version

    nodeFeatures = dict(pos=pos, subpos=subpos)
    TF.save(
        metaData=metaData,
        nodeFeatures=nodeFeatures,
        location=HERE_BASE,
        module=f'{TF_LOC}/{version}',
        silent=True,
    )
    nFeats = len(nodeFeatures)
    featRep = ', '.join(sorted(nodeFeatures))

    cats = collections.Counter()
    for w in F.otype.s('word'):
      ps = pos.get(w, '')
      sp = subpos.get(w, '')
      cat = f'{ps}-{sp}'
      cats[cat] += 1

    total = sum(cats.values())
    uncategorized = cats['-']
    categorized = total - uncategorized
    catPerc = int(round(100 * categorized / total))
    uncatPerc = int(round(100 * uncategorized / total))
    nCats = len(cats) - 1

    stst = '**'

    md = f'''
---

## Features

{stst}{nFeats} TF features saved: {featRep}**.

{nCats} categories.

category | % | number of nodes
--- | --- | ---
none | {uncatPerc} | {uncategorized}
all | {catPerc} | {categorized}
'''
    for (cat, n) in sorted(
        cats.items(),
        key=lambda x: (-x[1], x[0]),
    ):
      if cat == '-':
        continue
      perc = int(round(100 * n / total))
      md += f'{cat} | {perc} | {n}\n'

    dm(md)

    for loc in [HERE_BASE, DROPBOX_BASE]:
      path = os.path.expanduser(f'{loc}/{SET_NAME}')
      writeSets(sets, path)

    md = f'''
---

## sets

{stst}{len(sets)} sets written to disk (GitHub repo and Dropbox)**.

set | number of nodes
--- | ---
'''
    for (name, nodes) in sorted(sets.items()):
      md += f'{name} | {len(nodes)}\n'

    dm(md)
