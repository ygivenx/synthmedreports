from setuptools import setup, find_packages

setup(
    name="synthmedreports",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pydantic",
        "pandas",
        "pyarrow",  # Required for Parquet output]
    ],
    entry_points={
        "console_scripts": ["generate_reports=synthmedreports.generate_reports:main"]
    },
    author="Rohan Singh",
    author_email="singhrohan@outlook.com",
    description="A customizable tool for generating synthetic medical report CSV files.",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
