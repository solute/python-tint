# coding: utf-8

from __future__ import unicode_literals

import os
import collections
import sys
import csv
import operator

import pkg_resources

import colormath.color_diff
import colormath.color_objects
import colormath.color_conversions

import icu

import fuzzywuzzy.process
import fuzzywuzzy.fuzz

MatchResult = collections.namedtuple("MatchResult", ("hex_code", "score"))
FindResult = collections.namedtuple("FindResult", ("color_name", "distance"))


def _hex_to_rgb(hex_code):
    """
    >>> _hex_to_rgb("007fff")
    (0, 127, 255)
    """
    return tuple(map(ord, hex_code.decode("hex")))


def _hex_to_lab(hex_code):
    rgb_values = _hex_to_rgb(hex_code)
    rgb_color = colormath.color_objects.sRGBColor(*rgb_values, is_upscaled=True)
    return colormath.color_conversions.convert_color(rgb_color, colormath.color_objects.LabColor)


_normalize = icu.Normalizer2.getInstance(
    None,
    "nfkc_cf",
    icu.UNormalizationMode2.COMPOSE
).normalize


class TintRegistry(object):
    """A registry for color names, categorized by color systems.

    Args:
      load_defaults (bool, optional): Load default color systems provided
        by `tint`. Currently, that's "en", "de", and "ral". Defaults to True.

    """
    def __init__(self, load_defaults=True):
        self._colors_by_system_hex = {}
        self._colors_by_system_lab = {}
        self._hex_by_color = {}
        if load_defaults:
            for filename in pkg_resources.resource_listdir("tint", "data"):
                base, ext = os.path.splitext(filename)
                if ext == ".csv":
                    # Yes, it's correct to join this with "/" because docs say so
                    # (it's no real path name)
                    self.add_colors_from_file(
                        base,
                        pkg_resources.resource_stream("tint", "data/" + filename)
                    )

    def add_colors_from_file(self, system, f_or_filename):
        """Add color definition to a given color system.

        You may pass either a file-like object or a filename string pointing
        to a color definition csv file. Each line in that input file should
        look like this::

            café au lait,a67b5b

        i.e. a color name and a sRGB hex code, separated by by comma (``,``). Note that
        this is standard excel-style csv format without headers.

        You may add to already existing color system. Previously existing color
        definitions of the same (normalized) name will be overwritten,
        regardless of the color system.

        Args:
          system (string): The color system the colors should be added to
            (e.g. ``"en"``).
          color_definitions (filename, or file-like object): Either
            a filename, or a file-like object pointing to a color definition
            csv file (excel style).

        """
        if hasattr(f_or_filename, "read"):
            colors = (row for row in csv.reader(f_or_filename) if row)
        else:
            with open(f_or_filename, "rb") as f:
                colors = [row for row in csv.reader(f) if row]

        self.add_colors(system, colors)

    def add_colors(self, system, colors):
        """Add color definition to a given color system.

        You may add to already existing color system. Previously existing color
        definitions of the same (normalized) name will be overwritten,
        regardless of the color system.

        Args:
          system (string): The color system the colors should be added to
            (e.g. ``"en"``).
          color_definitions (iterable of tuples): Color name / sRGB value pairs
            (e.g.  ``[("white", "ffffff"), ("red", "ff0000")]``)

        Examples:
          >>> color_definitions = {"greenish": "336633", "blueish": "334466"}
          >>> tint_registry = TintRegistry()
          >>> tint_registry.add_colors("vague", color_definitions.iteritems())

        """

        if system not in self._colors_by_system_hex:
            self._colors_by_system_hex[system] = {}
            self._colors_by_system_lab[system] = []

        for color_name, hex_code in colors:
            hex_code = hex_code.lower().strip().strip("#")
            color_name = color_name.lower().strip()
            if not isinstance(color_name, unicode):
                color_name = unicode(color_name, "utf-8")

            self._colors_by_system_hex[system][hex_code] = color_name
            self._colors_by_system_lab[system].append((_hex_to_lab(hex_code), color_name))
            self._hex_by_color[_normalize(color_name)] = hex_code

    def match_name(self, in_string):
        """Match a color to a sRGB value.

        The matching will be based purely on the input string and the color names in the
        registry. If there's no direct hit, a fuzzy matching algorithm is applied. This method
        will never fail to return a sRGB value, but depending on the score, it might or might
        not be a sensible result – as a rule of thumb, any score less then 90 indicates that
        there's a lot of guessing going on. It's the callers responsibility to judge if the return
        value should be trusted.

        In normalization terms, this method implements "normalize an arbitrary color name
        to a sRGB value".

        Args:
          in_string (string): The input string containing something resembling
            a color name.

        Returns:
          A named tuple with the members `hex_code` and `score`.

        Examples:
          >>> tint_registry = TintRegistry()
          >>> tint_registry.match_name("rather white")
          MatchResult(hex_code=u'ffffff', score=95)

        """
        in_string = _normalize(in_string)
        if in_string in self._hex_by_color:
            return MatchResult(self._hex_by_color[in_string], 100)

        # We want the standard scorer *plus* the set scorer, because colors are often
        # (but not always) related by sub-strings
        color_names = self._hex_by_color.keys()
        set_match = dict(fuzzywuzzy.process.extract(
            in_string,
            color_names,
            scorer=fuzzywuzzy.fuzz.token_set_ratio
        ))
        standard_match = dict(fuzzywuzzy.process.extract(in_string, color_names))

        # This would be much easier with a collections.Counter, but alas! it's a 2.7 feature.
        key_union = set(set_match) | set(standard_match)
        counter = ((n, set_match.get(n, 0) + standard_match.get(n, 0)) for n in key_union)
        color_name, score = sorted(counter, key=operator.itemgetter(1))[-1]

        return MatchResult(self._hex_by_color[color_name], score / 2)

    def find_nearest(self, hex_code, system, filter_set=None):
        """Find a color name that's most similar to a given sRGB hex code.

        In normalization terms, this method implements "normalize an arbitrary sRGB value
        to a well-defined color name".

        Args:
          system (string): The color system. Currently, ``"de"``, ``"en"`` and
            ``"ral"`` are the default systems.
          filter_set (iterable of string, optional): Limits the output choices
            to fewer color names. The names (e.g. ``["black", "white"]``) must be
            present in the given system.
            If omitted, all color names of the system are considered. Defaults to None.

        Returns:
          A named tuple with the members `color_name` and `distance`.

        Raises:
          ValueError: If argument `system` is not a registered color system.

        Examples:
          >>> tint_registry = TintRegistry()
          >>> tint_registry.find_nearest("54e6e4", system="en")
          FindResult(color_name=u'bright turquoise', distance=3.730288645055483)
          >>> tint_registry.find_nearest("54e6e4", "en", filter_set=("white", "black"))
          FindResult(color_name=u'white', distance=25.709952192116894)

        """

        if system not in self._colors_by_system_hex:
            raise ValueError(
                "%r is not a registered color system. Try one of %r"
                % (system, self._colors_by_system_hex.keys())
            )
        hex_code = hex_code.lower().strip()

        # Try direct hit (fast path)
        if hex_code in self._colors_by_system_hex[system]:
            color_name = self._colors_by_system_hex[system][hex_code]
            if filter_set is None or color_name in filter_set:
                return FindResult(color_name, 0)

        # No direct hit, assemble list of lab_color/color_name pairs
        colors = self._colors_by_system_lab[system]
        if filter_set is not None:
            colors = (pair for pair in colors if pair[1] in set(filter_set))

        # find minimal distance
        lab_color = _hex_to_lab(hex_code)
        min_distance = sys.float_info.max
        min_color_name = None
        for current_lab_color, current_color_name in colors:
            distance = colormath.color_diff.delta_e_cie2000(lab_color, current_lab_color)
            if distance < min_distance:
                min_distance = distance
                min_color_name = current_color_name

        return FindResult(min_color_name, min_distance)
