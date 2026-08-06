"""
Run the same broad-pool qualification scan (proven feasible on
http_client) against every pre-registered category, reusing the cached
candidate pool and cached abbreviated docs from step 1.
"""
import json
import os
import sys
from crawl import abbrev_doc
from categories import CATEGORIES

def package_ever_depends_on_any(pkg, competitors):
    doc = abbrev_doc(pkg)
    if not doc or "versions" not in doc:
        return None
    hits = {}
    for vstr, vmeta in doc["versions"].items():
        deps = vmeta.get("dependencies", {}) or {}
        chosen = [c for c in competitors if c in deps]
        if chosen:
            hits[vstr] = chosen
    return hits if hits else None

def main():
    pool = json.load(open("candidate_pool.json"))
    for category, competitors in CATEGORIES.items():
        out_path = f"qualifying_{category}.json"
        if os.path.exists(out_path):
            existing = json.load(open(out_path))
            if len(existing) > 5:
                print(f"[{category}] already done ({len(existing)-1} qualifying), skipping", file=sys.stderr)
                continue
        qualifying = {}
        for i, pkg in enumerate(pool):
            if pkg in competitors:
                continue
            hits = package_ever_depends_on_any(pkg, competitors)
            if hits:
                qualifying[pkg] = hits
            if i % 500 == 0:
                print(f"  [{category}] scanned {i}/{len(pool)}, qualifying so far={len(qualifying)}", file=sys.stderr)
        json.dump(qualifying, open(out_path, "w"), indent=1)
        switchers = {p: h for p, h in qualifying.items()
                     if len({c for chosen in h.values() for c in chosen}) > 1}
        print(f"[{category}] qualifying={len(qualifying)} switchers={len(switchers)}")

if __name__ == "__main__":
    main()
