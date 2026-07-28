VENV := .venv
PYTHON := $(VENV)/bin/python
DP := $(VENV)/bin/dp

.DEFAULT_GOAL := install

.PHONY: install update list run test clean

install: $(PYTHON)
	$(PYTHON) -m pip install -e .

$(PYTHON):
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip

update: install

list:
	$(DP) --list

run: install
	$(DP) $(ARGS)

test:
	$(PYTHON) -m unittest discover -s tests -v

clean:
	rm -rf $(VENV) build dist *.egg-info
