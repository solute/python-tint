# coding: utf-8

import pytest
import tint


@pytest.fixture
def tint_registry(request):
    return tint.TintRegistry()


def test_white(tint_registry):
    assert tint_registry.match_name("white") == ("ffffff", 100)


def test_weiss(tint_registry):
    hex_code, score = tint_registry.match_name("weiss")
    assert tint_registry.find_nearest(hex_code, "de").color_name == u"weiß"


def test_nearest_filter(tint_registry):
    hex_code, score = tint_registry.match_name("pearl")
    nearest_color, distance = tint_registry.find_nearest(
        hex_code,
        system="de",
        filter_set=(u"weiß", "schwarz")
    )
    assert nearest_color == u"weiß"


def test_nearest_filter_dict(tint_registry):
    hex_code, score = tint_registry.match_name("purple")
    nearest_color, distance = tint_registry.find_nearest(
        hex_code,
        filter_set={"ff0000": "red", "00ff00": "green"}
    )
    assert nearest_color == "red"


def test_nearest_de_en(tint_registry):
    hex_code, score = tint_registry.match_name(u"perlweiß")
    nearest_color, distance = tint_registry.find_nearest(
        hex_code,
        system="en",
        filter_set=("white", "black")
    )
    assert nearest_color == u"white"


def test_ral_de(tint_registry):
    hex_code, score = tint_registry.match_name("RAL 1000")
    nearest_color, distance = tint_registry.find_nearest(hex_code, system="de")
    assert nearest_color == u"grünbeige"


def test_exact_nearest(tint_registry):
    color_name = "pearl"
    hex_code, score = tint_registry.match_name(color_name)
    nearest_color, distance = tint_registry.find_nearest(hex_code, system="en")
    assert color_name == nearest_color


def test_parse_no_valid_color_name(tint_registry):
    assert tint_registry.match_name("not_a_valid_color").score < 100


def test_find_no_exact_hex(tint_registry):
    assert tint_registry.find_nearest("842456", "en").distance > 0


def test_find_exact_hex(tint_registry):
    hex_code, score = tint_registry.match_name("white")
    assert tint_registry.find_nearest(hex_code, "en").distance == 0
