import pandas as pd
import numpy as np

SOURCE = "/mnt/v-ger/omniverse/data/rubin/survey/rubin_one_night.csv"
OUTPUT = "/mnt/v-ger/omniverse/data/rubin/survey/rubin_demo_sequence.csv"

df = pd.read_csv(SOURCE)

demo = df.head(100).copy()

for col in ["RA", "dec", "alt", "az", "rotSkyPos", "pa", "rotTelPos"]:
    if col in demo.columns:
        demo[f"{col}_deg"] = np.degrees(demo[col])

cols = [
    "ID",
    "mjd",
    "RA_deg",
    "dec_deg",
    "alt_deg",
    "az_deg",
    "band",
    "filter",
    "exptime",
    "slewtime",
    "visittime",
    "airmass",
    "FWHMeff",
    "skybrightness",
    "scheduler_note",
    "target_name",
    "lmst",
]

demo = demo[[c for c in cols if c in demo.columns]]

demo.to_csv(OUTPUT, index=False)

print(f"Wrote {len(demo)} visits to:")
print(OUTPUT)
print()
print(demo.head(10).to_string(index=False))
