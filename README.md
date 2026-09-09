# Rubin Observatory Survey Visualization in NVIDIA Omniverse

An interactive technical visualization of simulated Vera C. Rubin Observatory survey operations, built with NVIDIA Omniverse, OpenUSD, Python, Rubin Scheduler, Astropy, and Blender.

The project drives an articulated Rubin telescope model through a sequence of simulated survey visits while visualizing the corresponding survey fields against a time-varying celestial sky.

This is an independent portfolio and learning project. It uses simulated survey data and publicly available source material and does **not** represent live Rubin Observatory telemetry.

This project is not an official publication or product of NSF NOIRLab, AURA, Vera C. Rubin Observatory, or NVIDIA.

## Project Goals

The primary goal of this project was to develop practical experience with NVIDIA Omniverse and explore a Blender-to-OpenUSD-to-Omniverse workflow for scientific and engineering visualization.

The project explores:

* Preparing an existing 3D asset for articulated simulation
* Blender-to-USD asset workflows
* OpenUSD scene hierarchy and transforms
* Custom Omniverse Kit extension development
* Scientific data integration
* Astronomical coordinate systems
* Time-varying visualization
* Interactive technical storytelling

This is a prototype and visualization project rather than an engineering-validated digital twin of the Rubin Observatory telescope.

## Features

* Articulated Rubin telescope with independent azimuth and elevation control
* Simulated observing visits generated with `rubin_scheduler`
* Telescope pointing driven by scheduled altitude and azimuth
* Survey footprints derived from celestial RA/Dec coordinates
* Astropy-based transformation of celestial coordinates into local Alt/Az
* LMST-driven celestial sky rotation
* Filter-specific `u`, `g`, `r`, `i`, `z`, and `y` footprint colors
* Slightly different marker sizes to distinguish overlapping revisits
* Custom Omniverse Kit extension providing:

  * Survey playback
  * Play/pause controls
  * Previous/next visit navigation
  * Playback-speed controls
  * Visit metadata
  * Footprint controls
  * Filter legend

## Architecture

At a high level, the visualization pipeline is:

```text
Rubin Scheduler
      |
      v
Simulated observing sequence
      |
      v
Python preprocessing
      |
      +----------------------+
      |                      |
      v                      v
Visit data            Footprint motion
Alt/Az, RA/Dec,       Astropy coordinate
LMST, timing          transformations
      |                      |
      +-----------+----------+
                  |
                  v
          Omniverse Kit Extension
                  |
        +---------+---------+
        |         |         |
        v         v         v
    Telescope   Sky     Footprints
        |         |         |
        +---------+---------+
                  |
                  v
              USD Stage
```

Astronomical coordinate transformations that would otherwise complicate the interactive runtime are currently precomputed with Astropy. The Omniverse extension handles visualization, playback, telescope articulation, sky orientation, and interaction.

## Telescope Asset Preparation

The telescope visualization began with a publicly available Rubin Observatory 3D model.

The source OBJ did not contain the articulation hierarchy needed by the simulation. I prepared the model in Blender by organizing the major moving components and establishing helper objects and pivot axes corresponding to the telescope's major mechanical degrees of freedom.

The resulting hierarchy was exported from Blender to USD and used programmatically by the Omniverse extension.

The primary articulation paths used by the visualization are:

```text
/Rubin_Telescope/Rubin_Root/Azimuth_Pivot
/Rubin_Telescope/Rubin_Root/Azimuth_Pivot/Elevation_Pivot
```

For this model:

```text
Azimuth   -> USD Z rotation
Elevation -> USD X rotation
```

The imported model requires the following elevation offset:

```text
USD elevation rotation = elevation_deg - 90
```

Some rendering artifacts were encountered during the Blender-to-USD workflow. Triangulating problematic polygon geometry in Blender before re-exporting resolved most of these issues.

The resulting articulation is suitable for this visualization, but it has not been validated as an engineering-accurate mechanical simulation of the Rubin telescope.

## Survey Data

The observing sequence is generated using Vera C. Rubin Observatory's `rubin_scheduler`.

The current demonstration uses 100 simulated visits.

Typical processed visit fields include:

```text
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
```

The telescope is driven primarily by the simulated altitude and azimuth values.

## Coordinate Systems

The project works with two important astronomical coordinate systems.

### Celestial coordinates

Survey fields are identified by:

```text
Right Ascension (RA)
Declination (Dec)
```

These describe locations in the celestial reference frame.

### Local horizon coordinates

The telescope is pointed using:

```text
Altitude
Azimuth
```

These describe the apparent direction of an object relative to the local horizon.

The relationship between RA/Dec and Alt/Az depends on observing location and time.

For footprint preprocessing, Astropy transforms celestial coordinates into local horizon coordinates using the simulated observation time and the location of Rubin Observatory on Cerro Pachón.

## Omniverse Coordinate Convention

The visualization uses:

```text
North = +Y
East  = -X
Up    = +Z
```

Local altitude and azimuth are converted into positions in this coordinate system for visualization.

## Time-Varying Footprint Positions

Survey footprints remain associated with their original RA/Dec positions on the celestial sphere, but their apparent Alt/Az positions change as Earth rotates.

For the current prototype, this motion is precomputed.

For each simulated visit time, the preprocessing pipeline transforms every footprint observed up to that point from RA/Dec into Alt/Az using Astropy.

For 100 visits, this produces:

```text
1 + 2 + 3 + ... + 100 = 5,050
```

time-dependent footprint positions.

The resulting data are consumed by the Omniverse extension during playback.

## Sky Motion

The celestial background is organized using a USD transform hierarchy:

```text
/Rubin_Telescope/SurveySky
    /CelestialFrame
        /DomeAxisFix
            /SiderealRotation
                /skyLight
```

Local sidereal time (LMST) from the simulated observations is used to update the visual orientation of the celestial background.

The current prototype uses a manually established reference alignment based on the first simulated visit:

```text
LMST = 12.663191562 h
SiderealRotation Y = -90 degrees
```

This approach was developed and visually validated for the prototype. A future version could replace the reference calibration with a more systematic derivation of the complete celestial coordinate transformation.

## Survey Footprint Visualization

Each simulated visit can create a distinct USD footprint prim, for example:

```text
/Rubin_Telescope/SurveyFootprints/Visit_000
```

Footprints can carry metadata including:

```text
rubin:visitID
rubin:filter
rubin:RA_deg
rubin:Dec_deg
rubin:markerRadius
```

Filters are visually distinguished using different colors:

```text
u  violet
g  green
r  orange/red
i  crimson
z  magenta
y  gold
```

Marker sizes vary slightly by filter to make overlapping revisits easier to distinguish. A very small radial offset is also used to reduce z-fighting.

These are visualization choices only. They do not represent changes in Rubin Observatory's physical field of view.

## Runtime Architecture

The current prototype uses a Kit runtime state machine rather than pre-authoring the complete survey as USD animation.

The extension updates telescope transforms while the application runs and represents different phases of the observing sequence, including slewing and visits.

This architecture also supports interactive controls such as playback speed, pause, and visit navigation.

For a fixed demonstration sequence, the animation could alternatively be pre-authored. The runtime approach was useful for exploring interactive application behavior and provides a path toward more dynamic simulation control in future versions.

## Scientific Validation and Limitations

Scientific validation in this prototype is limited.

The project was visually checked for consistency between:

* Simulated telescope Alt/Az pointing
* Survey footprint locations
* Processed astronomical coordinates
* Celestial coordinate reference imagery/grid

This does **not** constitute a complete numerical validation of the astronomical transformation pipeline or an engineering validation of the telescope mechanics.

One known visual limitation is that footprint markers are represented as geometry at a finite distance from the scene origin while the celestial background is effectively infinitely distant. This can introduce visible parallax between the markers and background.

A future implementation could represent footprints directly in celestial/angular space or composite them with the sky representation rather than treating them as finite-distance objects.

Other future validation and development areas include:

* Continuous sky rotation during simulation playback
* Telescope tracking throughout an exposure
* Numerical validation against simulation inputs
* Verification of telescope mechanical limits and motion against authoritative engineering specifications
* More systematic celestial-frame alignment
* More dynamic integration with `rubin_scheduler`

## Repository Contents

This repository intentionally contains the **project-specific source and supporting material**, rather than a complete NVIDIA Kit application distribution.

```text
source/
└── extensions/
    └── proctor.engineering.data/
        ├── data/
        │   ├── icon.png
        │   └── preview.png
        └── proctor/
            └── engineering/
                └── data/
                    └── extension.py

tools/
└── rubin/
    ├── generate_one_night.py
    ├── extract_demo_sequence.py
    └── precompute_footprint_motion.py

assets/
└── usd/
    └── rubin_telescope.usdc

docs/
└── UPDATE_WORKFLOW.md
```

NVIDIA-provided Kit App Template scaffolding is intentionally not redistributed in this repository.

Developers interested in running the project will need an appropriate NVIDIA Omniverse/Kit development environment and can integrate the project-specific extension source into their own Kit App Template project.

See `docs/UPDATE_WORKFLOW.md` for information about the survey-data preparation workflow.

## Technology

* NVIDIA Omniverse
* NVIDIA Kit App Template
* OpenUSD
* Python
* Rubin Scheduler
* Astropy
* Blender
* RTX rendering

## Credits and Data Sources

### NVIDIA Omniverse

This project depends on NVIDIA Omniverse, Kit, OpenUSD-related APIs, and NVIDIA development tooling.

NVIDIA software and NVIDIA-provided components remain governed by their applicable NVIDIA license terms and are not covered by any license applied to this project's original source code.

### Rubin Observatory Telescope Model

Source model:

Vera C. Rubin Observatory / NSF NOIRLab / AURA

https://noirlab.edu/public/products/models3d/Rubin-CAD-201801/

The source model was prepared in Blender for articulation and exported to USD for this visualization.

Please refer to the original source for its applicable attribution and licensing terms.

### NASA SVS Deep Star Map

NASA/Goddard Space Flight Center
Scientific Visualization Studio

Gaia DR2: ESA/Gaia/DPAC

https://svs.gsfc.nasa.gov/4851/

### Rubin Scheduler

Vera C. Rubin Observatory `rubin_scheduler`

https://github.com/lsst/rubin_scheduler

The project uses Rubin Scheduler to generate simulated observing sequences. The scheduler is a separate open-source project governed by its own license.

### Astropy

Astropy is used for astronomical time and coordinate transformations.

https://www.astropy.org/

Additional attribution and provenance information is provided in `CREDITS.md`.

## Development Approach

This project was developed as an independent learning and portfolio exercise.

I directed the scientific visualization concept, asset preparation, scene design, coordinate-system integration, interaction design, testing, validation, and technical direction.

ChatGPT and Codex were used extensively as implementation collaborators for Python development, debugging, documentation, and exploration of the Omniverse APIs.

The project should therefore be understood both as a demonstration of scientific/technical visualization work and as an exploration of AI-assisted software development.

## Status

Prototype / portfolio project.

The current implementation demonstrates the intended visualization and interaction concepts but leaves several areas for future refinement, particularly scientific validation, celestial-coordinate rendering, asset-pipeline architecture, and deeper use of OpenUSD composition.
