# Imposter Backend

The backend part of automated poster generation system for 
Municipal Library of Prague.

[![Build Status](https://travis-ci.org/jsmesami/imposter-backend.svg?branch=master)](https://travis-ci.org/jsmesami/imposter-backend)

## Overview

A standalone repository of Django backend API for ClojureScript
[frontend](https://github.com/jsmesami/imposter-frontend). 

## Development

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

### Testing

    make test

## License

Copyright © 2017 Ondřej Nejedlý

Distributed under the Eclipse Public License either version 1.0 or 
(at your option) any later version.
