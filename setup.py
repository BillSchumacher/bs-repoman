from setuptools import setup

setup(
    name='bs-repoman',
    version='0.1.0',
    py_modules=['bs_repoman'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'bs_repoman = repoman:cli',
        ],
    },
    scripts=[
        'bs_repoman/scripts/repoman.py',
    ],
)
