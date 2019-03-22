#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name='Imposter Backend',
    description='The backend part of automated poster generation system for Municipal Library of Prague',
    version='1.0.4',
    author='Ondřej Nejedlý',
    url='https://github.com/jsmesami/imposter-backend',
    license='EPL',
    python_requires='>=3.5',
    install_requires=open('requirements.txt').readlines(),
    packages=find_packages(),
    scripts=['src/manage.py'],
    test_suite='tests',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: EPL-1.0 License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
