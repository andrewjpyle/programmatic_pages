"""Load data/parks.csv into the Park table. SAMPLE DATA: every park and town is fictional.

    python manage.py migrate
    python seed.py
"""

import csv
import os
import sys
from decimal import Decimal
from pathlib import Path


def main() -> None:
    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    import django

    django.setup()
    from parks.models import Park

    with (here / "data" / "parks.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))

    Park.objects.all().delete()
    Park.objects.bulk_create(
        Park(
            slug=r["slug"],
            name=r["name"],
            city=r["city"],
            acres=int(r["acres"]),
            trail_miles=Decimal(r["trail_miles"]) if r["trail_miles"] else None,
            opened=int(r["opened"]),
            description=r["description"],
        )
        for r in rows
    )
    print(f"Loaded {len(rows)} fictional parks")


if __name__ == "__main__":
    main()
