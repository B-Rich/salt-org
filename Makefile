SHELL := /bin/bash
.PHONY: lint test deps

test: deps
	pep8 --config ./pep8 .

lint: deps
	autopep8 -i -r -j0 -a --experimental --max-line-length 100 --indent-size 2 .

deps:
	pip install -r requirements.txt
