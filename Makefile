include .env

.PHONY: setup_env
setup_env:
	pip install --upgrade pip
	pip install --prefer-binary .


.PHONY: run_ward_spending_scripts
run_ward_spending_scripts: setup_env
	extract_ward_spending_data_from_pdfs && \
	postprocess_and_combine_ward_spending_data && \
	app_token=$(app_token) generate_ward_spending_geocoding


.PHONY: run_bikeway_installation_scripts
run_bikeway_installation_scripts: setup_env
	generate_bikeway_installations_geocoding


.PHONY: setup_env_dev
setup_env_dev:
	pip install --upgrade pip
	pip install --prefer-binary -r requirements-dev.txt


.PHONY: format
format: setup_env_dev
	ruff format .
	ruff check . --fix


.PHONY: lint
lint: setup_env_dev
	ruff format . --check
	ruff check . --no-fix


.PHONY: test
test: setup_env setup_env_dev
	PYTHONPATH="$${PWD}" \
	pytest \
		-m "not integration_test" \
		--cov $${PWD}/src \
		-v \
		tests/


.PHONY: integration_test
integration_test: setup_env setup_env_dev
	PYTHONPATH="$${PWD}" \
	app_token=$(app_token) \
	pytest \
		-m "integration_test" \
		-v \
		tests/
