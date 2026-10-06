#!/usr/bin/env python
import argparse
from oncoverse.real_data.pipeline import download_and_normalize

parser = argparse.ArgumentParser(description="Download and normalize OncoVerse Kaggle datasets")
parser.add_argument("dataset", choices=["wisconsin", "metabric"])
args = parser.parse_args()
print(download_and_normalize(args.dataset))
