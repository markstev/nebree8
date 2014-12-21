#!/usr/bin/env python

import random
import sys

import drinks.manual_db


# MUST MAP TO ORDER OF PHYSICAL VALVES
INGREDIENTS_ORDERED = (
    "angostura bitters",
    "lime juice",
    "lemon juice",
    "grenadine", # brown bottle dark liquid
    "agave syrup", # clear bottle amber liquid
    "simple syrup",
    "kahlua",
    "pimms",
    "triple sec",
    "tequila",
    "gin",
    "rum",
    "rye",
    "bourbon",
    "vodka",
)

