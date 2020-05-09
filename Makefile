SHELL=/bin/bash

PACKAGE = reportforce
TEST_DIR = tests

test:
	pytest

CLEAR_PACKAGING = rm -rf build dist $(PACKAGE).egg-info

clean:
	$(CLEAR_PACKAGING)
	$(CLEAR_COVERAGE)

publish:
	python3 setup.py sdist bdist_wheel
	twine upload --skip-existing dist/*
	$(CLEAR_PACKAGING)

lint:
	flake8 $(PACKAGE)

COVERAGE = pytest --cov=reportforce tests
CLEAR_COVERAGE = coverage erase

cov:
	$(COVERAGE)
	$(CLEAR_COVERAGE)

htmlcov:
	$(COVERAGE)
	coverage html
	$(CLEAR_COVERAGE)
	firefox htmlcov/index.html

fix:
	nvim -q <(flake8 $(PACKAGE) tests)

PROFILE_SCRIPT = profiler.py
PROFILE_OUTPUT = profile.txt

profile:
	python3 -m cProfile -o $(PROFILE_OUTPUT) -s cumtime $(PROFILE_SCRIPT)

.PHONY: test publish lint cov fix htmlcov profile
