# coding: utf-8

import io as _io
from os.path import splitext as _splitext
from os.path import dirname as _dirname
import os as _os
import re as _re
import collections as _collections
import sys as _sys

from colormath import color_objects as _color_objects
from colormath import color_conversions as _color_conversions
from colormath import color_diff as _color_diff

import icu as _icu


def _str_normalize(in_string):
    return in_string.replace(u"ß", u"ss")


def _hex_to_rgb(hex_code):
    return tuple(ord(c) for c in hex_code.decode("hex"))


def parse(in_string):
    in_string = _normalize(in_string.lower().strip())
    if in_string in _hex_by_color:
        # We're done
        return _hex_by_color[in_string]

    results = _collections.Counter()
    for color_name, hex_code in _hex_by_color.items():
        for token in _re.findall(r"[\w']+", in_string):
            if color_name.find(token) != -1:
                results[hex_code] += 1

    if results:
        return results.most_common(1)[0][0]

    #TODO: better handle non-exact matches


def get_exact_name(hex_code, system="de"):
    return _colors_by_system_hex[system][hex_code]


def get_nearest_name(hex_code, system="de", filter_set=None):
    lab_color = _lab_by_hex[hex_code]
    colors = _colors_by_system_hex[system]
    if filter_set is not None:
        filter_set = set(filter_set)
        colors = dict(pair for pair in colors.items() if pair[1] in filter_set)

    min_distance = _sys.float_info.max
    min_color = ""
    for current_hex_code, current_color_name in colors.items():
        current_lab_color = _lab_by_hex[current_hex_code]
        diff = _color_diff.delta_e_cie2000(lab_color, current_lab_color)
        if diff < min_distance:
            min_distance = diff
            min_color = current_color_name
    return min_color


_normalize = _icu.Normalizer2.getInstance(
    None,
    "nfkc_cf",
    _icu.UNormalizationMode2.COMPOSE
).normalize


_colors_by_system_hex = {}
_hex_by_color = {}
_lab_by_hex = {}
for filename in _os.listdir(_dirname(__file__) or "."):
    base, ext = _splitext(filename)
    base = base.lower()
    if ext != ".txt":
        continue

    with _io.open(filename, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                break

            color_name, sep, hex_code = line.partition("#")
            color_name = color_name.lower().strip()
            hex_code = hex_code.lower().strip()

            if base not in _colors_by_system_hex:
                _colors_by_system_hex[base] = {hex_code: color_name}
            else:
                _colors_by_system_hex[base][hex_code] = color_name

            norm_color_name = _normalize(color_name)

            _hex_by_color[norm_color_name] = hex_code
            rgb_values = _hex_to_rgb(hex_code)
            rgb_color = _color_objects.sRGBColor(*rgb_values, is_upscaled=True)
            lab_color = _color_conversions.convert_color(rgb_color, _color_objects.LabColor)
            _lab_by_hex[hex_code] = lab_color

