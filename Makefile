.PHONY: install dev_install upgrade_dependencies

install:
	pip install -r requirements.txt

dev_install: install
	pip install -r dev_requirements.txt
	pre-commit install
	pre-commit install --hook-type commit-msg

upgrade_dependencies: dev_install
	pip install pip-tools
	pip-compile --upgrade --output-file ./requirements.txt requirements.in
	pip-compile --upgrade --output-file ./dev_requirements.txt dev_requirements.in

mypy:
	python -m mypy --config-file ./mypy.ini giges --txt-report .mypy_reports
	cat .mypy_reports/index.txt

coverage:
	python -m pytest --cov=giges --cov-report term --cov-report html:reports/coverage-integration --cov-report term:skip-covered

pre-commit:
	pre-commit run -a

check: pre-commit  mypy coverage
