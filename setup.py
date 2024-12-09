from setuptools import find_packages, setup

setup(
    name="sc-proj-gbm-radiomics",
    version="0.1.0",
    packages=find_packages(),
    # entry_points={
    #     "console_scripts": [
    #         # Add command line scripts here
    #     ],
    # },
    author="Nabil Jabareen",
    author_email="nabil.jabareen@gmail.com",
    description="A gridsearch generator for parallel computing.",
    url="https://github.com/NabJa/gridsearch",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
