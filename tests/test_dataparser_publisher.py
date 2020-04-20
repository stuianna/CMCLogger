import unittest
import logging
from cmclogger.dataparser.publisher import Publisher
import cmclogger.settings as settings
from cmclogger.cmclogger import CMCLogger
import os
logging.disable(logging.CRITICAL)

badData = [{ # Has missing entry
    "circulating_supply": 4642367414,
    "cmc_rank": 4,
    "date_added": "2015-02-25T00:00:00.000Z",
    "last_updated": "2020-03-25T19:28:25.000Z",
    "max_supply": 'null',
    "name": "Tether",
    "num_market_pairs": 4239,
    "platform": {
      "id": 83,
      "name": "Omni",
      "slug": "omni",
      "symbol": "OMNI",
      "token_address": "31"
    },
    "quote": {
      "AUD": {
        "last_updated": "2020-03-25T19:28:00.000Z",
        "market_cap": 7812270864.97417,
        "percent_change_1h": 0.05824603,
        "percent_change_24h": -0.54021238,
        "percent_change_7d": -1.03829609,
        "price": 1.6828204595385283,
        "volume_24h": 89513788903.59727
      }
    },
    "slug": "tether",
    "symbol": "USDT",
    "tags": [],
    "total_supply": 4776930644
  }
]

goodData = [{
    "circulating_supply": 4642367414,
    "cmc_rank": 4,
    "date_added": "2015-02-25T00:00:00.000Z",
    "id": 825,
    "last_updated": "2020-03-25T19:28:25.000Z",
    "max_supply": 'null',
    "name": "Tether",
    "num_market_pairs": 4239,
    "platform": {
      "id": 83,
      "name": "Omni",
      "slug": "omni",
      "symbol": "OMNI",
      "token_address": "31"
    },
    "quote": {
      "AUD": {
        "last_updated": "2020-03-25T19:28:00.000Z",
        "market_cap": 7812270864.97417,
        "percent_change_1h": 0.05824603,
        "percent_change_24h": -0.54021238,
        "percent_change_7d": -1.03829609,
        "price": 1.6828204595385283,
        "volume_24h": 89513788903.59727
      }
    },
    "slug": "tether",
    "symbol": "USDT",
    "tags": [],
    "total_supply": 4776930644
  },
  {
    "circulating_supply": 18350387.5,
    "cmc_rank": 5,
    "date_added": "2017-07-23T00:00:00.000Z",
    "id": 1831,
    "last_updated": "2020-03-25T19:28:07.000Z",
    "max_supply": 21000000,
    "name": "Bitcoin Cash",
    "num_market_pairs": 457,
    "platform": 'null',
    "quote": {
      "AUD": {
        "last_updated": "2020-03-25T19:28:00.000Z",
        "market_cap": 6768058516.560338,
        "percent_change_1h": 0.13321202,
        "percent_change_24h": -2.96056717,
        "percent_change_7d": 20.29887496,
        "price": 368.823738275845,
        "volume_24h": 5791425128.458918
      }
    },
    "slug": "bitcoin-cash",
    "symbol": "BCH",
    "tags": [
      "Mineable"
    ],
    "total_supply": 18350387.5
  }
]

goodStatus = {
  "credit_count": 1,
  "elapsed": 11,
  "error_code": 0,
  "error_message": 'null',
  "notice": 'null',
  "timestamp": "2020-03-24T18:28:37.355Z"
}

badStatus = {
  "credit_count": 0,
  "elapsed": 11,
  "error_code": 3,
  "error_message": 'null',
  "notice": 'null',
  "timestamp": "2020-03-24T18:28:37.355Z"
}

class CMCAPI_configuration_setting_and_checking(unittest.TestCase):

    def setUp(self):
        self.workingDirectory = 'tests'
        cmcLogger = CMCLogger(self.workingDirectory,logging.CRITICAL)
        self.status = cmcLogger.get_status_file()
        #self.status = ConfigChecker()
        #makeDirectoriesAsNeeded(self.workingDirectory)
        #setStatusFileOptions(self.status,self.workingDirectory)

    def test_all_time_successful_calls_cannot_be_less_than_zero_reset_global_status(self):
        self.status.set_value(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls,-1)
        publisher = Publisher(self.status,None);
        self.assertIs(publisher.getStatus().get_value(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls),0)
        self.assertIs(publisher.getStatus().get_value(settings.status_file_all_time_section_name,settings.status_file_option_failed_calls),0)
        self.assertEqual(publisher.getStatus().get_value(settings.status_file_all_time_section_name,settings.status_file_option_success_rate),100.0)

    def test_all_time_failed_calls_cannot_be_less_than_zero_reset_global_status(self):
        self.status.set_value(settings.status_file_all_time_section_name,settings.status_file_option_failed_calls,-1)
        publisher = Publisher(self.status,None);
        self.assertIs(publisher.getStatus().get_value(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls),0)
        self.assertIs(publisher.getStatus().get_value(settings.status_file_all_time_section_name,settings.status_file_option_failed_calls),0)
        self.assertEqual(publisher.getStatus().get_value(settings.status_file_all_time_section_name,settings.status_file_option_success_rate),100.0)

    def test_all_time_success_cannot_be_less_than_zero_reset_global_status(self):
        self.status.set_value(settings.status_file_all_time_section_name,settings.status_file_option_success_rate,-0.01)
        publisher = Publisher(self.status,None);
        self.assertIs(publisher.getStatus().get_value(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls),0)
        self.assertIs(publisher.getStatus().get_value(settings.status_file_all_time_section_name,settings.status_file_option_failed_calls),0)
        self.assertEqual(publisher.getStatus().get_value(settings.status_file_all_time_section_name,settings.status_file_option_success_rate),100.0)

    def test_all_time_success_cannot_be_more_than_100_reset_global_status(self):
        self.status.set_value(settings.status_file_all_time_section_name,settings.status_file_option_success_rate,100.01)
        publisher = Publisher(self.status,None);
        self.assertIs(publisher.getStatus().get_value(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls),0)
        self.assertIs(publisher.getStatus().get_value(settings.status_file_all_time_section_name,settings.status_file_option_failed_calls),0)
        self.assertEqual(publisher.getStatus().get_value(settings.status_file_all_time_section_name,settings.status_file_option_success_rate),100.0)

    def tearDown(self):
        try:
            os.remove(os.path.join(self.workingDirectory,settings.status_file_directory,settings.status_file_name))
            os.removedirs(os.path.join(self.workingDirectory,settings.status_file_directory))
        except:
            pass

class CMCAPI_writing_status_files(unittest.TestCase):

    def setUp(self):
        self.workingDirectory = 'tests'
        cmcLogger = CMCLogger(self.workingDirectory,logging.CRITICAL)
        self.status = cmcLogger.get_status_file()
        self.publisher = Publisher(self.status,None);

    def tearDown(self):
        try:
            os.remove(os.path.join(self.workingDirectory,settings.status_file_directory,settings.status_file_name))
            os.removedirs(os.path.join(self.workingDirectory,settings.status_file_directory))
        except:
            pass

    def test_good_status_updates_last_call_timestamp(self):
        self.publisher.writeStatus(goodStatus)
        savedValue =  self.publisher.getStatus().get_value(settings.status_file_last_call_section_name,settings.status_file_option_timeStamp)
        expectedValue = self.publisher.toLocalTime(goodStatus[settings.CMC_status_timestamp])
        self.assertEqual(savedValue,expectedValue)

    def test_good_status_updates_last_call_error_code(self):
        self.publisher.writeStatus(goodStatus)
        savedValue =  self.publisher.getStatus().get_value(settings.status_file_last_call_section_name,settings.status_file_option_error_code)
        expectedValue = goodStatus[settings.CMC_status_error_code]
        self.assertIs(savedValue,expectedValue)

    def test_good_status_updates_last_call_error_message(self):
        self.publisher.writeStatus(goodStatus)
        savedValue =  self.publisher.getStatus().get_value(settings.status_file_last_call_section_name,settings.status_file_option_error_message)
        expectedValue = goodStatus[settings.CMC_status_error_message]
        self.assertIs(savedValue,expectedValue)

    def test_good_status_updates_last_call_elapsed(self):
        self.publisher.writeStatus(goodStatus)
        savedValue =  self.publisher.getStatus().get_value(settings.status_file_last_call_section_name,settings.status_file_option_elapsed)
        expectedValue = goodStatus[settings.CMC_status_elapsed]
        self.assertIs(savedValue,expectedValue)

    def test_good_status_updates_credits(self):
        self.publisher.writeStatus(goodStatus)
        savedValue =  self.publisher.getStatus().get_value(settings.status_file_last_call_section_name,settings.status_file_option_credit_count)
        expectedValue = goodStatus[settings.CMC_status_credit_count]
        self.assertIs(savedValue,expectedValue)

    def test_bad_status_updates_last_call_timestamp(self):
        self.publisher.writeStatus(badStatus)
        savedValue =  self.publisher.getStatus().get_value(settings.status_file_last_failed_secion_name,settings.status_file_option_timeStamp)
        expectedValue = self.publisher.toLocalTime(badStatus[settings.CMC_status_timestamp])
        self.assertEqual(savedValue,expectedValue)

    def test_bad_status_updates_last_call_error_code(self):
        self.publisher.writeStatus(badStatus)
        savedValue = self.publisher.getStatus().get_value(settings.status_file_last_failed_secion_name,settings.status_file_option_error_code)
        expectedValue = badStatus[settings.CMC_status_error_code]
        self.assertIs(savedValue,expectedValue)

    def test_bad_status_updates_last_call_error_message(self):
        self.publisher.writeStatus(badStatus)
        savedValue =  self.publisher.getStatus().get_value(settings.status_file_last_failed_secion_name,settings.status_file_option_error_message)
        expectedValue = badStatus[settings.CMC_status_error_message]
        self.assertIs(savedValue,expectedValue)

    def test_bad_status_updates_last_call_elapsed(self):
        self.publisher.writeStatus(badStatus)
        savedValue =  self.publisher.getStatus().get_value(settings.status_file_last_failed_secion_name,settings.status_file_option_elapsed)
        expectedValue = badStatus[settings.CMC_status_elapsed]
        self.assertIs(savedValue,expectedValue)

    def test_bad_status_updates_credits(self):
        self.publisher.writeStatus(badStatus)
        savedValue =  self.publisher.getStatus().get_value(settings.status_file_last_failed_secion_name,settings.status_file_option_credit_count)
        expectedValue = badStatus[settings.CMC_status_credit_count]
        self.assertIs(savedValue,expectedValue)

    def test_good_status_updates_successful_calls_current(self):
        expectedValueGood = self.publisher.getStatus().get_value(settings.status_file_current_session_section_name,settings.status_file_option_successful_calls) + 1
        self.publisher.writeStatus(goodStatus)
        newValueGood =  self.publisher.getStatus().get_value(settings.status_file_current_session_section_name,settings.status_file_option_successful_calls)
        self.assertIs(newValueGood,expectedValueGood)

    def test_good_status_updates_successful_calls_all_time(self):
        expectedValueGood = self.publisher.getStatus().get_value(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls) + 1
        self.publisher.writeStatus(goodStatus)
        newValueGood =  self.publisher.getStatus().get_value(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls)
        self.assertIs(newValueGood,expectedValueGood)

    def test_two_good_status_updates_successful_calls_all_time(self):
        expectedValueGood = self.publisher.getStatus().get_value(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls) + 2
        self.publisher.writeStatus(goodStatus)
        self.publisher.writeStatus(goodStatus)
        newValueGood =  self.publisher.getStatus().get_value(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls)
        self.assertIs(newValueGood,expectedValueGood)

    def test_two_good_status_updates_successful_calls_current(self):
        expectedValueGood = self.publisher.getStatus().get_value(settings.status_file_current_session_section_name,settings.status_file_option_successful_calls) + 2
        expectedValueBad = self.publisher.getStatus().get_value(settings.status_file_current_session_section_name,settings.status_file_option_failed_calls)
        self.publisher.writeStatus(goodStatus)
        self.publisher.writeStatus(goodStatus)
        newValueGood =  self.publisher.getStatus().get_value(settings.status_file_current_session_section_name,settings.status_file_option_successful_calls)
        newValueBad = self.publisher.getStatus().get_value(settings.status_file_current_session_section_name,settings.status_file_option_failed_calls)
        self.assertIs(newValueGood,expectedValueGood)
        self.assertIs(newValueBad,expectedValueBad)

    def test_two_bad_status_updates_failed_calls_current_only(self):
        expectedValueGood = self.publisher.getStatus().get_value(settings.status_file_current_session_section_name,settings.status_file_option_successful_calls)
        expectedValueBad = self.publisher.getStatus().get_value(settings.status_file_current_session_section_name,settings.status_file_option_failed_calls) + 2
        self.publisher.writeStatus(badStatus)
        self.publisher.writeStatus(badStatus)
        newValueGood =  self.publisher.getStatus().get_value(settings.status_file_current_session_section_name,settings.status_file_option_successful_calls)
        newValueBad = self.publisher.getStatus().get_value(settings.status_file_current_session_section_name,settings.status_file_option_failed_calls)
        self.assertIs(newValueGood,expectedValueGood)
        self.assertIs(newValueBad,expectedValueBad)

    def test_current_session_status_updated_for_good_calls(self):
        self.publisher.writeStatus(badStatus)
        self.publisher.writeStatus(goodStatus)
        self.publisher.writeStatus(goodStatus)
        actualValue = self.publisher.getStatus().get_value(settings.status_file_current_session_section_name,settings.status_file_option_success_rate)
        self.assertEqual(actualValue,66.67)

    def test_current_session_status_updated_for_good_calls(self):
        self.publisher.writeStatus(badStatus)
        self.publisher.writeStatus(badStatus)
        self.publisher.writeStatus(goodStatus)
        actualValue = self.publisher.getStatus().get_value(settings.status_file_all_time_section_name,settings.status_file_option_success_rate)
        self.assertEqual(actualValue,33.33)

class CMCAPI_configuration_writeing_output_data(unittest.TestCase):

    def setUp(self):
        self.workingDirectory = 'tests'
        cmcLogger = CMCLogger(self.workingDirectory,logging.CRITICAL)
        self.status = cmcLogger.get_status_file()
        self.database = cmcLogger.get_database()
        self.publisher = Publisher(self.status,self.database);

    def test_database_file_is_not_created_with_no_permissions(self):
        self.workingDirectory = '/'
        try:
            cmcLogger = CMCLogger(self.workingDirectory,logging.CRITICAL)
            created = True
        except:
            created = False
        self.assertIs(created,False)

    def test_database_is_created_if_not_exist_at_runtime(self):
        os.remove(os.path.join(self.workingDirectory,settings.data_file_directory,settings.database_file_name))
        exists = self.database.exists()
        self.assertIs(exists,False)
        self.publisher.writeData(goodData)
        exists = self.database.exists()
        self.assertIs(exists,True)

    def test_database_can_pass_none_object_without_errors(self):
        self.publisher.writeData(None)

    def test_database_creates_tabels_as_needed(self):
        self.publisher.writeData(goodData)
        tables = self.database.get_table_names()
        columns = self.database.get_column_names('BCH')
        self.assertIs(len(tables),2)
        self.assertIn('BCH',tables)
        self.assertIn('USDT',tables)
        self.assertIs(len(columns),18)

    def test_database_entry_added_successfully(self):
        self.publisher.writeData(goodData)
        lastEntry = self.database.get_last_time_entry('BCH')
        columns = self.database.get_column_names('BCH')
        self.assertEqual(lastEntry[settings.CMC_data_circulating_suuply],18350387.5)
        self.assertEqual(lastEntry[settings.CMC_data_cmc_rank],5)
        self.assertEqual(lastEntry[settings.CMC_data_name],'Bitcoin Cash')
        self.assertEqual(lastEntry[settings.CMC_data_num_market_pairs],457)
        self.assertEqual(lastEntry[settings.CMC_data_symbol],'BCH')


    def test_multiple_good_entries_are_written(self):
        self.publisher.writeData(goodData)
        self.publisher.writeData(goodData)
        df = self.database.table_to_df('USDT')
        self.assertIs(len(df), 2)

    def test_bad_data_results_in_no_entry_being_written(self):
        self.publisher.writeData(badData)
        df = self.database.table_to_df('USDT')
        self.assertIs(len(df), 0)

    def tearDown(self):
        try:
            os.remove(os.path.join(self.workingDirectory,settings.status_file_directory,settings.status_file_name))
            os.remove(os.path.join(self.workingDirectory,settings.data_file_directory,settings.database_file_name))
            os.removedirs(os.path.join(self.workingDirectory,settings.status_file_directory))
        except:
            pass

if __name__ == '__main__':
    unittest.main();
