test:
	python3 -m unittest discover -vfs tests

publish:
	python3 setup.py sdist bdist_wheel
	twine upload --skip-existing dist/*
	rm -rf build dist .egg seriesbr.egg-info

docs:
	cd docs && make html

coverage:
	pytest --cov=reportforce

lint:
	flake8 reportforce

cov:
	pytest --cov=reportforce --cov-report term-missing

fix:
	nvim -q <(flake8 .)

ctags:
	.git/hooks/ctags
