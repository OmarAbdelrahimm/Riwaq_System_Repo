# 🗂️ Riwaq File Naming Standard v2 — English only

> **Everything is Latin.** No Arabic characters in file names, no spaces, no underscores — hyphens only.
> Why: clean sorting, safe uploads from a browser or phone, no broken names on any OS, and YouTube suggests
> the file name as the default video title.
>
> **Honest note:** YouTube does **not** rank by file name. The value is (1) sorting, (2) preventing A/B mix-ups,
> (3) a decent default title on upload. Real SEO lives in the title, description and tags. Latin names help
> **you** and the platform move files around — not the algorithm.

---

## 1️⃣ The pattern

```
{number}-{KIND}-{A|B}-{english-slug}-v{n}.{ext}
```

`02-CVR-H-A-comparison-is-a-tool-not-a-standard-v1.jpg`

| Field | Values | Why |
|---|---|---|
| **number** | `01`…`06` · `S01`…`S09` · `CMP` (compiled) · `LIVE` (live stream) · `F01` · `00` (docs) | **Always first** — otherwise the folder sorts alphabetically and episodes scatter |
| **KIND** | see table below | Know what a file is without opening it |
| **A / B** | only for A/B pairs | Stops cover A being paired with title B |
| **english-slug** | 3–7 words, kebab-case, **lowercase only** (KIND and A/B are the only uppercase parts) | Searchable in Drive + default title on YouTube |
| **v** | `v1`, `v2` … | Old and new versions sort correctly side by side |
| **ext** | `.jpg` (upload) · `.png` (archive) · `.md` · `.srt` · `.mp4` | Last, always |

### Kinds

| Code | Meaning |
|---|---|
| `CVR-H` | horizontal cover 1280×720 |
| `CVR-V` | vertical cover 1080×1920 |
| `SEO` | titles / description / tags doc |
| `SUB-AR` `SUB-EN` `SUB-BI` | Arabic / English / bilingual subtitles |
| `VID` | final master |
| `QC` | preview sheet — **never uploaded** |
| `DOC` | planning / numbering / index doc — **never uploaded** (`00-DOC-…`) |

---

## 2️⃣ Full examples

| File | Standard name |
|---|---|
| Video 01 cover, variant A, second edition | `01-CVR-H-A-relationships-deeper-than-communication-v2.jpg` |
| SEO doc for the same video | `01-SEO-relationships-deeper-than-communication-v2.md` |
| Short 03 cover, variant B | `S03-CVR-V-B-comparison-necessary-not-binding-v1.jpg` |
| Bilingual subs, Short 07 | `S07-SUB-BI-you-marry-a-legacy-not-a-person-v1.srt` |
| Series index doc in the Drive root | `00-DOC-delivery-index-v1.md` |
| Shorts numbering doc inside the shorts root | `00-DOC-shorts-titles-and-numbering-v1.md` |

---

## 2️⃣b Folders follow the same logic

```
{number}-{KIND}-{english-slug}          e.g. 04-EP-shaytan-runs-through-the-blood
S0n-SHORT-{english-slug}                e.g. S07-SHORT-you-marry-a-legacy
00-SHORTS-01-to-09                      the container of all shorts
CMP-COMPILED-{english-slug}             the compiled episode
```

Latin only, hyphen-separated, number first — so the folder list sorts in publish order.

---

## 3️⃣ Enforcement (no manual naming, ever)

```bash
/tmp/venv/bin/python scripts/publish/naming.py --check <file> [<file> ...]   # 0 = compliant
```

`check_name()` rejects: Arabic characters, spaces, underscores, uppercase inside the slug,
a missing A/B on `CVR-*`, an A/B on anything else, the wrong extension for the kind,
a slug longer than 7 words, and anything outside the pattern.

The same function runs inside `seo_pack.py --audit` on the `**اسم الملف:**` line of every pack,
so a pack cannot ship with a name the pattern would reject.

**Retroactive rule:** the convention applies to every file already on Drive, not only new output —
IDs stay the same, only the name changes (see `docs/PRODUCTION_RULES.md` §⑥).
| Compiled film cover, A | `F01-CVR-H-A-the-relationship-that-fixes-all-relationships-v1.jpg` |
| Episode 04 master | `04-VID-shaytan-runs-through-the-blood-v1.mp4` |

---

## 3️⃣ Generating names

```python
from naming import cover_name, save_cover

stem = cover_name("02", "CVR-H", "المقارنة أداة لا معيار",
                  variant="A", v=1, en="comparison-is-a-tool-not-a-standard")
save_cover(im, stem, "outputs/PUBLISH_PACK_EP02_COVERS")
```

- Pass `en=` with a **hand-written English slug**. It is the title the world sees; never leave it to a machine.
- With no `en=`, `naming.translit()` falls back to a franco transliteration (`المقارنة أداة لا معيار` → `comparison-tool-not-standard`).
  Good enough for internal files, **not** for anything a viewer might read.

---

## 4️⃣ JPG vs PNG — measured on a real cover (1280×720)

| Format | Size | Note |
|---|---|---|
| PNG | 476 KB | lossless — the 2px frame lines and Arabic diacritics stay perfectly sharp |
| JPG `q92 sub=1` (old default) | 127 KB | `sub=1` smears colour edges → thin gold lines shimmer |
| **JPG `q95 sub=0` (adopted)** | **190 KB** | 4:4:4 → no colour smearing, text stays crisp, still 1/10 of the limit |
| YouTube limit | **2 MB** | everything above is safe |

**Rule:** `.jpg q95 4:4:4` is the **upload file** · `.png` is the **archival master** (future edits start here, never from a JPG).
Don't upload the PNG — YouTube re-encodes anyway.

---

## 5️⃣ The `QC` comparison sheet — retired

A single PNG holding both covers has **no publishing function**: it can't be uploaded, viewers never see it.
It also **misleads you**, because you judge at full size while viewers see **168px**.

**Decision:** it is no longer produced or delivered. Cover decisions are made from **168px thumb tests**
(`02-QC-A-thumb-168px-v1.png`) or shown in chat — never as a Drive deliverable.
