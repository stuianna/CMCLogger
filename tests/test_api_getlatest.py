import unittest
from unittest import mock
import logging
from cmclogger.api.getlatest import CMCGetLatest
from configchecker import ConfigChecker
from requests.models import Response
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import cmclogger.settings as settings
import json
import datetime

logging.disable(logging.CRITICAL)

response_status_401 = {"status": {"timestamp": "2018-06-02T22:51:28.209Z","error_code": 1002,"error_message": "API key missing.","elapsed": 10,"credit_count": 0}}

response_200 = {"status": {"timestamp": "2020-03-22T21:42:32.862Z", "error_code": 0, "error_message": None, "elapsed": 11, "credit_count": 1, "notice": None}, "data": [{"id": 1, "name": "Bitcoin", "symbol": "BTC", "slug": "bitcoin", "num_market_pairs": 7802, "date_added": "2013-04-28T00:00:00.000Z", "tags": ["mineable"], "max_supply": 21000000, "circulating_supply": 18282325, "total_supply": 18282325, "platform": None, "cmc_rank": 1, "last_updated": "2020-03-22T21:41:39.000Z", "quote": {"AUD": {"price": 10349.875293052113, "volume_24h": 68924929543.68837, "percent_change_1h": 2.03454894, "percent_change_24h": -3.98809565, "percent_change_7d": 19.18056641, "market_cap": 189219783817.04898, "last_updated": "2020-03-22T21:42:00.000Z"}}}]}

response_200_no_data = {"status": {"timestamp": "2020-03-22T21:42:32.862Z", "error_code": 0, "error_message": None, "elapsed": 11, "credit_count": 1, "notice": None}, "data": []}

response_200_bad_data_key = {"status": {"timestamp": "2020-03-22T21:42:32.862Z", "error_code": 0, "error_message": None, "elapsed": 11, "credit_count": 1, "notice": None}, "data": [{"id": 1, "name": "Bitcoin", "badKey": "BTC", "slug": "bitcoin", "num_market_pairs": 7802, "date_added": "2013-04-28T00:00:00.000Z", "tags": ["mineable"], "max_supply": 21000000, "circulating_supply": 18282325, "total_supply": 18282325, "platform": None, "cmc_rank": 1, "last_updated": "2020-03-22T21:41:39.000Z", "quote": {"AUD": {"price": 10349.875293052113, "volume_24h": 68924929543.68837, "percent_change_1h": 2.03454894, "percent_change_24h": -3.98809565, "percent_change_7d": 19.18056641, "market_cap": 189219783817.04898, "last_updated": "2020-03-22T21:42:00.000Z"}}}]}

response_200_bad_status_key = {"status": {"badKey": "2020-03-22T21:42:32.862Z", "error_code": 0, "error_message": None, "elapsed": 11, "credit_count": 1, "notice": None}, "data": [{"id": 1, "name": "Bitcoin", "symbol": "BTC", "slug": "bitcoin", "num_market_pairs": 7802, "date_added": "2013-04-28T00:00:00.000Z", "tags": ["mineable"], "max_supply": 21000000, "circulating_supply": 18282325, "total_supply": 18282325, "platform": None, "cmc_rank": 1, "last_updated": "2020-03-22T21:41:39.000Z", "quote": {"AUD": {"price": 10349.875293052113, "volume_24h": 68924929543.68837, "percent_change_1h": 2.03454894, "percent_change_24h": -3.98809565, "percent_change_7d": 19.18056641, "market_cap": 189219783817.04898, "last_updated": "2020-03-22T21:42:00.000Z"}}}]}

response_200_bad_main_key = {"status_bad": {"timestamp": "2020-03-22T21:42:32.862Z", "error_code": 0, "error_message": None, "elapsed": 11, "credit_count": 1, "notice": None}, "data": [{"id": 1, "name": "Bitcoin", "symbol": "BTC", "slug": "bitcoin", "num_market_pairs": 7802, "date_added": "2013-04-28T00:00:00.000Z", "tags": ["mineable"], "max_supply": 21000000, "circulating_supply": 18282325, "total_supply": 18282325, "platform": None, "cmc_rank": 1, "last_updated": "2020-03-22T21:41:39.000Z", "quote": {"AUD": {"price": 10349.875293052113, "volume_24h": 68924929543.68837, "percent_change_1h": 2.03454894, "percent_change_24h": -3.98809565, "percent_change_7d": 19.18056641, "market_cap": 189219783817.04898, "last_updated": "2020-03-22T21:42:00.000Z"}}}]}

response_bad_json = 'asdfa {sdf}'

class CMCAPI_configuration_setting_and_checking(unittest.TestCase):

    def setUp(self):
        self.config = ConfigChecker()
        self.config.set_expectation(
                settings.API_section_name,
                settings.API_option_private_key,
                str,
                settings.API_option_privatate_key_default)
        self.config.set_expectation(
                settings.
                API_section_name,
                settings.API_option_conversion_currency,
                str,
                settings.API_option_conversion_currency_default)
        self.config.set_expectation(
                settings.API_section_name,
                settings.API_option_start_index,
                int,
                settings.API_option_start_index_default)
        self.config.set_expectation(
                settings.API_section_name,
                settings.API_option_end_index,
                int,
                1)
        self.config.set_expectation(
                settings.API_section_name,
                settings.API_option_interval,
                int,
                settings.API_option_interval_default)

        ## Setting an empty filename automatically loads the default values
        self.config.set_configuration_file('');

        self.api = CMCGetLatest(self.config)

    def test_configuration_is_saved_correctly(self):
        apiConfig = self.api.getConfiguration()
        self.assertIs(apiConfig['privateKey'],settings.API_option_privatate_key_default)
        self.assertIs(apiConfig['conversionCurrency'],settings.API_option_conversion_currency_default)
        self.assertIs(apiConfig['startIndex'],settings.API_option_start_index_default)
        self.assertIs(apiConfig['endIndex'],1)
        self.assertIs(apiConfig['callInterval'],settings.API_option_interval_default)

    def test_configuration_start_index_cant_be_less_than_one(self):
        self.config.set_value(settings.API_section_name,settings.API_option_start_index,-1)
        self.api = CMCGetLatest(self.config)
        apiConfig = self.api.getConfiguration()
        self.assertIs(apiConfig['startIndex'],settings.API_option_start_index_default)

    def test_configuration_end_index_cant_be_less_than_start_index(self):
        self.config.set_value(settings.API_section_name,settings.API_option_start_index,10)
        self.config.set_value(settings.API_section_name,settings.API_option_end_index,1)
        self.api = CMCGetLatest(self.config)
        apiConfig = self.api.getConfiguration()
        self.assertIs(apiConfig['endIndex'],10)

    def test_configuration_start_index_cant_be_greater_than_4999(self):
        self.config.set_value(settings.API_section_name,settings.API_option_start_index,5000)
        self.api = CMCGetLatest(self.config)
        apiConfig = self.api.getConfiguration()
        self.assertIs(apiConfig['startIndex'],settings.API_option_start_index_default)

    def test_configuration_call_interval_must_be_greater_than_zero(self):
        self.config.set_value(settings.API_section_name,settings.API_option_interval,0)
        self.api = CMCGetLatest(self.config)
        apiConfig = self.api.getConfiguration()
        self.assertIs(apiConfig['callInterval'],settings.API_option_interval_default)

    def test_configuration_conversion_currency_must_be_of_allowed_type(self):
        self.config.set_value(settings.API_section_name,settings.API_option_conversion_currency,'asdf')
        self.api = CMCGetLatest(self.config)
        apiConfig = self.api.getConfiguration()
        self.assertIs(apiConfig['conversionCurrency'],settings.API_option_conversion_currency_default)

    def test_configuration_api_key_cannot_be_blank(self):
        self.config.set_value(settings.API_section_name,settings.API_option_private_key,'')
        self.api = CMCGetLatest(self.config)
        apiConfig = self.api.getConfiguration()
        self.assertIs(apiConfig['privateKey'],settings.API_option_privatate_key_default)

class API_getting_requests(unittest.TestCase):

    def setUp(self):
        self.config = ConfigChecker()
        self.config.set_expectation(
                settings.API_section_name,
                settings.API_option_private_key,
                str,
                settings.API_option_privatate_key_default)
        self.config.set_expectation(
                settings.
                API_section_name,
                settings.API_option_conversion_currency,
                str,
                settings.API_option_conversion_currency_default)
        self.config.set_expectation(
                settings.API_section_name,
                settings.API_option_start_index,
                int,
                settings.API_option_start_index_default)
        self.config.set_expectation(
                settings.API_section_name,
                settings.API_option_end_index,
                int,
                1)
        self.config.set_expectation(
                settings.API_section_name,
                settings.API_option_interval,
                int,
                settings.API_option_interval_default)

        ## Setting an empty filename automatically loads the default values
        self.config.set_configuration_file('');

        self.api = CMCGetLatest(self.config)

    @mock.patch('cmclogger.api.getlatest.Session.get')
    def test_correctly_formed_api_call(self,session_mock):
        expectedUrl = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        expectedParameters = {
                'start' : self.config.get_value(settings.API_section_name,settings.API_option_start_index),
                'limit' : self.config.get_value(settings.API_section_name,settings.API_option_end_index) - \
                            self.config.get_value(settings.API_section_name,settings.API_option_start_index) + 1,
                'convert' : self.config.get_value(settings.API_section_name,settings.API_option_conversion_currency),
                'sort'  :   'market_cap'
                }
        mock_response = Response()
        mock_response.status_code = 200
        type(mock_response).text = mock.PropertyMock(return_value=json.dumps(response_200))
        session_mock.return_value = mock_response

        self.api.getLatest();
        session_mock.assert_called_with(expectedUrl,params=expectedParameters,timeout=settings.API_call_timeout_seconds)


    @mock.patch('cmclogger.api.getlatest.Session.get')
    def test_status_200_results_in_true_return(self,session_mock):

        mock_response = Response()
        mock_response.status_code = 200
        type(mock_response).text = mock.PropertyMock(return_value=json.dumps(response_200))
        session_mock.return_value = mock_response

        success = self.api.getLatest();
        self.assertIs(success,True)

    @mock.patch('cmclogger.api.getlatest.Session.get')
    def test_custom_status_and_false_returned_if_bad_keys_in_json_response_200(self,session_mock):
        mock_response = Response()
        mock_response.status_code = 200
        type(mock_response).text = mock.PropertyMock(return_value=json.dumps(response_200_bad_main_key))
        session_mock.return_value = mock_response

        success = self.api.getLatest();
        status = self.api.getLatestStatus()
        self.assertIs(success,False)
        self.assertIs(type(status[settings.CMC_status_timestamp]),str)
        self.assertIs(status[settings.CMC_status_error_code],1)
        self.assertIs(type(status[settings.CMC_status_error_message]),str)
        self.assertIs(status[settings.CMC_status_elapsed],0)
        self.assertIs(status[settings.CMC_status_credit_count],0)

    @mock.patch('cmclogger.api.getlatest.Session.get')
    def test_custom_status_and_false_returned_if_bad_keys_in_json_response_not_200(self,session_mock):
        mock_response = Response()
        mock_response.status_code = 401
        type(mock_response).text = mock.PropertyMock(return_value=json.dumps(response_200_bad_main_key))
        session_mock.return_value = mock_response

        success = self.api.getLatest();
        status = self.api.getLatestStatus()
        self.assertIs(success,False)
        self.assertIs(self.api.getLatestData(),None)
        self.assertIs(type(status[settings.CMC_status_timestamp]),str)
        self.assertIs(status[settings.CMC_status_error_code],1)
        self.assertIs(type(status[settings.CMC_status_error_message]),str)
        self.assertIs(status[settings.CMC_status_elapsed],0)
        self.assertIs(status[settings.CMC_status_credit_count],0)

    @mock.patch('cmclogger.api.getlatest.Session.get')
    def test_custom_status_and_false_returned_if_cannot_parse_json_200(self,session_mock):
        mock_response = Response()
        mock_response.status_code = 200
        type(mock_response).text = mock.PropertyMock(return_value=response_bad_json)
        session_mock.return_value = mock_response

        success = self.api.getLatest();
        status = self.api.getLatestStatus()
        self.assertIs(success,False)
        self.assertIs(self.api.getLatestData(),None)
        self.assertIs(type(status[settings.CMC_status_timestamp]),str)
        self.assertIs(status[settings.CMC_status_error_code],2)
        self.assertIs(type(status[settings.CMC_status_error_message]),str)
        self.assertIs(status[settings.CMC_status_elapsed],0)
        self.assertIs(status[settings.CMC_status_credit_count],0)

    @mock.patch('cmclogger.api.getlatest.Session.get')
    def test_custom_status_and_false_returned_if_cannot_parse_json_not_200(self,session_mock):
        mock_response = Response()
        mock_response.status_code = 401
        type(mock_response).text = mock.PropertyMock(return_value=response_bad_json)
        session_mock.return_value = mock_response

        success = self.api.getLatest();
        status = self.api.getLatestStatus()
        self.assertIs(success,False)
        self.assertIs(self.api.getLatestData(),None)
        self.assertIs(type(status[settings.CMC_status_timestamp]),str)
        self.assertIs(status[settings.CMC_status_error_code],2)
        self.assertIs(type(status[settings.CMC_status_error_message]),str)
        self.assertIs(status[settings.CMC_status_elapsed],0)
        self.assertIs(status[settings.CMC_status_credit_count],0)


    @mock.patch('cmclogger.api.getlatest.time.sleep')
    @mock.patch('cmclogger.api.getlatest.Session.get')
    def test_custom_status_and_false_returned_if_connection_error_occurs(self,session_mock,sleep_mock):
        session_mock.side_effect = ConnectionError()

        success = self.api.getLatest();

        settings.API_callRetriesOnFailure = 0
        status = self.api.getLatestStatus()
        self.assertIs(success,False)
        self.assertIs(self.api.getLatestData(),None)
        self.assertIs(type(status[settings.CMC_status_timestamp]),str)
        self.assertIs(status[settings.CMC_status_error_code],3)
        self.assertIs(type(status[settings.CMC_status_error_message]),str)
        self.assertIs(status[settings.CMC_status_elapsed],0)
        self.assertIs(status[settings.CMC_status_credit_count],0)

    @mock.patch('cmclogger.api.getlatest.Session.get')
    def test_custom_status_and_false_returned_if_timeout_error_occurs(self,session_mock):
        session_mock.side_effect = Timeout()

        success = self.api.getLatest();

        status = self.api.getLatestStatus()
        self.assertIs(success,False)
        self.assertIs(self.api.getLatestData(),None)
        self.assertIs(type(status[settings.CMC_status_timestamp]),str)
        self.assertIs(status[settings.CMC_status_error_code],4)
        self.assertIs(type(status[settings.CMC_status_error_message]),str)
        self.assertIs(status[settings.CMC_status_elapsed],0)
        self.assertIs(status[settings.CMC_status_credit_count],0)

    @mock.patch('cmclogger.api.getlatest.Session.get')
    def test_custom_status_and_false_returned_if_redirecty_error_occurs(self,session_mock):
        session_mock.side_effect = TooManyRedirects()

        success = self.api.getLatest();

        status = self.api.getLatestStatus()
        self.assertIs(success,False)
        self.assertIs(self.api.getLatestData(),None)
        self.assertIs(type(status[settings.CMC_status_timestamp]),str)
        self.assertIs(status[settings.CMC_status_error_code],5)
        self.assertIs(type(status[settings.CMC_status_error_message]),str)
        self.assertIs(status[settings.CMC_status_elapsed],0)
        self.assertIs(status[settings.CMC_status_credit_count],0)

    @mock.patch('cmclogger.api.getlatest.Session.get')
    def test_custom_status_and_false_returned_if_bad_status_keys_200(self,session_mock):
        mock_response = Response()
        mock_response.status_code = 200
        type(mock_response).text = mock.PropertyMock(return_value=json.dumps(response_200_bad_status_key))
        session_mock.return_value = mock_response

        success = self.api.getLatest();

        status = self.api.getLatestStatus()
        self.assertIs(success,False)
        self.assertIs(self.api.getLatestData(),None)
        self.assertIs(type(status[settings.CMC_status_timestamp]),str)
        self.assertIs(status[settings.CMC_status_error_code],6)
        self.assertIs(type(status[settings.CMC_status_error_message]),str)
        self.assertIs(status[settings.CMC_status_elapsed],0)
        self.assertIs(status[settings.CMC_status_credit_count],0)

    @mock.patch('cmclogger.api.getlatest.Session.get')
    def test_custom_status_and_false_returned_if_data_length_isnt_correct(self,session_mock):
        mock_response = Response()
        mock_response.status_code = 200
        type(mock_response).text = mock.PropertyMock(return_value=json.dumps(response_200_no_data))
        session_mock.return_value = mock_response

        success = self.api.getLatest();

        status = self.api.getLatestStatus()
        self.assertIs(success,False)
        self.assertIs(self.api.getLatestData(),None)
        self.assertIs(type(status[settings.CMC_status_timestamp]),str)
        self.assertIs(status[settings.CMC_status_error_code],8)
        self.assertIs(type(status[settings.CMC_status_error_message]),str)
        self.assertIs(status[settings.CMC_status_elapsed],0)
        self.assertIs(status[settings.CMC_status_credit_count],0)

    @mock.patch('cmclogger.api.getlatest.Session.get')
    def test_custom_status_and_false_returned_if_bad_status_keys_not_200(self,session_mock):
        mock_response = Response()
        mock_response.status_code = 403
        type(mock_response).text = mock.PropertyMock(return_value=json.dumps(response_200_bad_status_key))
        session_mock.return_value = mock_response

        success = self.api.getLatest();

        status = self.api.getLatestStatus()
        self.assertIs(success,False)
        self.assertIs(self.api.getLatestData(),None)
        self.assertIs(type(status[settings.CMC_status_timestamp]),str)
        self.assertIs(status[settings.CMC_status_error_code],6)
        self.assertIs(type(status[settings.CMC_status_error_message]),str)
        self.assertIs(status[settings.CMC_status_elapsed],0)
        self.assertIs(status[settings.CMC_status_credit_count],0)

    @mock.patch('cmclogger.api.getlatest.Session.get')
    def test_api_status_and_false_if_code_is_not_200(self,session_mock):
        mock_response = Response()
        mock_response.status_code = 401
        type(mock_response).text = mock.PropertyMock(return_value=json.dumps(response_status_401))
        session_mock.return_value = mock_response

        success = self.api.getLatest();

        status = self.api.getLatestStatus()
        self.assertIs(success,False)
        self.assertIs(self.api.getLatestData(),None)
        self.assertIs(type(status[settings.CMC_status_timestamp]),str)
        self.assertEqual(status[settings.CMC_status_error_code],1002)
        self.assertIs(type(status[settings.CMC_status_error_message]),str)
        self.assertIs(status[settings.CMC_status_elapsed],10)
        self.assertIs(status[settings.CMC_status_credit_count],0)

    @mock.patch('cmclogger.api.getlatest.Session.get')
    def test_false_and_custom_status_if_json_data_is_bad(self,session_mock):
        mock_response = Response()
        mock_response.status_code = 200
        type(mock_response).text = mock.PropertyMock(return_value=json.dumps(response_200_bad_data_key))
        session_mock.return_value = mock_response

        success = self.api.getLatest();

        status = self.api.getLatestStatus()
        self.assertIs(success,False)
        self.assertIs(self.api.getLatestData(),None)
        self.assertIs(type(status[settings.CMC_status_timestamp]),str)
        self.assertEqual(status[settings.CMC_status_error_code],7)
        self.assertIs(type(status[settings.CMC_status_error_message]),str)
        self.assertIs(status[settings.CMC_status_elapsed],0)
        self.assertIs(status[settings.CMC_status_credit_count],0)

    @mock.patch('cmclogger.api.getlatest.Session.get')
    def test_API_call_increments_next_call_time_based_on_configuration(self,session_mock):

        mock_response = Response()
        mock_response.status_code = 200
        type(mock_response).text = mock.PropertyMock(return_value=json.dumps(response_200))
        session_mock.return_value = mock_response

        callTime = int(datetime.datetime.now().timestamp())
        callMinutes = self.api.getConfiguration()['callInterval']
        nextCall = callTime + callMinutes * 60;
        remainingTime = nextCall - int(datetime.datetime.now().timestamp())
        success = self.api.getLatest();

        apiNextCall = self.api.secondsToNextAPICall()
        self.assertLessEqual(apiNextCall,remainingTime)
        self.assertGreaterEqual(apiNextCall,remainingTime - 2)

    def test_next_api_call_returns_0_if_no_request_ever_made(self):
        apiNextCall = self.api.secondsToNextAPICall()
        self.assertIs(apiNextCall,0)

if __name__ == '__main__':
    unittest.main();
