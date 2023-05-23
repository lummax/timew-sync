import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="timew-sync",
    version="0.0.1",
    author="lummax",
    author_email="luogpg@googlemail.com",
    description="Sync timewarrior intervals to JIRA",
    packages=setuptools.find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["timew-report==1.0.2", "requests==2.31.0", "toml==0.10.1"],
    entry_points={"console_scripts": ["timew-sync = timew_sync.__main__:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
