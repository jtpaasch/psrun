program = psrun
src = psrun
tests = tests

clean:
	rm -rf *~ *.swp *.egg* dist .coverage .tox

install:
	pip install --editable .

test:
	python -m flake8 $(src) $(tests)
	coverage run --branch --source $(src) -m unittest -vv --failfast
	coverage report -m --fail-under 100
