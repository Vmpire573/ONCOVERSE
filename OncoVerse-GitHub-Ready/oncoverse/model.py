"""Deprecated compatibility module.

The old synthetic classifier has been removed from the active application. Use
`oncoverse.real_model.train_wisconsin` or `train_metabric_5y` instead.
"""
from .real_model import train_wisconsin, train_metabric_5y

def train_model(*args, **kwargs):
    raise RuntimeError("The synthetic demo model was removed. Use train_wisconsin() or train_metabric_5y().")
