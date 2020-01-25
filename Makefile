test:
	cd tests && python3 -m unittest -v -f

publish:
	python3 setup.py sdist bdist_wheel
	twine upload --skip-existing dist/*
	rm -rf build dist .egg seriesbr.egg-info

docs:
	cd docs && make html

coverage:
	pytest --cov=seriesbr

lint:
	flake8 seriesbr

cov:
	pytest --cov=seriesbr --cov-report term-missing
