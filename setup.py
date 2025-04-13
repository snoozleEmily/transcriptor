from setuptools import setup, find_packages
from src import __version__


from config.__authors__ import __author__
from config.requirements import get_requirements
from config.classifiers import CLASSIFIERS
from config.metadata import NAME, DESCRIPTION, LICENSE, KEYWORDS, PROJECT_URLS



setup(
    name=NAME,
    version=__version__,
    author=__author__,
    description=DESCRIPTION,
    url=PROJECT_URLS["github_repo"],
    project_urls=PROJECT_URLS,
    license=LICENSE,
    classifiers=CLASSIFIERS,
    packages=find_packages(where="src", exclude=["_deprecated*"]),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=get_requirements(),
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            f"{NAME}=transcriptor.cli:main",
        ],
    },
    keywords=KEYWORDS,
)
