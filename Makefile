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
