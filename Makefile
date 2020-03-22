test:
	@echo "Module - configChecker unit tests."
	@coverage run -m unittest discover -s modules/configChecker/ 
	@python -m unittest tests/test_cmcapi_wrapper.py 
	@coverage report

