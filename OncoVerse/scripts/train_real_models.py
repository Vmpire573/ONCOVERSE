#!/usr/bin/env python3
from pathlib import Path
import argparse, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from oncoverse.real_model import train_wisconsin, train_metabric_5y

p=argparse.ArgumentParser()
p.add_argument("--wisconsin")
p.add_argument("--metabric")
a=p.parse_args()
if a.wisconsin: print(train_wisconsin(a.wisconsin))
if a.metabric: print(train_metabric_5y(a.metabric))
if not a.wisconsin and not a.metabric: p.error("Provide --wisconsin and/or --metabric")
