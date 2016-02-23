import os

from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

setup(
	name='ple',
	version='0.0.1',
	description='PyGame Learning Environment',
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
	url='https://github.com/ntasfi/PyGame-Learning-Environment',
	author='Norman Tasfi',
	author_email='first letter of first name plus last at googles email service.',
	keywords='',
	license="MIT",
	packages=find_packages(),
	install_requires = [
		"pygame",
		"numpy"
	]
)