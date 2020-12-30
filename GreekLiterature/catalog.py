import os
import collections

from tf.core.timestamp import Timestamp
from tf.core.data import Data, WARP


BASE = os.path.expanduser("~/github")
ORG = "pthu"
REPO = "greek_literature"
REPO_PATH = f"{BASE}/{ORG}/{REPO}"
VERSION = "1.0"

OTYPE = WARP[0]


def collectTfDirs(path, result):
    """Collect TF directories.

    Collect all directories named `tf` that are somewhere below `path` and add
    the path names of those directories to the list `result`.

    Note: we strip the initial part that is common to all result paths.
    """

    with os.scandir(path) as it:
        for entry in it:
            name = entry.name
            if not name.startswith(".") and entry.is_dir():
                subPath = f"{path}/{name}"
                if name == "tf":
                    result.append(subPath.removeprefix(f"{REPO_PATH}/"))
                else:
                    collectTfDirs(subPath, result)


def getMeta(tfDir, tmObj):
    """Load the otype function of a TF dataset and deliver its metadata."""

    otypePath = f"{REPO_PATH}/{tfDir}/{VERSION}/{OTYPE}.tf"
    dataObj = Data(otypePath, tmObj)
    dataObj.load(metaOnly=True, silent=True)
    return dataObj.metaData


def makeCatalog():
    """Given a list of TF datasets, make a catalog of them.

    The catalog is first by author, then by title.
    The value is the path to the corresponding tf directory.
    """

    tmObj = Timestamp()
    works = collections.defaultdict(lambda: collections.defaultdict(list))
    tfDirs = []
    collectTfDirs(REPO_PATH, tfDirs)

    for tfDir in tfDirs:
        meta = getMeta(tfDir, tmObj)
        author = meta.get("author", "")
        title = meta.get("title", "")
        works[author][title].append(tfDir)

    return works
