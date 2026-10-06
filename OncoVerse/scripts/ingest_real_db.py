#!/usr/bin/env python
import argparse
from oncoverse.real_db import ingest_canonical_csv
p=argparse.ArgumentParser(); p.add_argument("csv"); a=p.parse_args(); print(ingest_canonical_csv(a.csv))
