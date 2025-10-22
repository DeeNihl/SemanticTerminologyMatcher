"""Setup script for Semantic Terminology Matcher."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="semantic-terminology-matcher",
    version="0.1.0",
    author="Your Name",
    description="OMOP Concepts Vector Store with FastAPI and CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/SemanticTerminologyMatcher",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
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
            "semantic-matcher=semantic_matcher.cli.main:cli",
        ],
    },
)
