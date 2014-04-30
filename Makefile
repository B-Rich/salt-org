SHELL := /bin/bash
.PHONY: lint test deps

lint: deps
	pep8 --config ./pep8 .

format: deps
	autopep8 -i -r -j0 -a --experimental --max-line-length 100 --indent-size 2 .

deps:
	pip install -r requirements.txt
