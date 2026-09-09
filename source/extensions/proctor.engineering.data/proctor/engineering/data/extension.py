
# This software contains source code provided by NVIDIA Corporation.

import csv
import math
import time

import omni.ext
import omni.kit.app
import omni.ui as ui
from omni.ui import color as cl
import omni.usd

from pxr import Gf, Sdf, UsdGeom, UsdShade


AZIMUTH_PATH = "/Rubin_Telescope/Rubin_Root/Azimuth_Pivot"
ELEVATION_PATH = "/Rubin_Telescope/Rubin_Root/Azimuth_Pivot/Elevation_Pivot"

SIDEREAL_ROTATION_PATH = (
    "/Rubin_Telescope/SurveySky/"
    "CelestialFrame/DomeAxisFix/SiderealRotation"
)

# Visit 0 calibration: the celestial grid aligns correctly at this LMST
# when SiderealRotation Y is -90 degrees.
SIDEREAL_REFERENCE_LMST_HOURS = 12.663191562149123
SIDEREAL_REFERENCE_Y_DEG = -90.0

# If the grid moves the wrong RA direction in a later-visit test,
# change this one value from +1.0 to -1.0.
SIDEREAL_DIRECTION = 1.0

FOOTPRINT_ROOT = "/Rubin_Telescope/SurveyFootprints"

# Radius of our local sky visualization.
FOOTPRINT_RADIUS = 100000.0

# Nominal Rubin footprint marker radius in this visualization.
# The real field of view is the same for every filter; the small size
# differences below are a visualization device so overlapping revisits
# remain readable instead of producing coincident-surface z-fighting.
FOOTPRINT_SIZE = 3050.0

FILTER_COLORS = {
    "u": Gf.Vec3f(0.45, 0.15, 1.00),  # violet
    "g": Gf.Vec3f(0.10, 1.00, 0.45),  # green
    "r": Gf.Vec3f(1.00, 0.25, 0.05),  # orange-red
    "i": Gf.Vec3f(1.00, 0.05, 0.25),  # crimson
    "z": Gf.Vec3f(0.80, 0.05, 1.00),  # magenta
    "y": Gf.Vec3f(1.00, 0.75, 0.10),  # gold
    "default": Gf.Vec3f(1.00, 1.00, 1.00),
}

# Slightly different marker radii by filter.
# These are intentionally close to the nominal 3050-unit radius.
FILTER_MARKER_SIZES = {
    "u": 2750.0,
    "g": 2870.0,
    "r": 2990.0,
    "i": 3110.0,
    "z": 3230.0,
    "y": 3350.0,
    "default": FOOTPRINT_SIZE,
}

# Tiny per-visit radial separation. This is visually negligible at a
# 100000-unit sky radius but prevents exact same-filter revisits from
# occupying mathematically identical surfaces.
FOOTPRINT_DEPTH_STEP = 8.0

VISIT_FILE = (
    "/mnt/v-ger/omniverse/data/rubin/survey/"
    "rubin_demo_sequence.csv"
)

MOTION_FILE = (
    "/mnt/v-ger/omniverse/data/rubin/survey/"
    "rubin_footprint_motion.csv"
)


class MyExtension(omni.ext.IExt):

    def on_startup(self, _ext_id):
        print("[proctor.engineering.data] Extension startup")

        self._visits = []
        self._motion_by_frame = {}
        self._visit_index = 0

        self._playing = False
        self._phase = "idle"

        self._phase_start_time = 0.0
        self._phase_duration = 0.0

        self._start_az = 0.0
        self._start_el = 0.0
        self._target_az = 0.0
        self._target_el = 0.0

        self._playback_speed = 10.0

        self._window = ui.Window(
            "Rubin Observatory Control",
            width=420,
            height=750,
        )

        with self._window.frame:
            with ui.VStack(spacing=10):

                ui.Label(
                    "RUBIN OBSERVATORY",
                    height=30,
                    style={"font_size": 20},
                )

                ui.Label("Survey Visit Control", height=24)

                ui.Button(
                    "Load Survey Sequence",
                    height=38,
                    clicked_fn=self._load_data,
                )

                ui.Separator()

                with ui.HStack(height=28):
                    ui.Label("Visit", width=120)
                    self._visit_label = ui.Label("-")

                with ui.HStack(height=28):
                    ui.Label("Azimuth", width=120)
                    self._az_label = ui.Label("-")

                with ui.HStack(height=28):
                    ui.Label("Elevation", width=120)
                    self._el_label = ui.Label("-")

                with ui.HStack(height=28):
                    ui.Label("RA", width=120)
                    self._ra_label = ui.Label("-")

                with ui.HStack(height=28):
                    ui.Label("Dec", width=120)
                    self._dec_label = ui.Label("-")

                with ui.HStack(height=28):
                    ui.Label("Filter", width=120)
                    self._filter_label = ui.Label("-")

                with ui.HStack(height=28):
                    ui.Label("Slew time", width=120)
                    self._slew_label = ui.Label("-")

                with ui.HStack(height=28):
                    ui.Label("Exposure", width=120)
                    self._exposure_label = ui.Label("-")

                ui.Separator()

                with ui.HStack(height=38):
                    ui.Button(
                        "Previous Visit",
                        clicked_fn=self._previous_visit,
                    )
                    ui.Button(
                        "Next Visit",
                        clicked_fn=self._next_visit,
                    )

                with ui.HStack(height=38):
                    ui.Button(
                        "Play",
                        clicked_fn=self._play,
                    )
                    ui.Button(
                        "Pause",
                        clicked_fn=self._pause,
                    )

                ui.Separator()

                ui.Label("Playback Speed", height=24)

                with ui.HStack(height=36):
                    ui.Button(
                        "1x",
                        clicked_fn=lambda: self._set_speed(1.0),
                    )
                    ui.Button(
                        "5x",
                        clicked_fn=lambda: self._set_speed(5.0),
                    )
                    ui.Button(
                        "10x",
                        clicked_fn=lambda: self._set_speed(10.0),
                    )
                    ui.Button(
                        "25x",
                        clicked_fn=lambda: self._set_speed(25.0),
                    )
                    ui.Button(
                        "50x",
                        clicked_fn=lambda: self._set_speed(50.0),
                    )

                with ui.HStack(height=28):
                    ui.Label("Speed", width=120)
                    self._speed_label = ui.Label("10x")

                with ui.HStack(height=28):
                    ui.Label("State", width=120)
                    self._state_label = ui.Label("Idle")

                ui.Separator()

                ui.Label("Survey Footprints", height=24)

                ui.Label("Filter Legend", height=20)

                with ui.HStack(height=24, spacing=8):
                    self._build_filter_legend_item(
                        "u",
                        "7326FF",
                    )
                    self._build_filter_legend_item(
                        "g",
                        "1AFF73",
                    )
                    self._build_filter_legend_item(
                        "r",
                        "FF400D",
                    )

                with ui.HStack(height=24, spacing=8):
                    self._build_filter_legend_item(
                        "i",
                        "FF0D40",
                    )
                    self._build_filter_legend_item(
                        "z",
                        "CC0DFF",
                    )
                    self._build_filter_legend_item(
                        "y",
                        "FFBF1A",
                    )

                with ui.HStack(height=36):
                    ui.Button(
                        "Create Current",
                        clicked_fn=self._create_current_footprint,
                    )
                    ui.Button(
                        "Clear Footprints",
                        clicked_fn=self._clear_footprints,
                    )

                ui.Spacer()

                self._status = ui.Label(
                    "Ready",
                    height=65,
                    word_wrap=True,
                )

        self._update_sub = (
            omni.kit.app.get_app()
            .get_update_event_stream()
            .create_subscription_to_pop(self._on_update)
        )

    def _build_filter_legend_item(
        self,
        filter_name,
        hex_color,
    ):
        with ui.HStack(width=100, height=22, spacing=5):
            ui.Rectangle(
                width=14,
                height=14,
                style={
                    "background_color": cl(hex_color),
                    "border_radius": 3,
                },
            )
            ui.Label(
                filter_name,
                width=18,
                height=20,
                style={"font_size": 15},
            )

    # ------------------------------------------------------------------
    # Stage helpers
    # ------------------------------------------------------------------

    def _get_stage(self):
        return omni.usd.get_context().get_stage()

    # ------------------------------------------------------------------
    # Load survey data
    # ------------------------------------------------------------------

    def _load_data(self):
        try:
            with open(
                VISIT_FILE,
                newline="",
                encoding="utf-8",
            ) as csvfile:
                reader = csv.DictReader(csvfile)
                self._visits = list(reader)

            if not self._visits:
                self._status.text = "No survey visits found."
                return

            self._motion_by_frame = {}

            with open(
                MOTION_FILE,
                newline="",
                encoding="utf-8",
            ) as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    frame = int(row["frame"])
                    footprint = int(row["footprint"])

                    if frame not in self._motion_by_frame:
                        self._motion_by_frame[frame] = {}

                    self._motion_by_frame[frame][footprint] = row

            self._visit_index = 0
            self._playing = False
            self._phase = "idle"

            self._show_visit()

            self._state_label.text = "Idle"

            motion_count = sum(
                len(v)
                for v in self._motion_by_frame.values()
            )

            self._status.text = (
                f"Loaded {len(self._visits)} visits and "
                f"{motion_count} footprint positions."
            )

            print(
                "[proctor.engineering.data] "
                f"Loaded {len(self._visits)} visits."
            )

            print(
                "[proctor.engineering.data] "
                f"Loaded {motion_count} footprint positions."
            )

        except Exception as exc:
            self._status.text = f"Load failed: {exc}"
            print(
                "[proctor.engineering.data] "
                f"Load failed: {exc}"
            )

    # ------------------------------------------------------------------
    # Telescope motion
    # ------------------------------------------------------------------

    def _set_rotation_axis(
        self,
        prim_path,
        axis,
        angle_degrees,
    ):
        stage = self._get_stage()

        if stage is None:
            return False

        prim = stage.GetPrimAtPath(prim_path)

        if not prim or not prim.IsValid():
            return False

        xformable = UsdGeom.Xformable(prim)

        rotate_op = None

        for op in xformable.GetOrderedXformOps():
            if op.GetOpType() == UsdGeom.XformOp.TypeRotateXYZ:
                rotate_op = op
                break

        if rotate_op is None:
            rotate_op = xformable.AddRotateXYZOp()

        current = rotate_op.Get()

        if current is None:
            current = Gf.Vec3f(0.0, 0.0, 0.0)

        x, y, z = current

        if axis == "X":
            x = angle_degrees
        elif axis == "Y":
            y = angle_degrees
        elif axis == "Z":
            z = angle_degrees

        rotate_op.Set(Gf.Vec3f(x, y, z))
        return True

    def _set_telescope_pointing(
        self,
        azimuth,
        elevation,
    ):
        az_ok = self._set_rotation_axis(
            AZIMUTH_PATH,
            "Z",
            azimuth,
        )

        # Imported Rubin model:
        # elevation 90 degrees = model X rotation 0
        # elevation 0 degrees  = model X rotation -90
        el_ok = self._set_rotation_axis(
            ELEVATION_PATH,
            "X",
            elevation - 90.0,
        )

        return az_ok and el_ok

    def _lmst_to_sidereal_y(self, lmst_hours):
        # Local Mean Sidereal Time advances 15 degrees per sidereal hour.
        # Use the shortest wrapped difference so a 24h -> 0h LMST wrap
        # does not produce an unnecessary 360-degree jump.
        delta_hours = (
            (lmst_hours - SIDEREAL_REFERENCE_LMST_HOURS + 12.0)
            % 24.0
        ) - 12.0

        delta_deg = delta_hours * 15.0

        return (
            SIDEREAL_REFERENCE_Y_DEG
            + SIDEREAL_DIRECTION * delta_deg
        )

    def _set_sidereal_rotation(self, lmst_hours):
        y_rotation = self._lmst_to_sidereal_y(
            lmst_hours
        )

        return self._set_rotation_axis(
            SIDEREAL_ROTATION_PATH,
            "Y",
            y_rotation,
        )

    # ------------------------------------------------------------------
    # Visit display
    # ------------------------------------------------------------------

    def _show_visit(self):
        if not self._visits:
            return

        visit = self._visits[self._visit_index]

        azimuth = float(visit["az_deg"])
        elevation = float(visit["alt_deg"])
        lmst_hours = float(visit["lmst"])

        self._set_telescope_pointing(
            azimuth,
            elevation,
        )

        self._set_sidereal_rotation(
            lmst_hours
        )

        self._visit_label.text = (
            f"{self._visit_index + 1} / "
            f"{len(self._visits)}"
        )

        self._az_label.text = f"{azimuth:.2f}°"
        self._el_label.text = f"{elevation:.2f}°"
        self._ra_label.text = f"{float(visit['RA_deg']):.2f}°"
        self._dec_label.text = f"{float(visit['dec_deg']):.2f}°"
        self._filter_label.text = visit["filter"]
        self._slew_label.text = f"{float(visit['slewtime']):.2f} s"
        self._exposure_label.text = f"{float(visit['exptime']):.1f} s"

        # Move all existing footprints to where they belong
        # at this observing time.
        self._update_footprints_for_frame(
            self._visit_index
        )
        
    # ------------------------------------------------------------------
    # Manual visit navigation
    # ------------------------------------------------------------------

    def _previous_visit(self):
        self._pause()

        if not self._visits:
            self._status.text = "Load a survey sequence first."
            return

        self._visit_index = max(
            0,
            self._visit_index - 1,
        )

        self._show_visit()

    def _next_visit(self):
        self._pause()

        if not self._visits:
            self._status.text = "Load a survey sequence first."
            return

        self._visit_index = min(
            len(self._visits) - 1,
            self._visit_index + 1,
        )

        self._show_visit()

    # ------------------------------------------------------------------
    # Playback controls
    # ------------------------------------------------------------------

    def _set_speed(self, speed):
        self._playback_speed = speed
        self._speed_label.text = f"{speed:g}x"

    def _play(self):
        if not self._visits:
            self._status.text = "Load a survey sequence first."
            return

        if self._visit_index >= len(self._visits) - 1:
            self._visit_index = 0
            self._show_visit()

        self._playing = True

        if self._phase == "idle":
            self._begin_slew()

    def _pause(self):
        self._playing = False
        self._phase = "idle"
        self._state_label.text = "Paused"

    # ------------------------------------------------------------------
    # Playback state machine
    # ------------------------------------------------------------------

    def _begin_slew(self):
        if self._visit_index >= len(self._visits) - 1:
            self._playing = False
            self._phase = "idle"
            self._state_label.text = "Complete"
            self._status.text = "Survey sequence complete."
            return

        current_visit = self._visits[self._visit_index]
        next_visit = self._visits[self._visit_index + 1]

        self._start_az = float(current_visit["az_deg"])
        self._start_el = float(current_visit["alt_deg"])
        self._target_az = float(next_visit["az_deg"])
        self._target_el = float(next_visit["alt_deg"])

        real_slew = float(next_visit["slewtime"])

        self._phase_duration = max(
            0.05,
            real_slew / self._playback_speed,
        )

        self._phase_start_time = time.monotonic()
        self._phase = "slew"

        self._state_label.text = "Slewing"

        self._status.text = (
            f"Real slew: {real_slew:.2f} s | "
            f"Playback: {self._playback_speed:g}x | "
            f"Display: {self._phase_duration:.2f} s"
        )

    def _begin_exposure(self):
        # The telescope has arrived at this visit.
        # Stamp its footprint onto the sky.
        self._create_footprint(
            self._visit_index
        )

        # Move every previously created footprint
        # to its proper location at this time.
        self._update_footprints_for_frame(
            self._visit_index
        )

        visit = self._visits[self._visit_index]
        real_visit = float(visit["visittime"])

        self._phase_duration = max(
            0.05,
            real_visit / self._playback_speed,
        )

        self._phase_start_time = time.monotonic()
        self._phase = "exposure"

        self._state_label.text = "Exposing"

        self._status.text = (
            f"Exposure/visit: {real_visit:.2f} s | "
            f"Playback: {self._playback_speed:g}x | "
            f"Display: {self._phase_duration:.2f} s"
        )

    def _shortest_angle_delta(
        self,
        start_deg,
        end_deg,
    ):
        return (
            (end_deg - start_deg + 180.0) % 360.0
        ) - 180.0

    def _smoothstep(self, t):
        t = max(0.0, min(1.0, t))
        return t * t * (3.0 - 2.0 * t)

    def _on_update(self, _event):
        if not self._playing:
            return

        now = time.monotonic()

        if self._phase == "slew":
            elapsed = now - self._phase_start_time
            t = elapsed / self._phase_duration

            if t >= 1.0:
                self._visit_index += 1
                self._show_visit()
                self._begin_exposure()
                return

            s = self._smoothstep(t)

            az_delta = self._shortest_angle_delta(
                self._start_az,
                self._target_az,
            )

            azimuth = self._start_az + az_delta * s

            elevation = (
                self._start_el
                + (self._target_el - self._start_el) * s
            )

            self._set_telescope_pointing(
                azimuth,
                elevation,
            )

        elif self._phase == "exposure":
            elapsed = now - self._phase_start_time

            if elapsed >= self._phase_duration:
                self._begin_slew()

    # ------------------------------------------------------------------
    # Coordinate conversion
    # ------------------------------------------------------------------

    def _altaz_to_position(
        self,
        alt_deg,
        az_deg,
        radius,
    ):
        alt = math.radians(alt_deg)
        az = math.radians(az_deg)

        horizontal = radius * math.cos(alt)

        # Scene convention established by calibration:
        # +Y = North
        # -X = East
        # +Z = Up
        x = -horizontal * math.sin(az)
        y = horizontal * math.cos(az)
        z = radius * math.sin(alt)

        return Gf.Vec3d(x, y, z)

    # ------------------------------------------------------------------
    # Footprint system
    # ------------------------------------------------------------------

    def _ensure_footprint_root(self):
        stage = self._get_stage()

        if stage is None:
            return None

        prim = stage.GetPrimAtPath(
            FOOTPRINT_ROOT
        )

        if not prim or not prim.IsValid():
            UsdGeom.Xform.Define(
                stage,
                FOOTPRINT_ROOT,
            )

        return stage.GetPrimAtPath(
            FOOTPRINT_ROOT
        )

    def _normalize_filter_name(self, filter_name):
        filter_key = str(filter_name).strip().lower()

        if filter_key in FILTER_COLORS:
            return filter_key

        if filter_key:
            first_character = filter_key[0]
            if first_character in FILTER_COLORS:
                return first_character

        return "default"

    def _get_marker_size_for_filter(self, filter_name):
        filter_key = self._normalize_filter_name(filter_name)
        return FILTER_MARKER_SIZES.get(
            filter_key,
            FILTER_MARKER_SIZES["default"],
        )

    def _get_display_color_for_filter(self, filter_name):
        filter_key = self._normalize_filter_name(filter_name)
        return FILTER_COLORS.get(
            filter_key,
            FILTER_COLORS["default"],
        )

    def _get_footprint_sky_radius(self, footprint_index):
        # A tiny depth bias keeps exact revisits from producing
        # coincident-surface artifacts while preserving sky alignment.
        return (
            FOOTPRINT_RADIUS
            + footprint_index * FOOTPRINT_DEPTH_STEP
        )

    def _create_footprint(
        self,
        footprint_index,
    ):
        if not self._visits:
            return

        stage = self._get_stage()

        if stage is None:
            return

        self._ensure_footprint_root()

        path = (
            f"{FOOTPRINT_ROOT}/"
            f"Visit_{footprint_index:03d}"
        )

        prim = stage.GetPrimAtPath(path)

        if prim and prim.IsValid():
            return

        visit = self._visits[
            footprint_index
        ]

        filter_name = visit["filter"]
        filter_key = self._normalize_filter_name(
            filter_name
        )

        marker = UsdGeom.Sphere.Define(
            stage,
            path,
        )

        marker_size = self._get_marker_size_for_filter(
            filter_name
        )

        marker.CreateRadiusAttr(
            marker_size
        )

        material = self._get_footprint_material(
            filter_name
        )

        if material:
            UsdShade.MaterialBindingAPI(
                marker.GetPrim()
            ).Bind(material)

        # Store useful Rubin metadata directly on the USD prim.
        marker.GetPrim().CreateAttribute(
            "rubin:visitID",
            Sdf.ValueTypeNames.Int,
        ).Set(
            int(visit["ID"])
        )

        marker.GetPrim().CreateAttribute(
            "rubin:filter",
            Sdf.ValueTypeNames.String,
        ).Set(
            filter_name
        )

        marker.GetPrim().CreateAttribute(
            "rubin:RA_deg",
            Sdf.ValueTypeNames.Double,
        ).Set(
            float(visit["RA_deg"])
        )

        marker.GetPrim().CreateAttribute(
            "rubin:Dec_deg",
            Sdf.ValueTypeNames.Double,
        ).Set(
            float(visit["dec_deg"])
        )

        marker.GetPrim().CreateAttribute(
            "rubin:markerRadius",
            Sdf.ValueTypeNames.Double,
        ).Set(
            marker_size
        )

        marker.GetPrim().CreateAttribute(
            "rubin:filterKey",
            Sdf.ValueTypeNames.String,
        ).Set(
            filter_key
        )

        display_color = self._get_display_color_for_filter(
            filter_name
        )

        marker.CreateDisplayColorPrimvar(
            UsdGeom.Tokens.constant
        ).Set(
            [display_color]
        )

    def _get_footprint_material(
        self,
        filter_name,
    ):
        stage = self._get_stage()

        if stage is None:
            return None

        filter_key = self._normalize_filter_name(
            filter_name
        )

        color = FILTER_COLORS.get(
            filter_key,
            FILTER_COLORS["default"],
        )

        material_path = (
            "/Rubin_Telescope/_materials/"
            f"FootprintGlow_{filter_key}"
        )
        shader_path = f"{material_path}/Shader"

        material = UsdShade.Material.Get(
            stage,
            material_path,
        )

        if not material:
            material = UsdShade.Material.Define(
                stage,
                material_path,
            )

            shader = UsdShade.Shader.Define(
                stage,
                shader_path,
            )

            shader.CreateIdAttr(
                "UsdPreviewSurface"
            )

            shader.CreateInput(
                "diffuseColor",
                Sdf.ValueTypeNames.Color3f,
            ).Set(
                color
            )

            shader.CreateInput(
                "emissiveColor",
                Sdf.ValueTypeNames.Color3f,
            ).Set(
                color
            )

            shader.CreateInput(
                "roughness",
                Sdf.ValueTypeNames.Float,
            ).Set(
                1.0
            )

            shader.CreateInput(
                "opacity",
                Sdf.ValueTypeNames.Float,
            ).Set(
                0.20
            )

            shader.CreateInput(
                "opacityThreshold",
                Sdf.ValueTypeNames.Float,
            ).Set(
                0.0
            )

            material.CreateSurfaceOutput().ConnectToSource(
                shader.ConnectableAPI(),
                "surface",
            )

        return material


    def _update_footprints_for_frame(
        self,
        frame_index,
    ):
        stage = self._get_stage()

        if stage is None:
            return

        frame_data = self._motion_by_frame.get(
            frame_index
        )

        if not frame_data:
            return

        for (
            footprint_index,
            row,
        ) in frame_data.items():

            path = (
                f"{FOOTPRINT_ROOT}/"
                f"Visit_{footprint_index:03d}"
            )

            prim = stage.GetPrimAtPath(path)

            # Footprints are created only when
            # their exposure occurs.
            if not prim or not prim.IsValid():
                continue

            alt_deg = float(
                row["alt_deg"]
            )

            az_deg = float(
                row["az_deg"]
            )

            position = self._altaz_to_position(
                alt_deg,
                az_deg,
                self._get_footprint_sky_radius(
                    footprint_index
                ),
            )

            xformable = UsdGeom.Xformable(
                prim
            )

            translate_op = None

            for op in xformable.GetOrderedXformOps():
                if (
                    op.GetOpType()
                    == UsdGeom.XformOp.TypeTranslate
                ):
                    translate_op = op
                    break

            if translate_op is None:
                translate_op = xformable.AddTranslateOp()

            translate_op.Set(
                position
            )

    def _create_current_footprint(self):
        if not self._visits:
            self._status.text = "Load a survey sequence first."
            return

        self._create_footprint(
            self._visit_index
        )

        self._update_footprints_for_frame(
            self._visit_index
        )

        self._status.text = (
            f"Created footprint for visit "
            f"{self._visit_index + 1}."
        )

    def _clear_footprints(self):
        stage = self._get_stage()

        if stage is None:
            return

        prim = stage.GetPrimAtPath(
            FOOTPRINT_ROOT
        )

        if prim and prim.IsValid():
            stage.RemovePrim(
                FOOTPRINT_ROOT
            )

        self._status.text = (
            "Cleared survey footprints."
        )

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------

    def on_shutdown(self):
        print(
            "[proctor.engineering.data] "
            "Extension shutdown"
        )

        self._playing = False
        self._update_sub = None
        self._window = None
