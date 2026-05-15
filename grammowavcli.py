#!/usr/bin/env python3
from pythonopenscad import Cube, Sphere, Cylinder, Translate, Union
from pythonopenscad.m3dapi import M3dRenderer
import argparse

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

args = argsparser.parse_args()

# --------------------------------------- parsing music file



# ---------------------------------------

model = Cylinder(
    h = args.height,
    r1 = args.diameter / 2,
    r2 = args.diameter / 2,
    center = True
)

model -= Cylinder( # hole
    h = args.height,
    r1 = args.hole_diameter / 2,
    r2 = args.hole_diameter / 2,
    center = True
)

model -= Translate([0, 0, (args.height / 2) - args.apple_height])(Cylinder( # apple
    h = args.apple_height,
    r1 = args.apple_diameter / 2,
    r2 = args.apple_diameter / 2
))

mesh = model.renderObj(M3dRenderer())
mesh.write_solid_stl(args.output)