[![Build Status](https://travis-ci.org/stuianna/CMCLogger.svg?branch=master)](https://travis-ci.org/stuianna/CMCLogger)
![Codecov](https://img.shields.io/codecov/c/github/stuianna/CMCLogger)
![GitHub](https://img.shields.io/github/license/stuianna/CMCLogger)

# CMCLogger - Coin Market Cap Cryptocurreny Data Logger

A python API and script for requesting, parsing and storing the latest cryptocurrency data availalbe using the [Coin Market Cap Free API](https://coinmarketcap.com/api/). Data entries are stored in a SQLite3 database, with CLI features for querying data and logger status.

## TLDR - Just Get Some Data

```bash
# Install the module and script
pip install CMCLogger

# Initialise the required configuration, supplying your API key. (Made above)
CMCLogger -a 'your-api-key' -g

# Start the logger. Use 'nohup CMCLogger' to start detached, 'CMCLogger &' to start in background.
CMCLogger 

# Query the latest stored price information for ticker 'BTC'
CMCLogger -q BTC
'BTC: $11676.55 (3.53%)'

# Same as above, but more detailed.
CMCLogger -dq BTC
'BTC: $11676.55 1H: -0.22% 1D: 3.53% 7D: 4.77% 24h Volume: 66.65 Billion'

# Get the logger status. Health is the moving average success rate of the last 30 calls.
CMCLogger -s
'Last successful call 1 minutes ago, health 100.0%.'

# Stop the logger
CMCLogger -k

# Copy the SQLite database to an excel file
CMCLogger -x
```

## Stored Data

When the logger is initialised, it creates a directory structure inside `$XDG_CONFIG_HOME`. This could be `~/.local/share/CMCLogger` or `~/.config/CMCLogger`, use `echo $XDG_CONFIG_HOME` to find the location on your system.

The directory structure is as follows:

```bash
CMCLogger
├── config.ini
└── data
    ├── cryptoData.db
    ├── log
    └── status.ini
```

**config.ini**

Contains configuration parameters used. Change any of these settings and restart the logger to apply them. Values shown are the default.
```ini
[CMC_API]
api_private_key = your-private-key-here
conversion_currency = AUD
curreny_symbol = $
rank_start_index = 1
rank_end_index = 200
request_interval = 5

[General]
status_file_format = ini
```

**cryptoData.db**

A SQLite3 database containing all data retreived by the logger. The database contains a separate table, named afeter the cryptocurrency symbol for each individual currecy collected. [SQLitebrower](https://sqlitebrowser.org/), is a good tool for browsing databases, or use `CMCLogger -x` to convert the database to an Excel file for viewing.


**status.ini**

Contains information on the status of the logger. This information is queried and returned  when using `CMCLogger -s` or `CMCLogger -ds`
```ini
[Last Successful Call]
timestamp = 2020-04-23 23:10:55.275000+03:00
error_code = 0
error_message = None
elapsed = 17
credit_count = 1

[Last Failed Call]
timestamp = 2020-04-23 22:39:26.646297+03:00
error_code = 255
error_message = No network connections available.
elapsed = 0
credit_count = 0

[Current Session]
health = 100.0
successful_calls = 35644
failed_calls = 587
success_rate = 98.38

[All Time]
successful_calls = 35746
failed_calls = 589
success_rate = 98.38
```

**log**

Runtime logs stored by the Python logging module.

## Polybar / I3WM Integration

**I3WM**

Add to `.i3/config` to start the logger on login.
```bash
exec --no-startup-id CMCLogger
```


**Polybar**

Add a polybar module for the target bar:
```bash
[module/crypto]
type = custom/script
exec = ~/bin/crypto
tail = true
interval = 300
```

The target script simply cycles through a set of symbols, a blank string is returned if the last entry was more than 10 minutes ago.
```bash
#!/bin/bash

queryArray=("BTC" "LTC" "ETH")
TEMPFILE="/tmp/tmp.CMCLOGGER"
source $TEMPFILE 2> /dev/null

function getNextSymbol {
	position=0
	for symbol in ${queryArray[@]}; do
		((position++))
		if [[ "$symbol" == "$LAST_SYMBOL" ]]; then
			size=${#queryArray[@]}
			position=$((position%size))
			CURRENT_SYMBOL=${queryArray[$position]}
			break
		fi
		CURRENT_SYMBOL=${queryArray[0]}
	done
	echo "LAST_SYMBOL=$CURRENT_SYMBOL" > $TEMPFILE
}

function checkStatus {
	jsonStatus=$(CMCLogger -js 2> /dev/null)
	lastCall=$(echo "$jsonStatus" | jq -r '.last_call')

	if (( $lastCall > 10 )); then
		echo ''
		exit
	fi
}

getNextSymbol
checkStatus
CMCLogger -q $CURRENT_SYMBOL
```
