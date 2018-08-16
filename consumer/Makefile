.PHONY: all

run:
	python manage.py runserver

run-web:
	npm start

postgres:
	@psql -h localhost -c "$$COMMAND"

reset-db:
	@$(MAKE) postgres	COMMAND="DROP DATABASE xt"
	@$(MAKE) postgres COMMAND="CREATE DATABASE xt"
	python manage.py migrate

company-fixture:
	python manage.py fetch_basic_companies
