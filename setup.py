import os

from setuptools import find_packages, setup

with open("requirements.in") as f:
    install_requires = [line for line in f if line and line[0] not in "#-"]

with open("dev_requirements.in") as f:
    tests_require = [line for line in f if line and line[0] not in "#-"]

setup(
    name="giges",
    version=os.getenv("PACKAGE_VERSION") or "dev",
    url="https://github.com/tesselo/giges",
    author="Daniel Moreno",
    author_email="daniel.moreno@tesselo.com",
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    include_package_data=True,
    classifiers=[
        "Private :: Do Not Upload",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
)

