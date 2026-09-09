# Credits, Data Sources, and Third-Party Components

This document records the primary external software, data, and source assets used in the **Rubin Observatory Survey Visualization in NVIDIA Omniverse** project.

This is an independent portfolio and learning project and is not an official publication or product of NSF NOIRLab, AURA, Vera C. Rubin Observatory, or NVIDIA.

The repository intentionally contains primarily project-specific source and supporting material. External software, development frameworks, datasets, and source assets remain subject to their respective licenses and terms.

## NVIDIA Omniverse and Kit

This project was developed for NVIDIA Omniverse using NVIDIA Kit, OpenUSD-related APIs, and NVIDIA development tooling.

NVIDIA-provided Kit App Template scaffolding used during development is intentionally not redistributed as part of the current repository.

The repository instead contains the project-specific extension source and supporting files needed to understand and reconstruct the visualization within an appropriate Omniverse/Kit development environment.

NVIDIA Omniverse, Kit, and other NVIDIA-provided software and components remain governed by their applicable NVIDIA license terms.

NVIDIA Omniverse:

https://developer.nvidia.com/omniverse

NVIDIA Kit App Template:

https://github.com/NVIDIA-Omniverse/kit-app-template

## Rubin Observatory Telescope Model

The telescope asset used by this visualization is derived from a publicly available Vera C. Rubin Observatory 3D model.

Source:

**CAD models of Rubin Observatory Telescope**
Vera C. Rubin Observatory / NSF NOIRLab / AURA

https://noirlab.edu/public/products/models3d/Rubin-CAD-201801/

For this project, the source model was prepared in Blender to support articulated visualization. Major moving components were organized around azimuth and elevation pivot structures and the resulting asset was exported to USD for use in Omniverse.

The repository includes the resulting project-specific USD asset:

```text
assets/usd/rubin_telescope.usdc
```

Please consult the original NOIRLab/Rubin source page for the authoritative licensing and attribution requirements applicable to the source model.

## Rubin Scheduler

Simulated observing visits are generated using Vera C. Rubin Observatory's `rubin_scheduler`.

Project:

**rubin_scheduler**
Vera C. Rubin Observatory / LSST software team

https://github.com/lsst/rubin_scheduler

The scheduler is used to generate simulated survey observations containing information such as observation time, telescope altitude and azimuth, celestial RA/Dec coordinates, filter, exposure time, slew time, and local mean sidereal time.

`rubin_scheduler` is a separate software project and remains governed by its own license.

The scheduler itself is not redistributed by this repository.

## Astropy

Astropy is used during preprocessing for astronomical time and coordinate transformations.

In particular, the project uses Astropy to transform fixed celestial RA/Dec survey positions into apparent local Alt/Az coordinates at the simulated observation times and observing location.

Project:

**The Astropy Project**

https://www.astropy.org/

Astropy is a separate open-source software project and remains governed by its own license.

## NASA Scientific Visualization Studio Deep Star Map

The celestial background used during development is based on:

**Deep Star Maps 2020**
Visualization by Ernie Wright
NASA Goddard Space Flight Center
Scientific Visualization Studio
SVS ID 4851

https://svs.gsfc.nasa.gov/4851/

The visualization incorporates astronomical source data including Gaia DR2.

Gaia mission data:

**ESA/Gaia/DPAC**

The star-map source remains subject to the attribution and usage guidance provided by NASA Scientific Visualization Studio and the underlying data providers.

The original NASA SVS star-map files are not redistributed by this repository.

## Blender

Blender was used to prepare the telescope asset for the Omniverse visualization, including organization of the model around the articulation hierarchy required for azimuth and elevation control.

Blender:

https://www.blender.org/

## OpenUSD

The project uses OpenUSD as the scene-description framework underlying the Omniverse visualization.

OpenUSD:

https://openusd.org/

USD is used for scene hierarchy, telescope articulation, transforms, visualization geometry, and project-specific metadata.

## Project-Specific Work

Project-specific work includes the scientific visualization concept, telescope asset preparation, scene design, coordinate-system integration, visualization design, interaction design, preprocessing workflow, testing, validation, documentation, and technical direction.

The repository includes project-specific Python code for:

* Generating a simulated Rubin observing sequence
* Extracting and converting a demonstration sequence
* Precomputing time-dependent survey-footprint positions
* Controlling the visualization within an Omniverse Kit extension
* Telescope articulation and survey playback
* Celestial sky orientation
* Survey-footprint creation and visualization
* Interactive visualization controls

## AI-Assisted Development

ChatGPT and Codex were used extensively as implementation collaborators during development.

Their use included assistance with:

* Python implementation
* Omniverse and OpenUSD API exploration
* Debugging
* Refactoring
* Data-processing workflows
* Documentation
* Investigation of technical alternatives

The scientific visualization goals, project direction, asset preparation, interaction design, testing, evaluation of results, and decisions about how the prototype should behave were directed by the project author.

This project is therefore also an example of an AI-assisted technical development workflow.

## Repository Distribution

The current repository is intentionally **not a complete redistribution of the development environment** used to build the project.

It contains project-specific source and supporting material while omitting NVIDIA-provided Kit App Template scaffolding and other external software components.

Developers wishing to reconstruct the project should obtain the appropriate software and dependencies from their original providers and integrate the project-specific extension source into an appropriate NVIDIA Omniverse/Kit development environment.

Third-party software and assets are not covered by any license applied to the project's original source code and remain subject to their respective licenses and terms.

## Repository History Note

During initial repository setup, unrelated source files were inadvertently included in the repository.

Those files have been removed from the current project tree. GitHub contributor attribution or historical commits may still reflect that earlier repository state.

Those contributors are not responsible for this project or its contents.
