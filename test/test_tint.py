# coding: utf-8

import pytest
import tint
import cStringIO as StringIO

GREENISH = "348954"
REDISH = "983431"

VAGUE_CSV = """
greenish,%s
redish,%s
""" % (GREENISH, REDISH)


@pytest.fixture
def tint_registry(request):
    return tint.TintRegistry()


@pytest.fixture
def no_default_tint_registry(request):
    return tint.TintRegistry(load_defaults=False)


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


def test_add_color_definitions_from_list(no_default_tint_registry):
    no_default_tint_registry.add_colors("vague", [("greenish", GREENISH), ("redish", REDISH)])
    hex_code, score = no_default_tint_registry.match_name("green")
    nearest_color, distance = no_default_tint_registry.find_nearest(hex_code, system="vague")
    assert hex_code == GREENISH
    assert nearest_color == "greenish"


def test_add_color_definitions_from_csv(no_default_tint_registry):
    csv = StringIO.StringIO(VAGUE_CSV)
    no_default_tint_registry.add_colors_from_file("vague", csv)
    hex_code, score = no_default_tint_registry.match_name("green")
    nearest_color, distance = no_default_tint_registry.find_nearest(hex_code, system="vague")
    assert hex_code == GREENISH
    assert nearest_color == "greenish"


def test_find_no_system(no_default_tint_registry):
    with pytest.raises(ValueError):
        no_default_tint_registry.find_nearest("000000", "not_a_real_system")


if __name__ == '__main__':
    pytest.main()
