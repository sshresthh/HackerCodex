import json, glob, os
from backend.db.firestore_utils import insert_event
from backend.normalizers.normalize import NORMALIZERS

def load_and_insert_all():
    for fname in glob.glob("backend/scrapers/data/*.json"):
        source = os.path.basename(fname).replace(".json", "")
        normalizer = NORMALIZERS.get(source)
        if not normalizer:
            print(f"⚠️ No normalizer for {source}, skipping")
            continue

        with open(fname, encoding="utf-8") as f:
            data = json.load(f)

        count = 0
        for ev in data:
            doc = normalizer(ev)
            insert_event(doc)
            count += 1

        print(f"Inserted {count} events from {source}")

if __name__ == "__main__":
    load_and_insert_all()
