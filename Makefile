WORKDIR = $(shell pwd)
VENV = $(WORKDIR)/venv
PYTHON = $(VENV)/bin/python
PIP =  $(VENV)/bin/pip
MANAGE = $(PYTHON) $(WORKDIR)/src/manage.py

clean:
	rm -rf $(VENV)

makemessages:
	 cd src; $(MANAGE) makemessages -l cs

compilemessages:
	 cd src; $(MANAGE) compilemessages

makemigrations:
	$(MANAGE) makemigrations imposter

migrate:
	  $(MANAGE) migrate

loaddata:
	$(MANAGE) loaddata src/fixtures/bureau.json
	$(MANAGE) load_specs

install: clean
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt
	make migrate
	make loaddata
	make compilemessages

test:
	  $(MANAGE) test
