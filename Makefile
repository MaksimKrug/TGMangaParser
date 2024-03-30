PYTHON ?= python3
CODE = src

pretty:
ifneq ($(CODE),)
	unify --in-place --recursive $(CODE)
	black --target-version py310 --skip-string-normalization $(CODE)
	isort $(CODE)
endif

lint:
ifneq ($(CODE),)
	black --target-version py310 --check --skip-string-normalization $(CODE)
	pylint --rcfile=setup.cfg $(CODE)
	mypy --install-types --non-interactive --config-file setup.cfg $(CODE)
endif