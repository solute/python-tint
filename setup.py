from setuptools import setup

import os
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:
    install_requires = [
        "colormath",
        "numpy",
        "pyicu",
        "fuzzywuzzy",
        "sphinxcontrib-napoleon",
        "python-Levenshtein",
        # Remove this if colormath bug #51 is resolved
        "networkx",
    ]
else:
    install_requires = [
        "sphinxcontrib-napoleon",
        "mock",
    ]


setup(
    name="tint",
    version="0.4",
    description="Friendly Color Normalization",
    url="http://github.com/solute/python-tint",
    author="Christian Schramm",
    author_email="csch@solute.de",
    license="GPL2",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Topic :: Utilities",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    keywords=["color", "normalization", "fuzzy", "perceptual"],
    packages=["tint"],
    zip_safe=True,
    package_data={"tint": ["data/*"]},
    install_requires=install_requires,
    tests_require=[
        "pytest",
    ],
)

