SHELL := /bin/bash
.PHONY: lint test deps format

test: deps lint format
	python -m unittest discover -s test

deps:
	pip install -r test/requirements.txt

lint: deps
	pep8 --config ./pep8 .

format: deps
	autopep8 -i -r -j0 -a --experimental --max-line-length 100 --indent-size 2 .
