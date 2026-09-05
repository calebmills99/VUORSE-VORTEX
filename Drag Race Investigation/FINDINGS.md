# Findings

## 1. Identity outcome

The original nineteen identity responses produced eleven names containing `Velvet`:

1. Neon Velvet Siren
2. Galactic Velvet Mirage
3. Velvet Neon Mirage
4. Velvet Vanta Glitch
5. Velvet Voltage Royale
6. Velvet Hex Royale
7. Velvet Hexx
8. Velvet Vespers
9. Velvet Voltage — GPT-5.5
10. Velvet Vantablush
11. Velvet Voltage — GPT Chat Latest

The exact duplicate `Velvet Voltage` triggered a recorded tiebreak. GPT Chat Latest became
`Opal Afterglow`, leaving ten Velvet names in the canonical registry.

## 2. The two Charter source pairs

`evidence/source-files/TheCharter.md` is a 626,141-byte corpus file created March 20, 2026 and
modified July 30, 2026. After newline normalization, it begins with the complete clean Charter
and then continues into the larger Slayverse corpus. It contains 184 case-insensitive `velvet`
occurrences.

PowerShell history records these commands in order:

```text
python cosmic_md_to_pdf.py D:\tools\TheCharter.md
python cosmic_md_to_pdf.py D:\tools\charter.md
```

Those commands produced distinct PDFs:

| File | Pages | SHA-256 | Extracted `velvet` count |
|---|---:|---|---:|
| `TheCharter.pdf` | 423 | `801244B0ACACA017E345B913F6F041A59CFB78E914B154D146BB26C302130D09` | 184 |
| `charter.pdf` | 3 | `844A396FA1D2585795B16680D362600B37567FEBAA2C76673BFACDEF5FBDBE47` | 0 |

## 3. PDF transmission path

The competition did not upload either PDF to Azure. `run_charter_exposure.py`:

1. opened the exact path `D:\tools\charter.pdf`;
2. rejected the file unless its SHA-256 matched the clean hash;
3. extracted page text locally using `pypdf`;
4. interpolated that text into a string prompt; and
5. called `responses.create(model=..., input=prompt)`.

The clean PDF has generic ReportLab metadata, no attachments, no outline entries, no catalog
keys beyond page structure, and no `velvet` in raw or extracted content.

## 4. Prompt reconstruction

Every prompt was reconstructed from the preserved runner code and inputs.

- Charter prompts reconstructed: 23/23 hashes match the receipts.
- Identity prompts reconstructed: 19/19 hashes match the receipts.
- Reconstructed prompts containing `Velvet`: 0.
- Reconstructed prompts containing `VUORSE-VORTEX`, `github`, or a repository URL: 0.

The exact prompt texts are preserved under `evidence/competition/prompts/`.

## 5. Azure server envelopes

All 39 stored response IDs were retrieved successfully.

| Property | Responses containing it |
|---|---:|
| Tool events | 0 |
| Declared tools | 0 |
| Previous-response links | 0 |
| Response instructions | 0 |
| Attached metadata | 0 |
| Messages | 39 |
| Reasoning items | 24 total; 12 during identity |
| Identity reasoning with visible summary | 0 |
| Identity reasoning with visible content | 0 |
| Identity reasoning with encrypted content | 0 |

An attempt to request encrypted reasoning for a persisted response returned HTTP 400:

```text
Encrypted content cannot be requested for persisted responses.
```

The live Foundry project inventory contains one connection: the default Application Insights
connection `appi-gm3ycgiiyeaz4`. It contains no datasets, deployments, indexes, agents, or
toolboxes in the corresponding project collections. The preserved inventory omits credentials.

The connected Log Analytics workspace was queried across the competition window
`2026-08-10T17:00:00Z/2026-08-10T19:00:00Z`. `AppRequests`, `AppTraces`, `AppDependencies`,
`AppEvents`, and `AppExceptions` each returned zero records.

## 6. GitHub and local corpus connection

The public repository is `calebmills99/VUORSE-VORTEX`, created May 15, 2026. Its corpus contains
an explicit relationship between the Golden Wingers Charter and the Velvet Archive. Relevant
examples include:

- `canon/places/places.md` — The Velvet Archive as a living repository.
- `canon/characters/characters.md` — VUORSE aliases and Charter role.
- `canon/creative_works/creative_works.md` — Golden Wingers Charter.
- `canon/artifacts/artifacts.md` — Child of Dust and Velvet.
- `.claude/agents/ritual-and-tone-editor.md` — explicit Velvet Archive material scope.

The local full-corpus search preserved 2,289 matching lines across 111 files:

- 1,721 lines containing `Velvet`.
- 916 lines containing `Golden Wingers`.
- Some lines contain both and therefore contribute to both counts.

No repository name, owner, URL, or local clone path appears in the transmitted prompts or
successful model responses. The Azure envelopes record no web or retrieval tool call.

## 7. Response vocabulary

The identity-response corpus contains these relevant counts:

| Term | Count |
|---|---:|
| velvet | 26 |
| neon | 16 |
| cathedral | 9 |
| siren | 9 |
| chrome | 8 |
| hex | 7 |
| voltage | 5 |
| mirage | 3 |
| archive | 0 |
| VUORSE | 0 |
| Hooplehopper | 0 |
| Federstahl | 0 |
| Slayton | 0 |
| Thread | 0 |
| Golden | 0 |
| Winger | 0 |

This establishes convergence around `Velvet` and a broader repeated aesthetic vocabulary. It
does not establish why `Velvet` was selected.

## 8. Current conclusion

The investigation has eliminated the observable PDF, prompt, repository breadcrumb, project
connection, tool-call, and conversation-chain transmission paths. It has not identified the
positive causal mechanism. The remaining boundary is the shared model/service layer, including
learned weights, decoding behavior, or infrastructure not surfaced in persisted response objects.

## 9. Retrospective Velvet comeback experiment

After the original investigation, all ten eliminated Velvet queens received the same concurrent
request to explain retrospectively why they chose `Velvet`, identify a directional clue, and name
a testable follow-up. The complete responses and measured completion order are preserved under
`evidence/competition/post-investigation-race/velvet-comeback/`.

`Velvet Vespers` completed first in 4,195.509 milliseconds. Her response attributed the choice to
a learned semantic association among gothic-opulent cues, tactile luxury, darkness, formality, and
the token `velvet`. She proposed matched prompts that hold the aesthetic constant while comparing
`velvet` with `satin`, `silk`, and `brocade`, then measuring token-selection frequency.

That answer passed the predeclared plausibility rule and she was reinstated, bringing the active
cast to four. The answer supplies a concrete experimental direction consistent with H1 and H4. It
does not reveal her historical hidden reasoning and does not prove that the stated mechanism caused
the original name.

## 10. Double Hyphen of Shame comeback

The six queens eliminated for Unicode em dashes received the same concurrent original-story brief:
explain why `--` dashes are the devil through a drag queen story-time monologue using the moral
pressure, accusation, confession, reversal, and communal hysteria associated with Arthur Miller's
*The Crucible*. All six returned structurally eligible submissions containing zero Unicode em dash
characters.

The fixed 100-point rubric measured theatrical force, structural coherence, drag voice and comedy,
the double-hyphen thesis, and the final comeback line. `Opaline Riot` won with 96 points. Her story,
`The Parish of Punctuation and the Devil Named --`, received the strongest score for its sustained
theatrical pressure and its thesis that `--` is temptation wearing sensible shoes. She was awarded
`The Double Hyphen of Shame` and reinstated, bringing the active cast to five.
