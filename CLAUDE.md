# Instructions for Claude

You are working with a tool that generates Vista Social bulk-scheduling CSVs from arbitrary media + caption sources and hosts the media on GitHub so Vista can fetch it.

## When to use this repo

Use this tool whenever the user asks you to:
- "Schedule N posts on Vista Social"
- "Bulk upload posts to Vista Social"
- "Build a schedule CSV"
- Anything involving Vista Social's **Bulk Publishing → Import from CSV** flow

Do **not** use it for single-post scheduling (do that in Vista's UI) or for platforms other than Vista Social.

## What the tool does

1. Copies the user's media into `batches/<batch_name>/media/` in this repo.
2. Parses captions from source files (text sections like `CAROUSEL A1: ...`, or xlsx rows keyed by filename).
3. Assigns dates to posts using a posting-day rule (e.g., Mon–Thu only).
4. Writes `batches/<batch_name>/schedule.csv` in Vista's exact format.
5. On `--push`, commits and pushes — raw GitHub URLs go live instantly.

The user uploads that CSV at Vista Social → Bulk Publishing → Import from CSV.

## Workflow for a new batch

Walk through these steps in order. Don't skip ahead — surface ambiguities **before** generating anything.

### 1. Gather inputs

Ask concretely (not via AskUserQuestion — just ask in text):
- **Where is the media?** Absolute paths to carousel folders + static files. If it's a downloaded Google Drive ZIP, dig into the nested folders.
- **Where are the captions?** Usually a `Captions.txt` (text sections, one per carousel) and/or a `.xlsx` (one row per static with a filename column). Different batches may have different formats — adapt or extend the parsers.
- **Schedule rules:** start date, which weekdays to post, posting time, alternation pattern (e.g., alternate static/carousel).
- **Target platforms in Vista:** LinkedIn, FB, IG, X, etc. (informational — the CSV doesn't encode this; user picks profiles in Vista's UI.)
- **Timezone:** Vista uses the account's configured timezone. Confirm with the user; don't convert.

### 2. Inspect the actual files

Before mapping, `ls` the source folders and read the caption files. Common issues to flag:
- Folder names don't match caption keys (e.g., `C1_`, `C2`, `C3`… but captions reference `A1`, `A2`, `B2`…). Ask the user for the mapping.
- Slide count per carousel differs from caption doc — ask whether the caption is still accurate.
- Missing / scrapped files. Ask which pieces to include.
- Captions.txt and .xlsx may overlap or disagree — clarify which is authoritative per content type.
- Same hook text across multiple statics (visual variants of one message). Spread them across the schedule or pick one.

Do not silently guess these mappings. Confirm in a single consolidated list of questions.

### 3. Design the schedule

- `apply_dates(items, start, post_days)` from `vista_bulk` fills dates automatically.
- If post counts don't evenly alternate (e.g., 12 statics + 10 carousels), flag that at least one same-type pair will be adjacent. Suggest where to place it or whether to drop an item.
- For same-topic pairs (common when captions are written in multiple visual templates), space them ≥14 days apart.

Present the proposed schedule as a table with **filenames + a one-line identifier** per post. Do not label posts as "Static 1 / Static 2" — the user needs to verify content per slot.

### 4. Build the batch config

Copy an existing batch:
```
cp -r batches/brand_2026_04 batches/<new_batch_name>
```

Then edit `batches/<new_batch_name>/config.py`:
- Update source paths.
- Update the `_items` list — one dict per post, in posting order.
- Update `start` date, `post_days`, and `time` in `CONFIG`.
- If the caption file formats differ, point `captions.carousels.type` / `captions.statics.type` at the right parser.

### 5. Run the build

```
python build.py batches/<new_batch_name>/config.py
```

This generates the CSV locally without pushing. Verify row counts match expectations (statics = 1 row each; carousels = slide_count rows each).

Once the user confirms, push:
```
python build.py batches/<new_batch_name>/config.py --push
```

### 6. Hand off to Vista

Tell the user: upload `batches/<new_batch_name>/schedule.csv` at Vista Social → Bulk Publishing → Import from CSV. Ask them to verify in Vista's preview that:
- Carousels group correctly (N slides with identical caption+time → 1 carousel post).
- Times display in the account's local timezone as expected.
- Target profiles are selected.

## Vista Social CSV format (fixed)

Headers (exact, leading space before `time` is intentional — matches Vista's downloadable sample):
```
message,type,link, time
```

- `message` — caption text (supports multi-line, UTF-8 emojis OK).
- `type` — `image`, `video`, `article`, or `message`.
- `link` — public URL. GitHub raw URLs work. **Google Drive links do NOT.**
- ` time` — `2026-04-21 7:00 pm` or `2026-04-21 19:00`, or `now`, `queue next`, `queue last`.

**Carousel encoding:** repeat rows with identical `message` + ` time`, varying only `link` per slide. Vista groups them into one post.

**Limits:** 200-row hard cap, 100 recommended per upload.

## Parsers

Two caption parsers are provided in `vista_bulk.py`:

- `TextSections(path, section_prefix="CAROUSEL")` — for files where each caption sits under a header like `CAROUSEL A1: Some title` followed by slide breakdown, a `Caption` marker, then the body.
- `XlsxByFilename(path, filename_col, caption_col)` — for spreadsheets where each row holds one piece keyed by filename.

If a new batch has a different source format (JSON, CSV, Google Doc, per-file `.txt` sidecars, etc.), add a new parser class to `vista_bulk.py` that subclasses `CaptionSource` and implements `get(key) -> str`. Then register it in `build_caption_source()` with a new `type` string.

## Repo layout

```
vista_bulk.py                  # library: parsers, media copy, CSV writer, date helper
build.py                       # CLI runner
requirements.txt               # openpyxl
batches/
  <batch_name>/
    config.py                  # per-batch: source paths, schedule, time
    media/                     # auto-populated by build.py
      carousels/<folder>/slide_XX.png
      statics/<file>.png
    schedule.csv               # auto-generated; upload this to Vista
```

## Gotchas to remember

- **Repo must stay public.** Vista fetches media over public HTTP. Private repos → 404 on upload.
- **Timezone confusion.** Vista reads the datetime as-is in the account's timezone. Always confirm the user's account timezone matches the times they want.
- **Excel kills emojis in CSVs.** This tool writes UTF-8 directly via Python, so emojis are fine — but warn the user not to open + save `schedule.csv` in Excel before uploading.
- **Carousel aspect ratios.** Instagram rejects mixed aspect ratios in a carousel. Vista will warn at preview. Not this tool's job to validate — flag to user.
- **Folder names with trailing underscores or spaces.** Source folders from Google Drive downloads sometimes have junk (`C1_`, `Carousels-20260420T094945Z-3-001`). Use `folder_name` in the schedule item to set the clean name stored in the repo.
- **Source paths on Windows.** Use forward slashes or raw strings in `config.py`. The library normalizes.

## When to ask vs. act

Ask before:
- Deciding mappings between source filenames and caption keys.
- Dropping items to make alternation work.
- Choosing between same-hook variants.
- Pushing to GitHub (mention `--push` explicitly once CSV is verified).

Just do:
- Copying and inspecting source folders.
- Running `build.py` without `--push` to preview counts.
- Writing the batch config once inputs are clear.
- Pushing after the user confirms the CSV looks right.
