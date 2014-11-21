from setuptools import setup

setup(
    name="tint",
    version="0.2",
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
    install_requires=[
        "colormath",
        "numpy",
        "pyicu",
        "fuzzywuzzy",
        "sphinxcontrib-napoleon",
        "python-Levenshtein",
    ],
    tests_require=[
        "pytest",
    ],
)

