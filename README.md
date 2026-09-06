# Rubin Observatory Survey Visualization in NVIDIA Omniverse

An interactive technical visualization of simulated Vera C. Rubin Observatory survey operations, built with NVIDIA Omniverse, OpenUSD, Python, Rubin Scheduler, Astropy, and Blender.

The project drives an articulated Rubin telescope model through simulated survey visits while survey field markers accumulate on a time-varying celestial sky.

This project uses simulated survey data and does not represent live Rubin telescope telemetry.

## Features

- Articulated Rubin telescope with azimuth and elevation control
- Simulated observing visits generated with `rubin_scheduler`
- Telescope pointing driven by scheduled altitude and azimuth
- Celestial survey footprints derived from RA/Dec coordinates
- Astropy-based coordinate transformation for historical footprint motion
- LMST-driven sky rotation
- Filter-specific `u`, `g`, `r`, `i`, `z`, and `y` marker colors
- Slightly different marker sizes to help distinguish overlapping revisits
- Custom Omniverse Kit extension with:
  - survey loading
  - previous / next visit controls
  - play / pause
  - playback speed
  - animated telescope slews
  - visit metadata
  - footprint controls
  - filter legend

## Project structure

```text
source/
├── apps/
│   └── proctor.engineering.viewer.kit
└── extensions/
    └── proctor.engineering.data/

tools/
└── rubin/
    ├── generate_one_night.py
    ├── extract_demo_sequence.py
    └── precompute_footprint_motion.py

docs/
├── UPDATE_WORKFLOW.md
└── YOUTUBE_DEMO_OUTLINE.md
Coordinate conventions

The visualization uses:

North = +Y
East  = -X
Up    = +Z

The telescope articulation paths are:

/Rubin_Telescope/Rubin_Root/Azimuth_Pivot
/Rubin_Telescope/Rubin_Root/Azimuth_Pivot/Elevation_Pivot

The imported model points at zenith when the elevation pivot X rotation is zero, so:

USD elevation rotation = elevation_deg - 90
Survey data

The project uses simulated observations generated with Vera C. Rubin Observatory's rubin_scheduler.

Typical visit fields include:

ID
mjd
RA_deg
dec_deg
alt_deg
az_deg
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

The current demonstration sequence uses 100 simulated visits.

Time-varying sky coordinates

The telescope is controlled in local Alt/Az coordinates, while survey fields are defined in celestial RA/Dec coordinates.

To keep previously observed fields attached to the celestial sphere, Astropy is used to precompute the apparent altitude and azimuth of each historical footprint at each visit time.

For 100 visits, this produces:

1 + 2 + 3 + ... + 100 = 5050

time-dependent footprint positions.

Sky motion

The celestial background is rendered with a Dome Light.

Local sidereal time from the scheduler data is used to rotate the sky so the background and survey footprints remain synchronized.

The sky transform hierarchy is:

/Rubin_Telescope/SurveySky
    /CelestialFrame
        /DomeAxisFix
            /SiderealRotation
                /skyLight

The first simulated visit was calibrated with:

LMST = 12.663191562 h
SiderealRotation Y = -90 degrees

Subsequent sky rotation is calculated relative to that reference.

Survey footprint visualization

Each visit is represented by a distinct USD prim:

/Rubin_Telescope/SurveyFootprints/Visit_000
/Rubin_Telescope/SurveyFootprints/Visit_001
...

Footprints can store metadata including:

rubin:visitID
rubin:filter
rubin:RA_deg
rubin:Dec_deg
rubin:markerRadius

Filter-specific colors are used for visualization:

u  violet
g  green
r  orange/red
i  crimson
z  magenta
y  gold

Marker sizes vary slightly by filter to make overlapping revisits easier to read.

A very small radial offset is also used to reduce coincident-surface artifacts.

These size differences are visualization choices only; Rubin's physical field of view does not change with filter.

Build and launch

This repository contains project-specific source files intended to be used with NVIDIA's Kit App Template.

From a Kit App Template working copy:

./repo.sh build
./repo.sh launch

See docs/UPDATE_WORKFLOW.md for the data preparation and update steps.

Technology
NVIDIA Omniverse
NVIDIA Kit App Template
OpenUSD
Python
Rubin Scheduler
Astropy
Blender
RTX rendering
Credits

See CREDITS.md.

Project goals

This project explores the integration of:

scientific survey data
CAD-to-USD asset preparation
articulated scene control
astronomical coordinate systems
time-varying visualization
OpenUSD metadata
custom Omniverse Kit development
interactive technical storytelling
Future improvements

Potential next steps include:

more realistic field-of-view geometry
continuous sidereal motion during slews
richer scheduler analytics
additional metadata displays
camera presets and presentation modes
larger survey sequences
revisit-density and cadence visualization
survey strategy comparison
