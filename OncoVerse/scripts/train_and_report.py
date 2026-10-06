#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from oncoverse.real_model import train_wisconsin, train_metabric_5y
from oncoverse.real_survival import run_metabric_survival

wis=ROOT/'data/raw/wisconsin/breast_cancer_wisconsin_diagnostic.csv'
met=ROOT/'data/raw/metabric/Breast Cancer METABRIC.csv'
print(train_wisconsin(str(wis)))
print(train_metabric_5y(str(met)))
print(run_metabric_survival(str(met))['metrics'])
