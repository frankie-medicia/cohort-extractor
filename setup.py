import os

from setuptools import find_packages, setup

try:
    with open(os.path.join("cohortextractor", "VERSION")) as f:
        version = f.read().strip()
except Exception:
    version = "99.99.99.dev1"

setup(
    name="opensafely-cohort-extractor",
    version=version,
    packages=find_packages(),
    url="https://github.com/opensafely/cohort-extractor",
    author="OpenSAFELY",
    author_email="tech@opensafely.org",
    python_requires=">=3.7",
    install_requires=[
        "lz4",
        "pandas",
        "pyarrow",
        "pyyaml",
        "requests",
        "requests-pkcs12",
        "retry",
        "seaborn",
        "sqlalchemy",
        "sqlparse",
        "structlog",
        "tabulate",
        "tinynetrc",
    ],
    extras_require={
        "drivers": [
            # Used by the EMIS backend
            "presto-python-client",
            # Used by the TPP backend
            "ctds",  # Note: we pin this to specific pre-built wheel in requirements.prod.in
            "pyodbc",
        ]
    },
    entry_points={
        "console_scripts": ["cohortextractor=cohortextractor.cohortextractor:main"]
    },
    include_package_data=True,
    classifiers=["License :: OSI Approved :: GNU General Public License v3 (GPLv3)"],
)
