#
#   Package Management
#
.PHONY: install dev_install upgrade_dependencies

cli_install:
	pip install -e .

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

#
#   Code Checks
#
.PHONY: pre-commit mypy coverage check

pre-commit:
	pre-commit run -a

mypy:
	python -m mypy --config-file ./mypy.ini giges --txt-report .mypy_reports
	cat .mypy_reports/index.txt

coverage:
	GIGES_SETTINGS=giges.settings.TestingSettings \
	python -m pytest --cov=giges --cov-report term --cov-report html:reports/coverage-integration --cov-report term:skip-covered


check: pre-commit  mypy coverage

#
#   Extended Reports
#
.PHONY: smells security complexity check-advanced check-extended

smells:
	pip install semgrep
	semgrep --config=p/r2c-ci --config=p/flask

security:
	bandit -r pxsearch

complexity:
	wily build giges
	wily report giges

doc-style:
	pydocstyle giges

check-advanced: smells security
check-picky: complexity doc-style
check-extended: check check-advanced check-picky

#
#   Code Checks auto-fix
#
.PHONY: black

black:
	python -m black -l79 -tpy38 giges migrations test *.py
