#!/usr/bin/env python3
from pythonopenscad import Cube, Sphere
from pythonopenscad.m3dapi import M3dRenderer
import argparse

# --------------------------------------- parsing cli arguments

argsparser = argparse.ArgumentParser(
    prog="grammowavcli",
    description="converts a music file into a 3D model of a record for printing on a 3D printer and listening on a gramophone"
)

argsparser.add_argument("file")
argsparser.add_argument("-o", "--output", default="out.stl")
argsparser.add_argument("--diameter", type=int, default=120)
argsparser.add_argument("--rpm", type=int, default=78)

args = argsparser.parse_args()



# --------------------------------------- 

model = Cube([20,20,20]) - Sphere(r=12)

mesh = model.renderObj(M3dRenderer())
mesh.write_solid_stl("out.stl")