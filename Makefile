test:
	@coverage run -m unittest discover -s tests
	@coverage report

testRun:
	@./bin/CMCLogger -h
	@./bin/CMCLogger -w testWorkingDir -g 
	@./bin/CMCLogger -a 1234 -w testWorkingDir &
	@sleep 5
	@./bin/CMCLogger -l WARNING -w testWorkingDir &
	@sleep 3
	@./bin/CMCLogger -q BTC
	@./bin/CMCLogger -d -q LTC
	@./bin/CMCLogger -d -j -q ETH
	@./bin/CMCLogger -s
	@./bin/CMCLogger -s -d
	@./bin/CMCLogger -s -j
	@./bin/CMCLogger -s -d -j
	@rm -rf testWorkingDir
	@./bin/CMCLogger -k

