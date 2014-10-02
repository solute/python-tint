from setuptools import setup

setup(
    name='tint',
    version='0.1',
    description='Friendly Color Normalization',
    #url='http://github.com/...',
    author='Christian Schramm',
    author_email='csch@solute.de',
    #license='MIT',
    packages=['tint'],
    zip_safe=False,
    package_data={'tint': ['data/*.txt']},
    install_requires=[
        "pytest",
        "colormath",
        "numpy",
        "pyicu",
        "fuzzywuzzy",
        "sphinxcontrib-napoleon",
    ],
)

