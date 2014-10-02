# coding: utf-8

"""Match human readable color names to sRBG values (and vice versa).

`tint` was created to solve the problem of normalizing color strings of various
languages and systems to a well defined set of color names. In order to do that,
`tint` establishes a registry for color names and corresponding sRGB values. `tint`
is shipped with default color definitions for english ("en"), german ("de") and
RAL ("ral").

You may query that registry for a sRGB hex value by passing it a color name -- if
there's no exact match, a fuzzy match is applied.  Together with the hex value, a
matching score is returned: 100 is best (exact match), lower means worse.

Also, you may want to find the best name for a given sRGB value. Again, `tint` tries
to match exactly, and failing that, it will find a color name with the minimal
perceptual difference according to CIEDE2000. The color name and the color distance
are returned: A distance of 0 is best, higher means worse.

Examples:
  >>> import tint
  >>> tint_registry = tint.TintRegistry()
  >>> tint_registry.match_name("a darker greenish color")
  MatchResult(hex_code=u'013220', score=66)
  >>> tint_registry.find_nearest("013220", "en")
  FindResult(color_name=u'dark green', distance=0)
  >>> tint_registry.find_nearest("013220", "de")
  FindResult(color_name=u'moosgrün', distance=5.924604488762661)
  >>> tint_registry.find_nearest("013220", filter_set={"00ffff": "cyan", "ffff00": "yellow"})
  FindResult(color_name='cyan', distance=72.54986912349503)

"""

from __future__ import unicode_literals

import io
import os.path
import os
import collections
import sys

from pkg_resources import resource_listdir
from pkg_resources import resource_filename

from colormath import color_objects
from colormath import color_conversions
from colormath import color_diff

import icu

from fuzzywuzzy import process
from fuzzywuzzy import fuzz


MatchResult = collections.namedtuple("MatchResult", ("hex_code", "score"))
FindResult = collections.namedtuple("FindResult", ("color_name", "distance"))


def _hex_to_rgb(hex_code):
    return tuple(map(ord, hex_code.decode("hex")))


def _hex_to_lab(hex_code):
    rgb_values = _hex_to_rgb(hex_code)
    rgb_color = color_objects.sRGBColor(*rgb_values, is_upscaled=True)
    return color_conversions.convert_color(rgb_color, color_objects.LabColor)


def _read_colors(f):
    lines = (line.partition("#") for line in f if not line.startswith("#"))
    return [(part[0], part[2]) for part in lines]


_normalize = icu.Normalizer2.getInstance(
    None,
    "nfkc_cf",
    icu.UNormalizationMode2.COMPOSE
).normalize


class TintRegistry(object):
    """ A registry for color names and systems

    Args:
      load_defaults (bool, optional): Load default color systems provided
        by `tint`. Currently, that's "en", "de", and "ral". Defaults to True.

    """
    def __init__(self, load_defaults=True):
        self._colors_by_system_hex = {}
        self._colors_by_system_lab = {}
        self._hex_by_color = {}
        if load_defaults:
            for filename in resource_listdir("tint", "data"):
                base, ext = os.path.splitext(filename)
                if ext == ".txt":
                    self.add_colors(base, resource_filename("tint", "data/" + filename))

    def add_colors(self, system, colors_or_filename):
        """Add color definition to a given color system.

        You may pass either a file-like object or a filename string pointing to a
        color definition file. Each line in that input file should look like this::

            café au lait #a67b5b

        i.e. a color name (possibly with whitespace), and a hex code prefixed
        by `#` that will be interpreted as a sRGB value.

        If you provide a file-like object (i.e. one with a ``read()`` method), make
        sure you have opened it with the correct encoding.

        Alternatively, you may pass a mapping (e.g. ``{u"café au lait": "a67b5b", ...}``)
        or a sequence of tuples (e.g. ``[(u"café au lait", "a67b5b"), ...]``).
        The color name will be saved lower-cased and stripped. For matching purposes,
        a normalized version of the color name will be used (e.g. "weiß"->"weiss").

        Note that existing color definitions of the same (normalized) name will be
        overwritten.

        Args:
          system (string): The color system the colors should be added to
            (e.g. ``"en"``).
          colors_or_filename (sequence of tuples, dict, filename, or file-like object): Either
            a filename or a file-like object pointing to a color definition file,
            or an iterable of tuples (e.g.  ``[("white", "ffffff"), ("red", "ff0000")]``)
            or a dict (e.g.  ``{"white": "ffffff", "red": "ff0000"}``).

        Raises:
          TypeError: If argument `color_or_filename` is not of an accepted type.

        """
        if hasattr(colors_or_filename, "read"):
            colors = _read_colors(colors_or_filename)
        elif isinstance(colors_or_filename, (str, unicode)):
            with io.open(colors_or_filename, encoding="utf-8") as f:
                colors = _read_colors(f)
        elif isinstance(colors_or_filename, collections.Mapping):
            colors = colors_or_filename.items()
        elif isinstance(colors_or_filename, collections.Sequence):
            colors = colors_or_filename
        else:
            raise TypeError(
                "argument 'colors_or_filename' must be a file-like object, "
                "a filename string, a mapping or a sequence of tuples"
            )

        if system not in self._colors_by_system_hex:
            self._colors_by_system_hex[system] = {}
            self._colors_by_system_lab[system] = {}

        for color_name, hex_code in colors:
            color_name = color_name.lower().strip()
            hex_code = hex_code.lower().strip()
            lab_color = _hex_to_lab(hex_code)

            self._colors_by_system_hex[system][hex_code] = color_name
            self._colors_by_system_lab[system][lab_color] = color_name
            self._hex_by_color[_normalize(color_name)] = hex_code

    def match_name(self, in_string):
        """Match a color to a sRGB value.

        Args:
          in_string (string): The input string containing something resembling
            a color name.

        Returns:
          A named tuple with the members `hex_code`[0] and `score`[1].

        Examples:
          >>> tint_registry = tint.TintRegistry()
          >>> tint_registry.match_name("rather white")
          MatchResult(hex_code=u'ffffff', score=95)
          >>> tint_registry.match_name("qwertyuio")
          MatchResult(hex_code=u'343434', score=29)

        """
        in_string = _normalize(in_string)
        if in_string in self._hex_by_color:
            return MatchResult(self._hex_by_color[in_string], 100)

        # We want the standard scorer *plus* the set scorer, because colors are often
        # (but not always) related by sub-strings
        result_set_scorer = process.extract(
            in_string,
            self._hex_by_color.keys(),
            scorer=fuzz.token_set_ratio
        )
        result_standard_scorer = process.extract(in_string, self._hex_by_color.keys())
        counter = collections.Counter(dict(result_set_scorer))
        counter.update(collections.Counter(dict(result_standard_scorer)))
        color_name, score = counter.most_common(1)[0]
        return MatchResult(self._hex_by_color[color_name], score / 2)

    def find_nearest(self, hex_code, system=None, filter_set=None):
        """Find a color name that's most similar to a given sRGB hex code.

        Args:
          system (string, optional): The color system. Currently, ``"de"``, ``"en"`` and
            ``"ral"`` are the default systems. May be ommitted if `filter_set` is a
            mapping. Defaults to None.
          filter_set (dict or list of string, optional): Limits the output choices
            to fewer color names. If given a list of names (e.g. ``["black", "white"]``),
            these names must be presen in the given system. If it's a dict of hex
            values and color names (e.g. ``{"000000": "black", "ffffff": "white"}`` -
            notice the hex strings make up the keys, not the values of the dict), the
            argument `system` is ignored and may be ommitted.  If omitted, all color
            names of the system are considered. Defaults to None.

        Returns:
          A named tuple with the members `color_name` and `distance`.

        Raises:
          TypeError: If argument `system` is not passed and `filter_set` is not a mapping.

        Examples:
          >>> tint_registry = tint.TintRegistry()
          >>> tint_registry.find_nearest("54e6e4", system="en")
          FindResult(color_name=u'bright turquoise', distance=3.730288645055483)
          >>> tint_registry.find_nearest("54e6e4", "en", filter_set=("white", "black"))
          FindResult(color_name=u'white', distance=25.709952192116894)

        """

        filter_set_is_mapping = isinstance(filter_set, collections.Mapping)
        if system is None and not filter_set_is_mapping:
            raise TypeError(
                "find_nearest() needs argument 'system' if 'filter_set' is not a Mapping"
            )

        hex_code = hex_code.lower().strip()
        # Try direkt hit
        if filter_set_is_mapping:
            if hex_code in filter_set:
                return filter_set[hex_code]

        elif hex_code in self._colors_by_system_hex[system]:
            color_name = self._colors_by_system_hex[system][hex_code]
            if filter_set is None or color_name in set(filter_set):
                return FindResult(color_name, 0)

        # No direkt hit
        lab_color = _hex_to_lab(hex_code)
        if filter_set_is_mapping:
            colors = {}
            for hex_code, color_name in filter_set.items():
                colors[_hex_to_lab(hex_code)] = color_name
        else:
            colors = self._colors_by_system_lab[system]
            if filter_set is not None:
                filter_set = set(filter_set)
                colors = dict(pair for pair in colors.items() if pair[1] in filter_set)

        min_distance = sys.float_info.max
        min_color = None
        for current_lab_color, current_color_name in colors.items():
            current_lab_color = current_lab_color
            distance = color_diff.delta_e_cie2000(lab_color, current_lab_color)
            if distance < min_distance:
                min_distance = distance
                min_color = current_color_name

        return FindResult(min_color, min_distance)
