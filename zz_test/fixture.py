from itertools import chain

from tf.app import use
from tf.advanced.helpers import dm
from tf.core.helpers import console


APPS = f"""
    athenaeus
    banks
    bhsa
    dss
    nena
    oldbabylonian
    peshitta
    quran
    syrnt
    uruk

""".strip().split()


class TestApp:
    def __init__(self, hoist):
        self.apps = {app: None for app in APPS}
        self.hoist = hoist
        self.doApps = set()

    def foreground(self, app, refresh=False):
        A = self.apps[app]
        hoist = self.hoist
        appSpec = app if '/' in app else f"{app}:clone"
        if A is None:
            A = use(appSpec, checkout="clone", silent="deep", hoist=hoist)
            self.apps[app] = A
        else:
            if refresh:
                A.reuse(hoist=hoist)
            else:
                A.api.makeAvailableIn(hoist)
        hoist["A"] = A

    def testSet(self, apps=None):
        if apps is None:
            apps = APPS
        elif type(apps) is str:
            apps = apps.split()
        self.doApps = set()
        doApps = self.doApps

        for app in apps:
            if app not in self.apps:
                console(f"No such app: {app}", error=True)
                continue
            doApps.add(app)

    def test(self, function, refresh=True):
        for app in APPS:
            if app not in self.doApps:
                continue
            dm(f"# {app}")
            self.foreground(app, refresh=refresh)
            function()

    def select(
        self,
        verse=False,
        section=False,
        structure=False,
        slot=False,
        other=False,
        start=False,
        center=False,
        end=False,
        size=0,
        offset=0,
    ):
        hoist = self.hoist
        A = hoist["A"]
        api = A.api
        F = api.F
        T = api.T
        slotType = F.otype.slotType

        ac = A.context
        verseTypes = set(ac.verseTypes)

        structureTypes = T.structureTypeSet - verseTypes
        sectionTypes = T.sectionTypeSet - verseTypes
        allTypes = set(F.otype.all)
        otherTypes = allTypes - structureTypes - sectionTypes - verseTypes - {slotType}

        for tp in F.otype.all[::-1]:
            if (
                not verse
                and tp in verseTypes
                or not structure
                and tp in structureTypes - (sectionTypes if section else set())
                or not section
                and tp in sectionTypes - (structureTypes if structure else set())
                or not slot
                and tp == slotType
                or not other
                and tp in otherTypes
            ):
                continue
            nodes = F.otype.s(tp)
            startNodes = nodes[0 + offset:size + offset] if start else []
            mid = len(nodes) // 2
            midb = size // 2
            mide = midb + size % 2
            midNodes = nodes[mid - midb + offset : mid + mide + offset] if center else []
            endNodes = nodes[-size - offset:-offset if offset else None] if end else []
            seen = set()
            for n in chain(startNodes, midNodes, endNodes):
                if n in seen:
                    continue
                seen.add(n)
                yield (
                    n,
                    tp,
                    "verse"
                    if tp in verseTypes
                    else "sectional"
                    if tp in sectionTypes & structureTypes
                    else "structure"
                    if tp in structureTypes
                    else "section"
                    if tp in sectionTypes
                    else "slot"
                    if tp == slotType
                    else "",
                )

    def perform(self, method, nInfo, *args, **kwargs):
        hoist = self.hoist
        A = hoist["A"]

        (node, nType, kind) = (None, None, None) if nInfo is None else nInfo
        argStr = ", ".join(repr(a) for a in args)
        if argStr and node is not None:
            argStr = f", {argStr}"
        kwArgStr = ", ".join(f"{k}={repr(v)}" for (k, v) in kwargs.items())
        if kwArgStr:
            kwArgStr = f", {kwArgStr}"

        if node is None:
            headStr = ""
            nodeStr = ""
        else:
            if kind:
                kindStr = f"{kind}:"
            headStr = f"*{kindStr}* **{nType}** "
            nodeStr = node
        callStr = f"""
---

{headStr} `A.{method}({nodeStr}{argStr}{kwArgStr})`"""
        dm(callStr)
        theArgs = args if node is None else [node, *args]
        getattr(A, method)(*theArgs, **kwargs)


def typeShow(app, **options):
    api = app.api
    F = api.F
    for nType in F.otype.all:
        n = F.otype.s(nType)[0]
        dm(f"### {nType} {n}\n")
        app.plain(n, **options)
        app.pretty(n, **options)
