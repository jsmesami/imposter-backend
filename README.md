# Imposter Backend

The backend part of automated poster generation system for 
Municipal Library of Prague.

[![Build Status](https://travis-ci.org/jsmesami/imposter-backend.svg?branch=master)](https://travis-ci.org/jsmesami/imposter-backend)

## Overview

A standalone repository of Django backend API for ClojureScript
[frontend](https://github.com/jsmesami/imposter-frontend). 

## Deployment and development

### Prequisities

* Python 3.5+
* PostgreSQL 9 (only tested with 9.6)
* Ghostscript
* ImageMagick

### Installation

    # Create and edit local settings to match your setup:
    cp src/settings/local_[deploy|devel]_example.py src/settings/local.py
    vim src/settings/local.py
    
    # Create database to match your settings, eg.:
    psql -c "CREATE DATABASE imposter OWNER=imposter"
    
    # run installation
    make install

### Running the server

Project includes [Chaussette](https://chaussette.readthedocs.io/) as a WSGI server 
and [Circus](https://circus.readthedocs.io/) as supervisor. 

    make start
    make restart
    make stop 

### Testing

    make test

## Documentation

API is documented [here](docs/API.apib) or can be browsed at [Apiary](https://imposterapi.docs.apiary.io/).
Poster specification format is described [here](docs/SPEC.md).

## License

Copyright © 2018 Ondřej Nejedlý

Distributed under the Eclipse Public License either version 1.0 or 
(at your option) any later version.
