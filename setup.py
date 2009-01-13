args = {
    'name': 'lambdooz',
    'version': '0.0.0',
    'description': 'lambdooz',
    'packages': ['lambdooz'],
    'scripts': ['bin/lambdooz'],
}

setuptools_args = {
    'install_requires': ['decorator', 'pygame'],
}

try:
    from setuptools import setup
    args.update(setuptools_args)
except ImportError:
    from distutils.core import setup

setup(**args)
