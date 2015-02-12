tint - friendly color normalization
===================================

`tint` helps you getting a sRBG-value out of a color description string you happen
to stumble upon, as well as getting the best color name for any sRBG value you might
feed it with. Combined, these two functionalities enable you to narrow any color string
down to a well defined set of colors.

Install
-------

To install `tint`, use `pip` to download and install from `pypi`:

```bash
$ pip install tint
```

Quickstart
----------

```python
>>> import tint
>>> registry = tint.TintRegistry()
>>> registry.match_name("redish", fuzzy=True)
MatchResult(hex_code=u'ff0000', score=78)
>>> registry.find_nearest("ff1010", "en")
FindResult(color_name=u'red', distance=1.3001607954612469)
```

Full documentation is on [readthedocs](http://python-tint.readthedocs.org).


Contributing
------------

We will happily accept pull requests! Particularly, we welcome contributions to the color models – either expanding (or correcting) the current ones, or adding entirely new models. Make sure, however, that these color models are not protected by copyright claims or patents of any sort.

License
-------

`tint` is published under the GPL2 only license; see LICENSE.txt for the full text.

Copyright (c) 2014, Christian Schramm, solute GmbH
