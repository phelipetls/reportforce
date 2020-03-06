test:
	python3 -m unittest discover -vfs tests

publish:
	python3 setup.py sdist bdist_wheel
	twine upload --skip-existing dist/*
	rm -rf build dist .egg seriesbr.egg-info

docs:
	cd docs && make html

lint:
	flake8 reportforce

cov:
	coverage run --source reportforce/ -m unittest discover -s tests && coverage report && coverage erase

fix:
	nvim -q <(flake8 .)

ctags:
	.git/hooks/ctags
