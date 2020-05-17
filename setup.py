import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name="reportforce",
    version="0.0.7",
    author="Phelipe Teles",
    author_email="phelipe_teles@hotmail.com",
    description="A Salesforce Analytics API client for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/phelipetls/reportforce",
    packages=setuptools.find_packages(),
    install_requires=["pandas", "requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    project_urls={
        "Documentation": "https://reportforce.readthedocs.io/",
    },
)
