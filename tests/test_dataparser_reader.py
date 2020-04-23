import unittest
import logging
from io import StringIO
from cmclogger.dataparser.reader import Reader
import cmclogger.settings as settings
import json
import time
from cmclogger.cmclogger import CMCLogger
from dateutil import parser, tz

logging.disable(logging.CRITICAL)

requestFormat =  {
        settings.data_query_type     : 'price',      # price , status
        settings.data_query_tag      : 'BTC', # the tag, not valid for status
        settings.data_query_format   : "stdout",
        settings.data_query_detail   : "short",
        }

class CMCAPI_configuration_setting_and_checking(unittest.TestCase):

    def test_check(self):
        self.assertIs(False,False)

    def test_request_infomation_with_invalid_request_type(self):
        request = dict(requestFormat)
        request[settings.data_query_type] = "Invalid type",
        request[settings.data_query_tag] = "BTC"
        request[settings.data_query_format] = settings.data_query_format_stdout
        request[settings.data_query_detail] = settings.data_query_detail_short
        output = self.reader.processRequest(request)
        self.assertEqual("Request with type {} is not valid".format(request[settings.data_query_type]),output)

    def test_request_infomation_with_invalid_data_format(self):
        request = dict(requestFormat)
        request[settings.data_query_type] = settings.data_query_type_status
        request[settings.data_query_tag] = "BTC"
        request[settings.data_query_format] = "bad data format"
        request[settings.data_query_detail] = settings.data_query_detail_short
        output = self.reader.processRequest(request)
        self.assertEqual("Request with data format {} is not valid".format(request[settings.data_query_format]),output)

    def test_getting_the_status_short_version_stdout(self):
        request = dict(requestFormat)
        request[settings.data_query_type] = settings.data_query_type_status
        request[settings.data_query_tag] = "not used"
        request[settings.data_query_format] = settings.data_query_format_stdout
        request[settings.data_query_detail] = settings.data_query_detail_short
        output = self.reader.processRequest(request)
        currentTime = int(time.time())
        lastCall = int((parser.parse(self.reader.get_status_file().get_value(
            settings.status_file_last_call_section_name,
            settings.status_file_option_timeStamp)).astimezone(tz.tzlocal()).strftime('%s')))
        minutes = (currentTime - lastCall) / (60)
        self.assertEqual(output, "Last successful call {} minutes ago, health 80.0%.".format(int(minutes)))

    def test_getting_the_status_long_version_stdout(self):
        request = dict(requestFormat)
        request[settings.data_query_type] = settings.data_query_type_status
        request[settings.data_query_tag] = "not used"
        request[settings.data_query_format] = settings.data_query_format_stdout
        request[settings.data_query_detail] = settings.data_query_detail_long
        output = self.reader.processRequest(request)
        expected = StringIO()
        self.status.get_config_parser_object().write(expected)
        self.assertEqual(expected.getvalue(),output)

    def test_getting_the_status_short_version_json_bad_output_detail(self):
        request = dict(requestFormat)
        request[settings.data_query_type] = settings.data_query_type_status
        request[settings.data_query_tag] = "not used"
        request[settings.data_query_format] = settings.data_query_format_json
        request[settings.data_query_detail] = "invalid option"
        output = self.reader.processRequest(request)
        self.assertEqual("JSON status request with detail {} not valid".format(request[settings.data_query_detail]),output)

    def test_getting_the_status_short_version_json(self):
        request = dict(requestFormat)
        request[settings.data_query_type] = settings.data_query_type_status
        request[settings.data_query_tag] = "not used"
        request[settings.data_query_format] = settings.data_query_format_json
        request[settings.data_query_detail] = settings.data_query_detail_short
        output = self.reader.processRequest(request)
        currentTime = int(time.time())
        lastCall = int((parser.parse(self.reader.get_status_file().get_value(
            settings.status_file_last_call_section_name,
            settings.status_file_option_timeStamp)).astimezone(tz.tzlocal()).strftime('%s')))
        minutes = (currentTime - lastCall) / (60)
        expected = {
                settings.output_json_last_call  : int(minutes),
                settings.output_json_health     : 80.0
                }
        expectedJson = json.dumps(expected)
        self.assertEqual(expectedJson,output)

    def test_getting_the_status_long_version_json(self):
        request = dict(requestFormat)
        request[settings.data_query_type] = settings.data_query_type_status
        request[settings.data_query_tag] = "not used"
        request[settings.data_query_format] = settings.data_query_format_json
        request[settings.data_query_detail] = settings.data_query_detail_long
        output = self.reader.processRequest(request)
        expected = json.dumps(self.status.get_config_parser_object()._sections)
        self.assertEqual(expected,output)

    def test_getting_the_latest_price_single_tag_short_version_stdout(self):
        request = dict(requestFormat)
        request[settings.data_query_type] = settings.data_query_type_price
        request[settings.data_query_tag] = "BTC"
        request[settings.data_query_format] = settings.data_query_format_stdout
        request[settings.data_query_detail] = settings.data_query_detail_short
        output = self.reader.processRequest(request)
        self.assertEqual(output,"BTC: $10857.98 (-1.08%)")

    def test_getting_the_latest_price_single_tag_long_version_stdout(self):
        request = dict(requestFormat)
        request[settings.data_query_type] = settings.data_query_type_price
        request[settings.data_query_tag] = "BTC"
        request[settings.data_query_format] = settings.data_query_format_stdout
        request[settings.data_query_detail] = settings.data_query_detail_long
        output = self.reader.processRequest(request)
        self.assertEqual(output,"BTC: $10857.98 1H: -0.39% 1D: -1.08% 7D: -1.23% 24h Volume: 58.38 Billion")

    def test_getting_the_status_short_version_stdout_bad_output_detail(self):
        request = dict(requestFormat)
        request[settings.data_query_type] = settings.data_query_type_status
        request[settings.data_query_tag] = "not used"
        request[settings.data_query_format] = settings.data_query_format_stdout
        request[settings.data_query_detail] = "invalid option"
        output = self.reader.processRequest(request)
        self.assertEqual("STDOUT status request with detail {} not valid".format(request[settings.data_query_detail]),output)

    def test_getting_the_latest_price_single_tag_short_version_json(self):
        request = dict(requestFormat)
        request[settings.data_query_type] = settings.data_query_type_price
        request[settings.data_query_tag] = "BTC"
        request[settings.data_query_format] = settings.data_query_format_json
        request[settings.data_query_detail] = settings.data_query_detail_short
        output = self.reader.processRequest(request)
        outputDict = {
                settings.CMC_data_symbol : 'BTC',
                settings.CMC_data_quote_price : '$10857.98',
                settings.CMC_data_percent_change_24h : '-1.08%'
                }
        expectedOutput = str(json.dumps(outputDict))
        self.assertEqual(output,expectedOutput)

    def test_getting_the_latest_price_single_tag_long_version_json(self):
        request = dict(requestFormat)
        request[settings.data_query_type] = settings.data_query_type_price
        request[settings.data_query_tag] = "BTC"
        request[settings.data_query_format] = settings.data_query_format_json
        request[settings.data_query_detail] = settings.data_query_detail_long
        output = self.reader.processRequest(request)
        outputDict = {
                settings.CMC_data_symbol : 'BTC',
                settings.CMC_data_quote_price : '$10857.98',
                settings.CMC_data_percent_change_1h : '-0.39%',
                settings.CMC_data_percent_change_24h : '-1.08%',
                settings.CMC_data_percent_change_7d : '-1.23%',
                settings.CMC_data_quote_market_cap: '58.38 Billion'
                }
        expectedOutput = str(json.dumps(outputDict))
        self.assertEqual(output,expectedOutput)

    def test_query_not_existant_tag_recoves_with_simple_error_message(self):
        request = dict(requestFormat)
        request[settings.data_query_type] = settings.data_query_type_price
        request[settings.data_query_tag] = "invalid tag"
        request[settings.data_query_format] = settings.data_query_format_json
        request[settings.data_query_detail] = settings.data_query_detail_long
        output = self.reader.processRequest(request)
        expectedOutput = "{} not a valid stored cryptocurreny symbol.".format(request[settings.data_query_tag])
        self.assertEqual(output,expectedOutput)

    def test_query_not_existant_price_format_recoves_with_simple_error_message_long_detail(self):
        request = dict(requestFormat)
        request[settings.data_query_type] = settings.data_query_type_price
        request[settings.data_query_tag] = "BTC"
        request[settings.data_query_format] = "Unknown format again"
        request[settings.data_query_detail] = settings.data_query_detail_long
        output = self.reader.processRequest(request)
        expectedOutput = "{} is an invalid price request format".format(request[settings.data_query_format])
        self.assertEqual(output,expectedOutput)

    def test_query_not_existant_price_format_recoves_with_simple_error_message(self):
        request = dict(requestFormat)
        request[settings.data_query_type] = settings.data_query_type_price
        request[settings.data_query_tag] = "BTC"
        request[settings.data_query_format] = "Unknown format"
        request[settings.data_query_detail] = settings.data_query_detail_short
        output = self.reader.processRequest(request)
        expectedOutput = "{} is an invalid price request format".format(request[settings.data_query_format])
        self.assertEqual(output,expectedOutput)

    def test_query_not_existant_output_type_recoves_with_simple_error_message(self):
        request = dict(requestFormat)
        request[settings.data_query_type] = settings.data_query_type_price
        request[settings.data_query_tag] = "BTC"
        request[settings.data_query_format] = settings.data_query_format_json
        request[settings.data_query_detail] = "Unknown detail"
        output = self.reader.processRequest(request)
        expectedOutput = "{} is an invalid output detail request.".format(request[settings.data_query_detail])
        self.assertEqual(output,expectedOutput)

    def setUp(self):
        self.workingDirectory = 'tests/mockData'
        cmcLogger = CMCLogger(self.workingDirectory,logging.CRITICAL)
        self.status = cmcLogger.get_status_file()
        self.config = cmcLogger.get_config_file()
        self.database = cmcLogger.get_database()
        self.reader = Reader(self.status,self.database,self.config)

    def tearDown(self):
        pass
