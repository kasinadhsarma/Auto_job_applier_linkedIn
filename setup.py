"""
Setup script for LinkedIn Auto Job Applier.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="linkedin-auto-applier",
    version="1.0.0",
    author="LinkedIn Auto Job Applier Contributors",
    description="A modular and configurable automation tool for applying to jobs on LinkedIn",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/Auto_job_applier_linkedIn",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Scheduling",
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
    entry_points={
        "console_scripts": [
            "linkedin-apply=main:main",
        ],
    },
    package_data={
        "app": [
            "config/*.example",
            "data/resumes/.gitkeep",
            "data/logs/.gitkeep",
            "data/history/.gitkeep",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
