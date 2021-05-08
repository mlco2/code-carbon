import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

DEPENDENCIES = [
    "uvicorn[standard]==0.13.4",
    "fastapi==0.63.0",
    "sqlalchemy",
]

TEST_DEPENDENCIES = ["mock", "pytest", "responses", "tox", "pydantic[email]"]


setuptools.setup(
    name="carbonserver",
    version="0.1.0",
    author="BCG GAMMA, Comet.ml, Haverford College, MILA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    install_requires=DEPENDENCIES,
    tests_require=TEST_DEPENDENCIES,
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
    ],
    python_requires=">=3.7",
    entry_points={"console_scripts": ["carbonserver = carbonserver:main"]},
)
