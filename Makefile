test:
	@echo "Module - configChecker unit tests."
	@coverage run -m unittest discover -s tests
	@coverage report

