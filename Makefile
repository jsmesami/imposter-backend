WORKDIR = $(shell pwd)
MANAGE = python $(WORKDIR)/src/manage.py


makemessages:
	cd src && $(MANAGE) makemessages -l cs

compilemessages:
	cd src && $(MANAGE) compilemessages

makemigrations:
	$(MANAGE) makemigrations imposter

migrate:
	$(MANAGE) migrate

loaddata:
	$(MANAGE) loaddata src/fixtures/bureau.json
	$(MANAGE) load_specs

install:
	pip install -r requirements.txt
	make migrate
	make loaddata
	make compilemessages

test:
	$(MANAGE) test

start:
	circusd --daemon circus.ini

stop:
	circusctl quit

restart:
	circusctl restart
