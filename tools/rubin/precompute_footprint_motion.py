import pandas as pd
import numpy as np

from astropy.coordinates import AltAz, EarthLocation, SkyCoord
from astropy.time import Time
import astropy.units as u


SOURCE = "/mnt/v-ger/omniverse/data/rubin/survey/rubin_demo_sequence.csv"
OUTPUT = "/mnt/v-ger/omniverse/data/rubin/survey/rubin_footprint_motion.csv"

# Rubin Observatory / Cerro Pachon
location = EarthLocation(
    lat=-30.244633 * u.deg,
    lon=-70.749417 * u.deg,
    height=2647 * u.m,
)

df = pd.read_csv(SOURCE)

rows = []

for frame_index, frame in df.iterrows():
    obstime = Time(frame["mjd"], format="mjd", scale="utc")

    altaz_frame = AltAz(
        obstime=obstime,
        location=location,
    )

    for footprint_index, footprint in df.iloc[: frame_index + 1].iterrows():

        sky = SkyCoord(
            ra=footprint["RA_deg"] * u.deg,
            dec=footprint["dec_deg"] * u.deg,
            frame="icrs",
        )

        local = sky.transform_to(altaz_frame)

        rows.append(
            {
                "frame": frame_index,
                "frame_mjd": frame["mjd"],
                "footprint": footprint_index,
                "visit_id": footprint["ID"],
                "RA_deg": footprint["RA_deg"],
                "dec_deg": footprint["dec_deg"],
                "alt_deg": local.alt.deg,
                "az_deg": local.az.deg,
                "filter": footprint["filter"],
            }
        )

out = pd.DataFrame(rows)
out.to_csv(OUTPUT, index=False)

print(f"Wrote {len(out)} footprint positions")
print(f"Output: {OUTPUT}")
print()
print(out.head(20).to_string(index=False))
