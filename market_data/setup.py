"""
Setup configuration for xVA Market Data Analyzer
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="xva-market-analyzer",
    version="1.0.0",
    author="Jeff Woost",
    author_email="jeff.woost@example.com",
    description="A PyQt5 application for analyzing xVA market data and curve movements",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeff-woost/xva-market-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "xva-analyzer=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.csv", "*.md"],
        "resources": ["icons/*", "images/*", "styles/*"],
        "sample_data": ["*.json", "*.csv"],
    },
)