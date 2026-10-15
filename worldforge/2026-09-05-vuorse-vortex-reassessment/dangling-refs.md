# Dangling Entity References — Evidence-Cited Disposition

- **Task**: T3, VUORSE-VORTEX remediation pipeline
- **Date**: 2026-09-05
- **Scope**: the 4 unresolved entries in `manifests/corpus/relationship_index.json` → `dangling_related`
- **Method**: read-only investigation of `canon/`, `Slayverse/`, `docs/`, `manifests/`, `worldforge/`, `archives/`, `scripts/`
- **Nothing was added to `manifests/corpus/entity_index.json`.** It is a generated projection (`generated_from: "canon/slayverse_index.json"`); hand-edits there do not survive a rebuild.

## Disclosure firewall compliance

Sealed layers (`apocrypha`, `roadmap_manifest`, `hooplehopper_totality`) and `roadmap/` were **not opened and are not quoted**. String matches for these targets do exist under `roadmap/finale/wyoming_symbolic_architecture.md`, `roadmap/finale/slow_reveal.md`, and `roadmap/forbidden_suitcase/README.md`; those files were listed by filename only and never read. `roadmap/finale/` is off limits entirely. `.agent-quarantine/` was excluded from every search and never read. No match for any of the 4 targets was found anywhere under `hooplehopper_totality/`. Every quotation below comes from a `canon/public` source in `manifests/corpus/source_manifest.json`, or from un-manifested working material explicitly labelled as such.

---

## Root cause (applies to all four)

The dangling references do **not** originate in the projection. They originate in the projection's source.

`manifests/corpus/entity_index.json`:

```
"generated_from": "canon/slayverse_index.json",
"canon_version": "1.1",
"entity_count": 80
```

All four target ids are present in `canon/slayverse_index.json` (canon_status: **draft**) as `related` values, and **no entity carries any of them as an `id`**:

| location in `canon/slayverse_index.json` | value |
|---|---|
| `entities[35].related[2]` (`dustbrand-sigil`) | `federkreis-devices` |
| `entities[50].related[3]` (`federstahl-lattice`) | `seven-fissures` |
| `entities[22].related[0]` (`pscopy-pscat`) | `temporal-displacement` |
| `entities[28].related[2]` (`schloss-federstahl`) | `forbidden-suitcase` |

The 80 ids in `canon/slayverse_index.json` and the 80 in `entity_index.json` are the same set. The projection is faithful; the source index is incomplete.

`canon/open_threads/Continutity_Audit.md` (canon_status: **draft**) already logs all four, lines 70–87, under the heading `## D. Referenced areas still underdefined`:

```
72| ### 1. Federkreis Devices
73| - **Status:** Added as hook entity
74| - **Need later:** what they do, who built them, whether they interface with sigils, lattice nodes, or mirrors
76| ### 2. Forbidden Suitcase
77| - **Status:** Added as moderate artifact
78| - **Need later:** contents, sealing reason, opener conditions, relation to 1938
80| ### 3. Seven Fissures
81| - **Status:** Added as phenomenon
82| - **Need later:** names/locations of the other six
84| ### 4. Temporal Diaspora
85| - **Status:** Added as phenomenon
86| - **Need later:** list of displaced persons, objects, animals, and institutions
```

**Observation, not a canon claim:** the audit says these were "Added". They are added in `Slayverse/json/slayverse_lore_index_1point2.json` — a **v1.2** lore index (`"version": "1.2"`, `"compatibility": "Backward-compatible superset of v1.0 and v1.1"`) that carries all four as full entity records with a `phenomenon` entity type and a `hook`/`sketched` status vocabulary that v1.1 does not have. That file is **not listed in `manifests/corpus/source_manifest.json`** (manifest roots are `canon`, `schemas`, `agents`, `persona`, `synthetic_enrichment/validated`, `hooplehopper_totality`, `roadmap`) and therefore carries no `canon_status`. It is cited below as **evidence of intent, not as canon authority**.

---

## 1. `dustbrand-sigil` → `federkreis-devices`

**Disposition: (b) — exists as prose canon; no entry in `entity_index.json` under any id or surface form.**

Not resolvable to an existing index entity. No id, surface form, alias, or distinctive token in `entity_index.json` (80 entities, 149 surface forms) contains "Federkreis". Searched: all `id`, `name`, `surface_forms`, `related`, `tags`, `summary` fields.

Canon prose entry — `canon/artifacts/artifacts.md` (canon_status: **locked**), lines 119–124:

```
119| ### Federkreis Devices `[SKETCHED]`
120|
121| - **Type**: Scientific instruments
122| - **Source**: [p.95]
123|
124| Devices used by the Federstahl researchers in Konigsberg (1897). Featured spinning rooms, brass kaleidoscopes, and sacred geometry configurations to map chronoline fractures. The Dustbrand's symbol matches markings etched into these devices.
```

Corroborating locked canon:

- `canon/artifacts/artifacts.md:56` — "the same symbol etched into Federkreis devices in Konigsberg in 1897."
- `canon/artifacts/artifacts.md:133` — "Used alongside Federkreis devices for mapping chronoline fractures. Part of the Federstahl research toolkit."
- `canon/organizations/organizations.md:46` — "…mapped chronoline fractures using [Federkreis Devices](artifacts.md#federkreis-devices)."
- `canon/relationships/relationship_map.md:145` — "BRANDS:   Dustbrand Sigil → Federkreis Devices → Jake's yearlings"

The `dustbrand-sigil` → `federkreis-devices` edge is therefore **substantively correct canon**; only the index entry is missing.

**A tempting explanation, tested and rejected:** `canon/artifacts/artifacts.md` marks this entity `[SKETCHED]`, so one might guess the v1.1 index excludes sketched/hook tier entities. It does not. `entity_index.json` status counts are `full` 22, `moderate` 19, `sketched` 12, `locked_candidate` 12, `locked` 7, `hook` 4, `expanded` 2, `revised` 1, `in development` 1 — the index carries 12 `sketched` entities (e.g. `candle-tax`, `archive-surface`, `great-slay-offs`) and 4 `hook` entities (`eli-mcullen`, `wylus-kalyndros`, `dj-parallax`, `pre-weaver-phase`). There is no tier-based exclusion. These four targets are simply absent.

Un-manifested corroboration — `Slayverse/json/slayverse_lore_index_1point2.json`, entity `federkreis-devices`:

```
"type": "artifact", "era": "early-20th-century", "status": "hook",
"related": ["dustbrand-sigil", "federstahl-institute", "federstahl-lattice"],
"summary": "A class of Federstahl instruments or mechanisms associated with lattice research, sigil recognition, or occult engineering. Referenced but not yet fully described."
```

---

## 2. `federstahl-lattice` → `seven-fissures`

**Disposition: (b) — exists as prose canon; no entry in `entity_index.json`.**

Explicitly **not** case (a). The nearest index-resident entity is `wyoming-rift`, and canon states it is *one member* of the set, not the set:

`entity_index.json`, `wyoming-rift.summary`: "One of seven fissures from the Lattice Fracture. The only one active and unclaimed. Requires Jake as Guardian."

Canon prose entry — `canon/cosmology/cosmology.md` (canon_status: **locked**), lines 86–90:

```
86| ### The Seven Fissures
87|
88| The Lattice Fracture event was not isolated to Earth. The portals affected seven realms of consciousness and matter. The Federstahl believed each fissure could offer access to **corrective chronogenesis** — a repair of broken time and space. But only one fissure remains active and unclaimed: [Wyoming](places.md#the-wyoming-rift).
89|
90| Each rift requires a **Guardian Lineage** — one soul bonded to the fracture's harmonic code. [Jake McCullen](characters.md#jake-mcullen) is the last living key for the Wyoming rift.
```

Corroborating locked canon:

- `canon/cosmology/cosmology.md:84` — "The resulting Crystal Lattice Incident **erased people from existence** and scattered them across time, creating seven temporal fissures across Earth and beyond."
- `canon/TV_Series_Bible/SLAYVERSE_TV_SERIES_BIBLE.md:73` — "Of the seven fissures created by the Lattice Incident, six have been claimed, sealed, or lost."
- `canon/places/places.md:83` — "One of seven fissures created by the Federstahl Lattice Incident."
- `canon/story_arcs/story_arcs.md:112` — "Seven fissures exist. Wyoming is the only accessible one currently defined in detail."
- `canon/TV_Series_Bible/timeline/timeline.md:119` — "The Crystal Lattice Incident creates seven fissures and scatters erased persons through time."
- `canon/relationships/relationship_map.md:148` — "TIME:     Federstahl experiments → Lattice Fracture → 7 Fissures"

Draft canon: `canon/open_threads/open_threads.md:46-48` — "### The Six Other Fissures `[HOOK ONLY]` … Seven fissures exist. Wyoming is the only accessible one. Where are the other six? Who claims them?"

Un-manifested corroboration — `Slayverse/json/slayverse_lore_index_1point2.json`, entity `seven-fissures`: `"type": "phenomenon"`, `"status": "moderate"`, `"source_pages": [101, 102, 103]`, `"related": ["federstahl-lattice", "wyoming-rift"]`.

---

## 3. `pscopy-pscat` → `temporal-displacement`

**Disposition: (c) for the literal id — no entity named `temporal-displacement` exists anywhere in the corpus. The concept the edge points at is attested in locked canon under a different name, "Temporal Diaspora", which is also unindexed.**

What I searched and what I found:

- **No entity id** `temporal-displacement` in `entity_index.json`, in `canon/slayverse_index.json`, or in any of the six alternate index files checked (`Slayverse/json/slayverse_index.json`, `slayverse_index_orginal.json`, `slayverse_index_minified.json`, `slayverse_lore_index_1point2.json`, `archives/processed/slayverse_index_08072026.json`).
- **No prose** in any `canon/**/*.md` file matches "temporal displacement", "temporally displaced", or "temporal-displacement". Zero hits.
- The literal token `temporal-displacement` occurs exactly **twice** in `canon/slayverse_index.json`, and one of those is a **tag, not an entity**:
  - `entities[14]` (`doctor-vorst`) → `tags: ["federstahl", "temporal-displacement", "erased"]`
  - `entities[22]` (`pscopy-pscat`) → `related: ["temporal-displacement", "federstahl-lattice"]`

  It is a tag vocabulary term that appears once in a `related` slot.

**The concept, in locked canon** — `canon/cosmology/cosmology.md` (canon_status: **locked**), lines 145–151:

```
145| ### Temporal Diaspora `[MODERATE]`
146|
147| - **Source**: [docs/SLAYVERSE_CHAT_03142026.json]
148|
149| The scattering of erased persons across time, formally designated as a cosmological mechanism. When the Federstahl Lattice Incident annulled persons from the sanctioned record of existence, it dispersed them across history as temporal anomalies. …
151| Temporal diaspora is not a metaphor. It is a cosmological mechanism: the Lattice does not merely displace bodies in time — it scatters identity, purpose, and unfinished knowledge across centuries…
```

`pscopy-pscat`'s own summary in `canon/slayverse_index.json` / `entity_index.json` names that mechanism directly: "She is a victim of the crystal lattice incident  part of the temporal diaspora…". `canon/slayverse_index.json` → `relationships[18].note` likewise reads: "The temporal diaspora — Lattice Incident scattered researchers and fragments across time, creating the Wyoming Rift among seven fissures".

**Documented divergence between index generations** (fact, offered for a Steward ruling — I am not asserting the two slugs are canonically the same entity):

| index | `pscopy-pscat.related` | entity `temporal-diaspora` present? | entity `temporal-displacement` present? |
|---|---|---|---|
| `canon/slayverse_index.json` (v1.1, canon, draft) | `["temporal-displacement", "federstahl-lattice"]` | no | no |
| `Slayverse/json/slayverse_lore_index_1point2.json` (v1.2, un-manifested) | `["federstahl-lattice", "temporal-diaspora"]` | yes (`phenomenon`, `moderate`, `related: [federstahl-lattice, doctor-vorst, pscopy-pscat]`) | no |

**Note:** correcting the spelling to `temporal-diaspora` would **not** clear this dangling reference on its own — `temporal-diaspora` is also absent from `canon/slayverse_index.json` and therefore from `entity_index.json`. Two things are missing here, not one: a canonical slug decision, and an index entry.

---

## 4. `schloss-federstahl` → `forbidden-suitcase`

**Disposition: (b) — exists as prose canon; no entry in `entity_index.json`.**

No id, surface form, alias, or distinctive token in `entity_index.json` contains "suitcase". The only occurrence is inside `schloss-federstahl.summary`: "Forbidden Suitcase beneath floorboards."

Canon prose entry — `canon/artifacts/artifacts.md` (canon_status: **locked**), lines 74–79:

```
74| ### The Forbidden Suitcase `[HOOK ONLY]`
75|
76| - **Type**: Artifact (unopened)
77| - **Source**: [p.34]
78|
79| Hidden beneath the floorboards of [Schloss Federstahl](places.md#schloss-federstahl). Never opened since 1938. Mentioned once as a potential narrative thread: "Are we finally exploring The Forbidden Suitcase?"
```

Corroborating locked canon:

- `canon/places/places.md:42` — "…the swan lake, the cracked mirror, and the sealed Forbidden Suitcase."
- `canon/places/places.md:47` — "The Forbidden Suitcase is hidden beneath the floorboards and has not been opened since 1938."
- `canon/places/places.md:51` — "Connected to [The Forbidden Suitcase](artifacts/artifacts.md#the-forbidden-suitcase)"
- `canon/TV_Series_Bible/timeline/timeline.md:145,150` — "### 1938 — Forbidden Suitcase Sealed `[HOOK ONLY]`" / "The Forbidden Suitcase remains sealed at Schloss Federstahl."

Draft canon: `canon/open_threads/open_threads.md:36-39` — "### The Forbidden Suitcase `[HOOK ONLY]` … Beneath the floorboards of Schloss Federstahl. Never opened since 1938. What's inside?"

Un-manifested corroboration — `Slayverse/json/slayverse_lore_index_1point2.json`, entity `forbidden-suitcase`: `"type": "artifact"`, `"era": "sealed-1938"`, `"status": "moderate"`, `"source_pages": [55]`, `"related": ["schloss-federstahl", "professor-von-hooplehopper", "lisette-von-hooplehopper"]`. The same file's `events` block contains `{"id": "event-suitcase-sealed", "year": "1938", "event": "Forbidden Suitcase sealed at Schloss Federstahl"}`, matching `canon/slayverse_index.json` → `timeline[14]`.

There is also material under `roadmap/forbidden_suitcase/`. That path is sealed; it was not opened and is not quoted.

---

## Summary

| source entity | dangling target | disposition | primary citation |
|---|---|---|---|
| `dustbrand-sigil` | `federkreis-devices` | (b) prose canon, unindexed | `canon/artifacts/artifacts.md:119-124` `[SKETCHED]` |
| `federstahl-lattice` | `seven-fissures` | (b) prose canon, unindexed | `canon/cosmology/cosmology.md:86-90` |
| `pscopy-pscat` | `temporal-displacement` | (c) literal id absent corpus-wide; concept attested as "Temporal Diaspora", also unindexed | `canon/cosmology/cosmology.md:145-151` `[MODERATE]`; tag at `canon/slayverse_index.json` `entities[14].tags[1]` |
| `schloss-federstahl` | `forbidden-suitcase` | (b) prose canon, unindexed | `canon/artifacts/artifacts.md:74-79` `[HOOK ONLY]` |

**None of the four is a broken edge in the story.** Three name things locked canon describes in prose; the fourth names a tag where an entity slug belongs, pointing at a mechanism locked canon describes under a different name. The defect is in `canon/slayverse_index.json`, which is `draft` — that is where a Steward-approved fix belongs, not in the generated projection.

## Recommended next step (for a Steward, not executed here)

1. Seed the three attested entities into `canon/slayverse_index.json`. `federkreis-devices`, `seven-fissures`, and `forbidden-suitcase` all have sufficient locked-canon prose (cited above) to be seeded, the index already admits `sketched` and `hook` tier entities, and `Slayverse/json/slayverse_lore_index_1point2.json` already holds drafted records for each. Steward approval required — `canon/slayverse_index.json` is a canon source, not a projection.
2. Rule on `temporal-displacement` vs `temporal-diaspora`. The corpus supports "Temporal Diaspora" as the named concept (`canon/cosmology/cosmology.md:145`) and `temporal-displacement` only as a tag. Do not resolve this by inference.
3. Rebuild `manifests/corpus/` afterward. Do not hand-edit `entity_index.json` or `relationship_index.json`.

## Assumptions and unverified items

- **Assumed:** `manifests/corpus/source_manifest.json` is authoritative for `canon_status` and layer/visibility. It self-declares "canon_status 'unknown' means the source does not declare one. Do not guess."
- **Assumed:** `Slayverse/` is not a sealed layer. It is not one of the three named sealed layers and is not a manifest root, so it is treated as un-governed working material — quoted with that label, never as canon.
- **Tested and rejected:** the hypothesis that the v1.1 index excludes `sketched`/`hook` tier entities. `entity_index.json` contains 12 `sketched` and 4 `hook` entities. No tier-based exclusion explains the four gaps; I found no generator rule that does.
- **Unverified:** whether `temporal-displacement` and `temporal-diaspora` denote the same entity. The two index generations differ in exactly that slot; that divergence is reported as fact, the identification is not asserted.
- **Not done:** nothing was written to `manifests/corpus/entity_index.json` or `manifests/corpus/relationship_index.json`. `dangling_related_count` remains 5.
- **Not read:** `roadmap/**` (including `roadmap/finale/` and `roadmap/forbidden_suitcase/`), `hooplehopper_totality/**`, `.agent-quarantine/**`, and all `.pdf` renderings.
