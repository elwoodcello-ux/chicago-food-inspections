"""Download the Chicago Food Inspections dataset to data/raw/."""
import urllib.request
from pathlib import Path

URL = "https://data.cityofchicago.org/api/views/4ijn-s7e5/rows.csv?accessType=DOWNLOAD"
DEST = Path("data/raw/food_inspections.csv")


def main():
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if DEST.exists():
        print(f"Already downloaded: {DEST} ({DEST.stat().st_size / 1e6:.0f} MB)")
        return
    print("Downloading. This is a few hundred MB and may take several minutes.")
    urllib.request.urlretrieve(URL, DEST)
    print(f"Saved to {DEST} ({DEST.stat().st_size / 1e6:.0f} MB)")


if __name__ == "__main__":
    main()
