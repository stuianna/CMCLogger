# Filenames
input_configuation_filename = "config.ini"
data_file_directory = "data"
log_file_directory = data_file_directory
status_file_directory = data_file_directory
log_file_name = "log"
database_file_name = 'cryptoData.db'
status_file_name = 'status.ini'
appNameDirectory = 'CMCLogger'

# Configuration file section and option names
API_section_name = "CMC_API"
API_option_private_key = "api_private_key"
API_option_privatate_key_default = 'your-private-key-here'
API_option_conversion_currency = 'conversion_currency'
API_option_conversion_currency_default = 'AUD'
API_option_conversion_currency_symbol = 'curreny_symbol'
API_option_conversion_currency_symbol_default = '$'
API_option_start_index = 'rank_start_index'
API_option_start_index_default =  1
API_option_end_index = 'rank_end_index'
API_option_end_index_default = 200
API_option_interval = 'request_interval'
API_option_interval_default = 5

general_section_name = "General"
general_option_status_file_format = 'status_file_format'
general_option_status_file_format_default = 'ini'

# Data output json infomration
output_json_last_call = "last_call"
output_json_health = "health"

# Coinmarketcap API information
getLatest_Url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
getLatest_Parameters = {
        'start'             : 1,
        'limit'             : 10,
        'convert'           : 'AUD',
        'sort'              : 'market_cap'
        }
getLatest_Headers = {
        'Accepts'           : 'application/json',
        'X-CMC_PRO_API_KEY' : 'default'
        }
API_call_timeout_seconds = 5
API_callRetriesOnFailure = 3

CMC_status_timestamp = 'timestamp'
CMC_status_error_code = 'error_code'
CMC_status_error_message = 'error_message'
CMC_status_elapsed = 'elapsed'
CMC_status_credit_count = 'credit_count'

CMC_data_id = "id"
CMC_data_id_type = "INTEGER"
CMC_data_name = "name"
CMC_data_name_type = "TEXT"
CMC_data_symbol = "symbol"
CMC_data_symbol_type = "TEXT"
CMC_data_slug = "slug"
CMC_data_slug_type = "TEXT"
CMC_data_cmc_rank = "cmc_rank"
CMC_data_cmc_rank_type = "INTEGER"
CMC_data_num_market_pairs = "num_market_pairs"
CMC_data_num_market_pairs_type = "INTEGER"
CMC_data_circulating_suuply = "circulating_supply"
CMC_data_circulating_suuply_type = "REAL"
CMC_data_total_supply = "total_supply"
CMC_data_total_supply_type = "REAL"
CMC_data_max_supply = "max_supply"
CMC_data_max_supply_type = "INTEGER"
CMC_data_last_updated = "last_updated"
CMC_data_last_updated_type = "INTEGER"
CMC_data_data_added = "date_added"
CMC_data_data_added_type = "INTEGER"
CMC_data_tags = "tags"
CMC_data_tags_type = "TEXT"
CMC_data_platform = "platform"
CMC_data_platform_type = "TEXT"
CMC_data_quote = "quote"
CMC_data_quote_price = "price"
CMC_data_quote_price_type = "REAL"
CMC_data_quote_volume_24h = "volume_24h"
CMC_data_quote_volume_24h_type = "REAL"
CMC_data_quote_market_cap = "market_cap"
CMC_data_quote_market_cap_type = "REAL"
CMC_data_percent_change_1h = "percent_change_1h"
CMC_data_percent_change_1h_type = "REAL"
CMC_data_percent_change_24h = "percent_change_24h"
CMC_data_percent_change_24h_type = "REAL"
CMC_data_percent_change_7d = "percent_change_7d"
CMC_data_percent_change_7d_type = "REAL"

# Status file section and option names
status_file_last_call_section_name = 'Last Successful Call'
status_file_option_timeStamp = CMC_status_timestamp
status_file_option_error_code = CMC_status_error_code
status_file_option_error_message = CMC_status_error_message
status_file_option_elapsed = CMC_status_elapsed
status_file_option_credit_count = CMC_status_credit_count
status_file_option_health = "health"

status_file_current_session_section_name = 'Current Session'
status_file_option_successful_calls = 'successful_calls'
status_file_option_failed_calls = 'failed_calls'
status_file_option_success_rate = 'success_rate'

status_file_all_time_section_name = 'All Time'

status_file_last_failed_secion_name = 'Last Failed Call'

# Data query information
data_query_type = "query_type"
data_query_type_price = "query_type_price"
data_query_type_status = "query_type_status"
data_query_tag = "query_tag"
data_query_format = "output_format"
data_query_format_stdout = "output_format_stdout"
data_query_format_json = "output_format_json"
data_query_detail = "output_detail"
data_query_detail_short = "output_detail_short"
data_query_detail_long = "output_detail_long"
