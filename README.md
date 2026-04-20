# Vista Social Bulk Schedule

Public media host + CSV generator for Vista Social's bulk-publishing upload.

## What it does

1. Copies your media (carousels, statics) into a batch folder in this repo.
2. Parses captions from your source files (text sections or xlsx rows).
3. Assigns dates per a posting-day rule (e.g., Mon–Thu).
4. Writes a `schedule.csv` matching Vista Social's bulk-publishing template.
5. (Optional) `git push` — raw GitHub URLs go live immediately.

You then upload `schedule.csv` in Vista Social → Bulk Publishing → Import from CSV.

## Repo layout

```
vista_bulk.py                 # library: parsers, media copy, csv writer, schedule helper
build.py                      # CLI: python build.py <config.py> [--push]
batches/
  brand_2026_04/
    config.py                 # this batch's config (paths, schedule, time)
    media/                    # auto-populated: carousels/, statics/
    schedule.csv              # auto-generated CSV (upload this to Vista)
```

## Starting a new batch

1. Copy an existing batch folder and rename:
   ```
   cp -r batches/brand_2026_04 batches/<new_batch_name>
   ```
2. Edit `batches/<new_batch_name>/config.py`:
   - Source paths (`CAROUSELS_SRC`, `STATICS_SRC`)
   - Caption source types (`text_sections` or `xlsx_by_filename`)
   - The `_items` list — one entry per post, in posting order
   - `start` date in `apply_dates(...)` and `post_days`
   - Global `time`
3. Run:
   ```
   python build.py batches/<new_batch_name>/config.py --push
   ```
4. Upload `batches/<new_batch_name>/schedule.csv` to Vista Social.

## Caption source types

**`text_sections`** — for files where each caption lives under a section header like `CAROUSEL A1: ...`.
Each post's `caption_key` matches the section key (`A1`, `B2`, etc.).

**`xlsx_by_filename`** — for spreadsheets with one row per piece. The `caption_key` matches the value in the filename column.

Add new parsers in `vista_bulk.py` if your source format differs.

## Schedule item shape

```python
{"type": "carousel", "caption_key": "A1",               "src_folder": "...", "folder_name": "C1"}
{"type": "static",   "caption_key": "founders_s1.png",  "src_file":   "..."}
```

- `folder_name` (carousel only) — the folder name inside the repo; defaults to the source basename.
- Per-item `time` override is supported (else falls back to `CONFIG["time"]`).

`apply_dates(items, start, post_days)` fills in `date` on each item, skipping non-post days.

## Vista CSV format (what this tool writes)

Exact headers (space before `time` is intentional — matches Vista's sample):

```
message,type,link, time
<caption>,image,<public url>,2026-04-21 7:00 pm
```

- Carousels: 5 rows with identical `message` + ` time` + image type, different `link`s per slide. Vista groups them automatically.
- Multi-line captions are properly CSV-quoted; don't worry about the raw line count.

## Gotchas

- **Times are local to your Vista account's timezone** — the CSV doesn't carry a TZ. Set the Vista account to the correct zone before uploading.
- **Media URLs must be public.** This repo is public; raw.githubusercontent.com URLs work out of the box. Don't flip the repo private.
- **200-row CSV limit** in Vista; 100 recommended. Each carousel = slide_count rows.
- **Captions with emojis** — fine here (Python writes UTF-8), but don't author CSVs in Excel which strips them.
