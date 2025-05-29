from setuptools import setup, find_packages

setup(
    name="fedloadw",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "spacy",
        "schedule",
        "uvicorn",
        "fastapi",
        "pytest",
        "pytest-cov"
    ],
    package_data={
        "fedloadw": ["*.json"]
    },
    entry_points={
        "console_scripts": [
            "fedloadw=fedloadw.scheduler:main"
        ]
    }
)
