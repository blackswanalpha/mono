#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="mono-lang",
    version="1.0.0",
    description="Mono Language Interpreter",
    author="Mono Team",
    author_email="info@mono-lang.org",
    url="https://github.com/mono-lang/mono",
    packages=find_packages(),
    scripts=["bin/mono", "bin/reactive-mono"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
)
