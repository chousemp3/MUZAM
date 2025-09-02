#!/usr/bin/env python3
"""
Setup script for MUZAM - Open Source Audio Recognition Engine
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
with open("requirements.txt") as f:
    requirements = [
        line.strip() for line in f if line.strip() and not line.startswith("#")
    ]

setup(
    name="muzam",
    version="1.0.0",
    author="MUZAM Community",
    author_email="community@muzam.org",
    description="Open Source Audio Recognition Engine - Better than Shazam",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/muzam-project/muzam",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "web": ["fastapi>=0.100.0", "uvicorn>=0.23.0", "jinja2>=3.1.0"],
        "cli": ["click>=8.0.0", "rich>=13.0.0"],
        "ml": ["scikit-learn>=1.0.0", "tensorflow>=2.13.0"],
        "dev": ["pytest>=7.0.0", "black>=23.0.0", "flake8>=6.0.0"],
        "all": [
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
            "jinja2>=3.1.0",
            "click>=8.0.0",
            "rich>=13.0.0",
            "scikit-learn>=1.0.0",
            "tensorflow>=2.13.0",
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "muzam=muzam.cli.main:main",
            "muzam-server=muzam.web.app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "muzam": [
            "web/templates/*.html",
            "web/static/*.css",
            "web/static/*.js",
            "data/*.json",
        ],
    },
    keywords=[
        "audio",
        "recognition",
        "music",
        "shazam",
        "fingerprinting",
        "machine-learning",
        "open-source",
        "privacy",
        "local",
    ],
    project_urls={
        "Bug Reports": "https://github.com/muzam-project/muzam/issues",
        "Source": "https://github.com/muzam-project/muzam",
        "Documentation": "https://docs.muzam.org",
        "Funding": "https://github.com/sponsors/muzam-project",
    },
)
