# coding: utf-8

import colors as _colors


def test_white():
    assert _colors.parse("white") == "ffffff"


def test_weiss():
    hex_code = _colors.parse("weiss")
    assert _colors.get_exact_name(hex_code, "de") == u"weiß"


def test_nearest_simple():
    hex_code = _colors.parse("pearl")
    assert _colors.get_nearest_name(hex_code, filter_set=(u"weiß", "schwarz")) == u"weiß"


def test_nearest_en_de():
    hex_code = _colors.parse("pearl")
    assert _colors.get_nearest_name(hex_code, system="de") == u"perlweiß"


def test_ral_de():
    hex_code = _colors.parse("RAL 1000")
    nearest_color = _colors.get_nearest_name(hex_code, system="de")
    exact_color = _colors.get_exact_name(hex_code, system="de")
    assert nearest_color == exact_color == u"grünbeige"


def test_exact_nearest():
    color_name = "pearl"
    hex_code = _colors.parse(color_name)
    nearest_color = _colors.get_nearest_name(hex_code, system="en")
    exact_color = _colors.get_exact_name(hex_code, system="en")
    assert color_name == nearest_color == exact_color

