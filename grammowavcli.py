#!/usr/bin/env python3
from pythonopenscad import Cube, Sphere, Cylinder, Translate, Union
from pythonopenscad.m3dapi import M3dRenderer
import argparse
import av
import numpy as np
import subprocess

# --------------------------------------- parsing cli arguments

argsparser = argparse.ArgumentParser(
    prog="grammowavcli",
    description="converts a music file into a 3D model of a record for printing on a 3D printer and listening on a gramophone"
)

argsparser.add_argument("input")
argsparser.add_argument("-o", "--output", default="out.stl")

argsparser.add_argument("--diameter", type=int, default=120)
argsparser.add_argument("--height", type=int, default=3)

argsparser.add_argument("--hole-diameter", type=int, default=5)
argsparser.add_argument("--apple-diameter", type=int, default=50)
argsparser.add_argument("--apple-height", type=int, default=0.5)

argsparser.add_argument("--rpm", type=int, default=78)
argsparser.add_argument("--sample-rate", type=int, default=16000)

args = argsparser.parse_args()

# --------------------------------------- parsing music file

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

input_sound = load_audio(args.input, args.sample_rate)

# ---------------------------------------

model = Cylinder(
    h = args.height,
    r1 = args.diameter / 2,
    r2 = args.diameter / 2
)

model -= Cylinder( # hole
    h = args.height,
    r1 = args.hole_diameter / 2,
    r2 = args.hole_diameter / 2
)

model -= Translate([0, 0, args.height - args.apple_height])(Cylinder( # apple
    h = args.apple_height,
    r1 = args.apple_diameter / 2,
    r2 = args.apple_diameter / 2
))

# --------------------------------------- write audio

for i, sample in enumerate(input_sound):
    print(i, sample)

# --------------------------------------- save stl

mesh = model.renderObj(M3dRenderer())
mesh.write_solid_stl(args.output)