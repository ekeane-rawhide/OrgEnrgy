import sys
from reconstruct import build_category
from categories import CATEGORIES

for cat in CATEGORIES:
    print(f"=== {cat} ===", file=sys.stderr)
    out = build_category(cat)
    print(f"[{cat}] dated series for {len(out)} packages")
