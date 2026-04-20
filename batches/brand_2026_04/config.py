"""Batch config: Qubit Capital Brand, April 2026.

Template for future batches — copy this directory, rename, edit the
paths/schedule below, then run:
    python build.py batches/<new_batch>/config.py --push
"""

from vista_bulk import apply_dates

BRAND = r"C:/Users/Saurabh/OneDrive/Desktop/Brand"
CAROUSELS_SRC = f"{BRAND}/Carousels-20260420T094945Z-3-001/Carousels"
STATICS_SRC = f"{BRAND}/Statics-20260420T094937Z-3-001/Statics"

# Items in posting order (date is assigned by apply_dates).
# - type: "static" | "carousel"
# - caption_key: section key in Captions.txt (for carousels) or filename (for statics)
# - src_file / src_folder: absolute path to the source media
# - folder_name (carousels only): sanitized folder name in the repo (defaults to basename)
_items = [
    {"type": "static",   "caption_key": "founders_s1.png", "src_file":   f"{STATICS_SRC}/founders_s1.png"},
    {"type": "carousel", "caption_key": "A1",               "src_folder": f"{CAROUSELS_SRC}/C1_",  "folder_name": "C1"},
    {"type": "static",   "caption_key": "v2_s2.png",        "src_file":   f"{STATICS_SRC}/v2_s2.png"},
    {"type": "carousel", "caption_key": "A2",               "src_folder": f"{CAROUSELS_SRC}/C2"},
    {"type": "static",   "caption_key": "founders_s2.png", "src_file":   f"{STATICS_SRC}/founders_s2.png"},
    {"type": "carousel", "caption_key": "A3",               "src_folder": f"{CAROUSELS_SRC}/C3"},
    {"type": "static",   "caption_key": "founders_s4.png", "src_file":   f"{STATICS_SRC}/founders_s4.png"},
    {"type": "carousel", "caption_key": "A4",               "src_folder": f"{CAROUSELS_SRC}/C4"},
    {"type": "static",   "caption_key": "v2_s4.png",        "src_file":   f"{STATICS_SRC}/v2_s4.png"},
    {"type": "carousel", "caption_key": "A5",               "src_folder": f"{CAROUSELS_SRC}/C5"},
    {"type": "static",   "caption_key": "static_s3.png",    "src_file":   f"{STATICS_SRC}/static_s3.png"},
    {"type": "carousel", "caption_key": "B2",               "src_folder": f"{CAROUSELS_SRC}/C6"},
    {"type": "static",   "caption_key": "founders_s3.png", "src_file":   f"{STATICS_SRC}/founders_s3.png"},
    {"type": "carousel", "caption_key": "B3",               "src_folder": f"{CAROUSELS_SRC}/C7"},
    {"type": "static",   "caption_key": "static_s2.png",    "src_file":   f"{STATICS_SRC}/static_s2.png"},
    {"type": "carousel", "caption_key": "B4",               "src_folder": f"{CAROUSELS_SRC}/C8"},
    {"type": "static",   "caption_key": "v2_s5.png",        "src_file":   f"{STATICS_SRC}/v2_s5.png"},
    {"type": "carousel", "caption_key": "B5",               "src_folder": f"{CAROUSELS_SRC}/C9"},
    {"type": "static",   "caption_key": "static_s10.png",   "src_file":   f"{STATICS_SRC}/static_s10.png"},
    {"type": "carousel", "caption_key": "B6",               "src_folder": f"{CAROUSELS_SRC}/C10"},
]

CONFIG = {
    "time": "7:00 pm",  # Vista account's configured timezone (GMT+6 for this batch)
    "captions": {
        "carousels": {
            "type": "text_sections",
            "path": f"{CAROUSELS_SRC}/Captions.txt",
            "section_prefix": "CAROUSEL",
        },
        "statics": {
            "type": "xlsx_by_filename",
            "path": f"{STATICS_SRC}/Static Captions.xlsx",
            "filename_col": "File Name",
            "caption_col": "Caption",
        },
    },
    "schedule": apply_dates(_items, start="2026-04-21", post_days=("Mon", "Tue", "Wed", "Thu")),
}
