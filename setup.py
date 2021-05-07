import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

DEPENDENCIES = [
    "APScheduler",
    "dash",
    "dash_bootstrap_components",
    "dataclasses;python_version<'3.7'",
    "fire",
    "pandas",
    "pynvml",
    "requests",
    "psutil",
    "py-cpuinfo",
]

TEST_DEPENDENCIES = ["mock", "pytest", "responses", "tox", "numpy"]


setuptools.setup(
    name="codecarbon",
    version="1.2.0",
    author="Mila, DataForGood, BCG GAMMA, Comet.ml, Haverford College",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    install_requires=DEPENDENCIES,
    tests_require=TEST_DEPENDENCIES,
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    package_data={
        "codecarbon": [
            "data/cloud/impact.csv",
            "data/hardware/cpu_power.csv",
            "data/private_infra/2016/usa_emissions.json",
            "data/private_infra/2016/canada_energy_mix.json",
            "data/private_infra/2016/global_energy_mix.json",
            "viz/assets/*.png",
        ],
    },
    python_requires=">=3.6",
    entry_points={"console_scripts": ["carbonboard = codecarbon.viz.carbonboard:main"]},
)
