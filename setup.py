from setuptools import setup

setup(
    name="tint",
    version=0.2,
    description="Friendly Color Normalization",
    #url="http://github.com/...",
    author="Christian Schramm",
    author_email="csch@solute.de",
    license="MIT",
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

