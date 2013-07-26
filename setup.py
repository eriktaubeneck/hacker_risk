"""
Risk
-----------------------

Objects and methods for playing the boardgame Risk
"""
from setuptools import setup, find_packages
import risk

setup(
        name = "Risk",
        version = risk.__version__,
        url = 'https://github.com/eriktaubeneck/hacker-risk',
        author = 'Erik Taubeneck',
        author_email = 'erik.taubeneck@gmail.com',
        description = 'Objects and mthods for playing the boardgame Risk',
        packages = find_packages(),
        package_data = {
            '':['*.json'],
            },
        zip_safe=False,
        platforms = 'any',
        include_package_data=True,
        test_suite="tests",
        install_requires=[],
        tests_require=[],
        classifiers=[
                    'Environment :: Web Environment',
                    'Intended Audience :: Developers',
                    'Operating System :: OS Independent',
                    'Programming Language :: Python',
                    'Topic :: Software Development :: Libraries :: Python Modules'
                    ],
    )
