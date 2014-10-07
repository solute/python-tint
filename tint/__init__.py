# coding: utf-8

"""Match human readable color names to sRBG values (and vice versa).

`tint` was created to solve the problem of normalizing color strings of
various languages and systems to a well defined set of color names. In order
to do that, `tint` establishes a registry for color names and corresponding
sRGB values. `tint` ships with default color definitions for english ("en"),
german ("de") and RAL ("ral").

You may query the aforementioned registry for a sRGB hex value by passing it a
color name -- if there's no exact match, a fuzzy match is applied.  Together
with the hex value, a matching score is returned: 100 is best (exact match),
lower means worse.

Also, you may want to find the best name for a given sRGB value. Again, `tint`
tries to match exactly, and failing that, it will find a color name with the
minimal perceptual difference according to CIEDE2000. The color name and the
color distance are returned: A distance of 0 is best, higher means worse.

Examples:
  >>> import tint
  >>> tint_registry = tint.TintRegistry()
  >>> tint_registry.match_name("a darker greenish color")
  MatchResult(hex_code=u'013220', score=66)
  >>> tint_registry.find_nearest("013220", "en")
  FindResult(color_name=u'dark green', distance=0)
  >>> tint_registry.find_nearest("013220", "de")
  FindResult(color_name=u'moosgrün', distance=5.924604488762661)
  >>> tint_registry.add_colors("limited", [("cyan", "00ffff"), ("yellow", "ffff00)])
  >>> tint_registry.find_nearest("013220", system="limited")
  FindResult(color_name=u'cyan', distance=72.54986912349503)

"""

from .tint import TintRegistry
