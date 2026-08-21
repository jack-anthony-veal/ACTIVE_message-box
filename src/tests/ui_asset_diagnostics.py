import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT = os.path.join(ROOT, "client")
if CLIENT not in sys.path:
    sys.path.insert(0, CLIENT)

from assets.registry import ASSETS, PLACEMENTS, REGIONS


def placement_valid(name, x, y, region_name):
    _, width, height = ASSETS[name]
    region_x, region_y, region_width, region_height = REGIONS[region_name]
    return (
        x >= region_x and y >= region_y
        and x + width <= region_x + region_width
        and y + height <= region_y + region_height
    )


print("{:<20} {:<28} {:>3} {:>3} {:>3} {:>3} {:<8} {}".format(
    "screen", "asset", "x", "y", "w", "h", "region", "valid"
))
for screen, name, x, y, region_name in PLACEMENTS:
    _, width, height = ASSETS[name]
    valid = "yes" if placement_valid(name, x, y, region_name) else "no"
    print("{:<20} {:<28} {:>3} {:>3} {:>3} {:>3} {:<8} {}".format(
        screen, name, x, y, width, height, region_name, valid
    ))
