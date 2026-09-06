from pathlib import Path

import numpy as np
import pandas as pd

from rubin_scheduler.scheduler.example import (
    generate_baseline_coresched,
    run_sched,
)
from rubin_scheduler.utils import SURVEY_START_MJD


OUT_DIR = Path("/mnt/v-ger/omniverse/data/rubin/survey")
OUT_DIR.mkdir(parents=True, exist_ok=True)

DB_FILE = OUT_DIR / "rubin_one_night.db"
CSV_FILE = OUT_DIR / "rubin_one_night.csv"

survey_start = float(SURVEY_START_MJD)

print(f"Survey start MJD: {survey_start}")

print("Building baseline scheduler...")
scheduler = generate_baseline_coresched(
    nside=32,
    survey_start_mjd=survey_start,
    no_too=True,
)

print("Running one-night simulation...")
observatory, scheduler, observations = run_sched(
    scheduler,
    survey_length=1.0,
    nside=32,
    filename=str(DB_FILE),
    verbose=True,
    survey_start_mjd=survey_start,
)

print(f"\nGenerated {len(observations)} visits")

print("\nAvailable fields:")
print(observations.dtype.names)

# Convert the structured ObservationArray into a DataFrame.
df = pd.DataFrame.from_records(observations)

df.to_csv(CSV_FILE, index=False)

print(f"\nDatabase: {DB_FILE}")
print(f"CSV:      {CSV_FILE}")

print("\nFirst five visits:")
print(df.head().to_string())
