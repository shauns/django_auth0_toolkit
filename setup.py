#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'requests>=2',
    'PyJWT>=1.4.2',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='django_auth0_toolkit',
    version='0.2.1',
    description="Toolkit for using Auth0 with Django projects",
    long_description=readme + '\n\n' + history,
    author="Shaun Stanworth",
    author_email='shaun.stanworth@googlemail.com',
    url='https://github.com/shauns/django_auth0_toolkit',
    packages=[
        'django_auth0_toolkit',
    ],
    package_dir={'django_auth0_toolkit':
                 'django_auth0_toolkit'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='django_auth0_toolkit',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
