test:
	@echo "Module - configChecker unit tests."
	@coverage run -m unittest discover -s modules/configChecker/ 
	@coverage run -a tests/test_responseFetcher.py
	@coverage report

