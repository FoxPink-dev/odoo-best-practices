import os
from setuptools import setup, find_packages

setup(
    name="odoo-best-practices",
    version="1.0.0-beta.1",
    description="Static analysis + knowledge platform for Odoo engineering",
    long_description=open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/FoxPink-dev/odoo-best-practices",
    license="MIT",
    author="FoxPink",
    packages=find_packages(include=["analyzer", "analyzer.*"]),
    include_package_data=True,
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "odoo-review=analyzer.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Quality Assurance",
    ],
)
