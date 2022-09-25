from os.path import exists
from setuptools import setup, find_packages

setup(
    name='bs-repoman',
    author="Bill Schumacher",
    author_email="34168009+BillSchumacher@users.noreply.github.com",
    version='0.2.0',
    packages=find_packages(),
    py_modules=['bs_repoman'],
    install_requires=[
        'Click',
        'bs-pathutils',
    ],
    entry_points={
        'console_scripts': [
            'bs_repoman = repoman:cli',
        ],
    },
    scripts=[
        'bs_repoman/scripts/repoman.py',
    ],
    url="https://github.com/BillSchumacher/bs-repoman",
    license="MIT",
    description="Utility for reduced boilerplate work.",
    long_description=open("README.md").read() if exists("README.md") else "",
    long_description_content_type='text/markdown',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries",
    ],
)
