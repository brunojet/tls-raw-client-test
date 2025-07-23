#!/usr/bin/env python3
"""
Setup script for TLS Raw Client
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "TLS Raw Client - A Python library for low-level TLS diagnostics and proxy support."

# Read version from __init__.py
def read_version():
    version_file = os.path.join("src", "tlsraw", "__init__.py")
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.0"

setup(
    name="tlsraw",
    version=read_version(),
    author="Bruno Jet",
    author_email="your.email@example.com",
    description="A Python library for low-level TLS diagnostics and proxy support",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/brunojet/tls-raw-client-test",
    project_urls={
        "Bug Tracker": "https://github.com/brunojet/tls-raw-client-test/issues",
        "Documentation": "https://github.com/brunojet/tls-raw-client-test#readme",
        "Source Code": "https://github.com/brunojet/tls-raw-client-test",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security :: Cryptography",
        "Topic :: System :: Networking",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    install_requires=[
        # Only standard library dependencies
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "tlsraw-test=tlsraw.tls_raw_client:main",
            "tlsraw-proxy=tlsraw.proxy_tls_client:main",
            "tlsraw-diagnostic=tlsraw.firewall_diagnostic:main",
        ],
    },
    keywords=[
        "tls", "ssl", "proxy", "firewall", "diagnostics", "networking", 
        "corporate", "lambda", "aws", "raw-sockets"
    ],
    include_package_data=True,
    zip_safe=False,
)
