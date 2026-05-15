#!/usr/bin/env python3
from pythonopenscad import Cube, Sphere, Cylinder, Translate, Union, POSC_GLOBALS
from pythonopenscad.m3dapi import M3dRenderer
import argparse
import av
import numpy as np
import subprocess
import math

def map(x, a1, a2, b1, b2):
    return b1 + (x - a1) * (b2 - b1) / (a2 - a1)

# --------------------------------------- parsing cli arguments

argsparser = argparse.ArgumentParser(
    prog="grammowavcli",
    description="converts a music file into a 3D model of a record for printing on a 3D printer and listening on a gramophone"
)

argsparser.add_argument("input")
argsparser.add_argument("-o", "--output", default="out.stl")

argsparser.add_argument("--diameter", type=float, default=120)
argsparser.add_argument("--height", type=float, default=3)

argsparser.add_argument("--hole-diameter", type=float, default=5)
argsparser.add_argument("--apple-diameter", type=float, default=50)
argsparser.add_argument("--apple-height", type=float, default=0.5)
argsparser.add_argument("--track-border-offset", type=float, default=3)

argsparser.add_argument("--rpm", type=float, default=78.26)
argsparser.add_argument("--sample-rate", type=int, default=16000)
argsparser.add_argument("--silence-start-seconds", type=float, default=1)
argsparser.add_argument("--silence-end-seconds", type=float, default=1)

argsparser.add_argument("--track-height", type=float, default=0.15)
argsparser.add_argument("--track-width", type=float, default=0.08)
argsparser.add_argument("--track-width-bottom", type=float, default=0.01)
argsparser.add_argument("--track-amplitude", type=float, default=0.1)

args = argsparser.parse_args()

# --------------------------------------- load sound

def load_audio(path, sr=44100):
    container = av.open(path)

    resampler = av.audio.resampler.AudioResampler(
        format="flt",
        layout="mono",
        rate=sr
    )

    out = []

    for frame in container.decode(audio=0):
        frames = resampler.resample(frame)

        if not frames:
            continue

        if not isinstance(frames, list):
            frames = [frames]

        for f in frames:
            arr = f.to_ndarray().reshape(-1)
            out.append(arr)

    if not out:
        return np.array([], dtype=np.float32)

    return np.concatenate(out)

silence_start = np.zeros(int(args.silence_start_seconds * args.sample_rate), dtype=np.float32)
silence_end = np.zeros(int(args.silence_end_seconds * args.sample_rate), dtype=np.float32)
audio = load_audio(args.input, args.sample_rate)

input_sound = np.concatenate([
    silence_start,
    audio,
    silence_end
])

input_sound_len = len(input_sound)

# ---------------------------------------

disk_radius = args.diameter / 2
apple_radius = args.apple_diameter / 2

model = Cylinder(
    h = args.height,
    r1 = disk_radius,
    r2 = disk_radius
)

model -= Cylinder( # hole
    h = args.height,
    r1 = args.hole_diameter / 2,
    r2 = args.hole_diameter / 2
)

model -= Translate([0, 0, args.height - args.apple_height])(Cylinder( # apple
    h = args.apple_height,
    r1 = apple_radius,
    r2 = apple_radius
))

# --------------------------------------- write audio

cutter = Cylinder(
    h = args.track_height,
    r1 = args.track_width_bottom / 2,
    r2 = args.track_width / 2
)

cutter_offset_z = args.height - args.track_height

track_start_offset = disk_radius - args.track_border_offset
track_end_offset = apple_radius + args.track_border_offset

cut_mask = []

for i, sample in enumerate(input_sound):
    timeline = i / args.sample_rate

    angle = math.radians(timeline * args.rpm)
    offset = map(i, 0, input_sound_len, track_start_offset, track_end_offset)
    sample_offset = offset + (sample * args.track_amplitude)

    offset_x = math.sin(angle) * sample_offset
    offset_y = math.cos(angle) * sample_offset

    cut_mask.append(Translate([offset_x, offset_y, cutter_offset_z])(cutter))

model = model - Union()(*cut_mask)

# --------------------------------------- save stl

mesh = model.renderObj(M3dRenderer())
mesh.write_solid_stl(args.output)