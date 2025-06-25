import os

from setuptools import find_packages, setup

with open("README.md") as readme_file:
    README = readme_file.read()

setup_args = {
    "name": "csutl",
    "version": os.environ["BUILD_VERSION"],
    "description": "CoinSpot Utility",
    "long_description_content_type": "text/markdown",
    "long_description": README,
    "license": "MIT",
    "packages": find_packages(where="src", include=["csutl", "csutl.*"]),
    "author": "Jesse Reichman",
    "keywords": ["CoinSpot", "Utility"],
    "url": "https://github.com/archmachina/csutl",
    "download_url": "https://pypi.org/project/csutl/",
    "entry_points": {"console_scripts": ["csutl = csutl.cli:main"]},
    "package_dir": {"": "src"},
    "install_requires": ["requests>=2.32.0"],
}

if __name__ == "__main__":
    setup(**setup_args, include_package_data=True)
