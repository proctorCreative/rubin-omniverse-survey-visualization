# Updating the Rubin Simulation Data

This document is a short, machine-independent checklist for refreshing the simulated Rubin survey data used by the Omniverse visualization.

The examples below assume:

- the Rubin Scheduler Python environment is already installed,
- the required Rubin simulation support data has been downloaded,
- the project source and data-preparation scripts are available locally.

Adjust paths to match your own installation.

## 1. Activate the Rubin Scheduler environment

Activate the Python environment that contains `rubin_scheduler` and Astropy.

Example:

```bash
source /path/to/rubin-env/bin/activate
```

If your Rubin support data is stored outside the default location, set:

```bash
export RUBIN_SIM_DATA_DIR=/path/to/rubin_sim_data
```

If the scheduler support data has not been downloaded yet, run:

```bash
scheduler_download_data
```

This is usually a one-time setup unless the Rubin simulation data products need to be refreshed.

## 2. Generate a simulated observing night

Run the survey-generation script:

```bash
python tools/rubin/generate_one_night.py
```

The script generates a simulated Rubin observing sequence for one night.

Typical outputs include:

```text
rubin_one_night.db
rubin_one_night.csv
```

These are generated data products and do not need to be committed to Git unless there is a specific reason to preserve them.

## 3. Extract the demonstration sequence

Run:

```bash
python tools/rubin/extract_demo_sequence.py
```

This produces the smaller sequence used by the Omniverse demonstration.

Current expected output:

```text
rubin_demo_sequence.csv
```

The extraction script can be edited to change the number of visits or the selection strategy.

The Omniverse extension expects fields including:

```text
ID
mjd
RA_deg
dec_deg
alt_deg
az_deg
band
filter
exptime
slewtime
visittime
airmass
FWHMeff
skybrightness
scheduler_note
target_name
lmst
```

## 4. Precompute historical footprint motion

Run:

```bash
python tools/rubin/precompute_footprint_motion.py
```

Expected output:

```text
rubin_footprint_motion.csv
```

This preprocessing step uses Astropy to transform each historical survey footprint from RA/Dec into local Alt/Az at each visit time.

That is what allows previously observed fields to move with the celestial sky while the telescope remains in the local horizontal coordinate system.

For 100 visits, the motion table contains:

```text
1 + 2 + 3 + ... + 100 = 5050
```

footprint positions.

## 5. Place the runtime data where the extension expects it

The extension requires two CSV inputs:

```text
rubin_demo_sequence.csv
rubin_footprint_motion.csv
```

You can either:

1. place those files in the paths configured in the extension, or
2. update the `VISIT_FILE` and `MOTION_FILE` constants in `extension.py` to match your local data directory.

For portability, consider replacing hard-coded absolute paths with environment variables or a project-relative data location in a future update.

## 6. Verify the sky calibration

Before running a full playback, confirm that:

- the telescope points at the current survey footprint,
- the survey footprint matches the expected celestial location,
- the north and south celestial poles remain fixed,
- the star background rotates consistently with local sidereal time.

The current sky hierarchy is:

```text
/Rubin_Telescope/SurveySky
    /CelestialFrame
        /DomeAxisFix
            /SiderealRotation
                /skyLight
```

The first simulated visit was calibrated with approximately:

```text
LMST = 12.663191562 h
SiderealRotation Y = -90 degrees
```

## 7. Build the Omniverse application

From the NVIDIA Kit App Template working directory:

```bash
./repo.sh build
```

## 8. Launch the application

Run:

```bash
./repo.sh launch
```

Then:

1. Open the Rubin Observatory control panel.
2. Click **Load Survey Sequence**.
3. Clear old survey footprints if necessary.
4. Step through a few visits.
5. Confirm telescope pointing and sky alignment.
6. Start playback at the desired speed.

## 9. Quick validation checklist

Before considering the updated dataset ready:

- Visit count is correct.
- Telescope azimuth/elevation values look reasonable.
- The first visit aligns with its survey footprint.
- A later visit also aligns correctly.
- Previously created footprints move with the sky.
- The star background tracks with LMST.
- Filter colors and legend display correctly.
- Overlapping revisits do not visibly z-fight.
