#!/usr/bin/env python3
from pythonopenscad import Cube, Sphere
from pythonopenscad.m3dapi import M3dRenderer

model = Cube([20,20,20]) - Sphere(r=12)

mesh = model.renderObj(M3dRenderer())
mesh.write_solid_stl("out.stl")