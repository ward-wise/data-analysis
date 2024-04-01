IMAGE_URI=ward-wise/data-anaylsis


.PHONY: build_image
build_image:
	echo "building image" && \
	docker build \
		-f ./Dockerfile \
		-t "${IMAGE_URI}" \
		.


.PHONY: setup_env
setup_env:
	pip install --upgrade pip
	pip install --prefer-binary .


.PHONY: run_ward_spending_scripts
run_ward_spending_scripts: setup_env
	extract_ward_spending_data_from_pdfs && \
	postprocess_and_combine_ward_spending_data && \
	generate_ward_spending_geocoding


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


.PHONY: format_docker
format_docker:
	docker run \
	  -v $$(pwd):/app \
	  --workdir /app \
	  --entrypoint="" \
	  --rm \
	  -t python:3.12-slim \
	  /bin/bash -c "apt-get update && apt-get install make && make format"


.PHONY: lint
lint: setup_env_dev
	ruff format . --check
	ruff check . --no-fix


.PHONY: lint_docker
lint_docker:
	docker run \
	  -v $$(pwd):/app \
	  --workdir /app \
	  --entrypoint="" \
	  --rm \
	  -t python:3.12-slim \
	  /bin/bash -c "apt-get update && apt-get install make && make lint"


.PHONY: test
test: setup_env setup_env_dev
	PYTHONPATH="$${PWD}" \
	pytest \
		-m "not integration_test" \
		--cov $${PWD}/src \
		-v \
		tests/


.PHONY: test_docker
test_docker: build_image
	docker run \
	  -v $$(pwd)/Makefile:/app/Makefile \
	  -v $$(pwd)/requirements-dev.txt:/app/requirements-dev.txt \
	  -v $$(pwd)/tests:/app/tests \
	  --workdir /app \
	  --entrypoint="" \
	  --rm \
	  -it "${IMAGE_URI}" \
	  /bin/bash -c "make test"


.PHONY: integration_test
integration_test: setup_env setup_env_dev
	PYTHONPATH="$${PWD}" \
	app_token=$(app_token) \
	pytest \
		-m "integration_test" \
		-v \
		tests/


.PHONY: integration_test_docker
integration_test_docker: build_image
	docker run \
	  -v $$(pwd)/Makefile:/app/Makefile \
	  -v $$(pwd)/requirements-dev.txt:/app/requirements-dev.txt \
	  -v $$(pwd)/tests:/app/tests \
	  --workdir /app \
	  --entrypoint="" \
	  --rm \
	  -t "${IMAGE_URI}" \
	  /bin/bash -c "apt-get update && apt-get install make && make integration_test"
