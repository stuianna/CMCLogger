import unittest
from unittest import mock
import logging
from modules.data_publisher import DataPublisher
from modules.configChecker.configChecker import ConfigChecker
import settings
import json
import datetime
import time
import os
logging.disable(logging.CRITICAL)
from CMCLogger import setStatusFileOptions, makeDirectoriesAsNeeded

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
        self.status = ConfigChecker()
        makeDirectoriesAsNeeded(self.workingDirectory)
        setStatusFileOptions(self.status,self.workingDirectory)

    def test_all_time_successful_calls_cannot_be_less_than_zero_reset_global_status(self):
        self.status.setValue(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls,-1)
        publisher = DataPublisher(self.status);
        self.assertIs(publisher.getStatus().getValue(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls),0)
        self.assertIs(publisher.getStatus().getValue(settings.status_file_all_time_section_name,settings.status_file_option_failed_calls),0)
        self.assertEqual(publisher.getStatus().getValue(settings.status_file_all_time_section_name,settings.status_file_option_success_rate),100.0)

    def test_all_time_failed_calls_cannot_be_less_than_zero_reset_global_status(self):
        self.status.setValue(settings.status_file_all_time_section_name,settings.status_file_option_failed_calls,-1)
        publisher = DataPublisher(self.status);
        self.assertIs(publisher.getStatus().getValue(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls),0)
        self.assertIs(publisher.getStatus().getValue(settings.status_file_all_time_section_name,settings.status_file_option_failed_calls),0)
        self.assertEqual(publisher.getStatus().getValue(settings.status_file_all_time_section_name,settings.status_file_option_success_rate),100.0)

    def test_all_time_success_cannot_be_less_than_zero_reset_global_status(self):
        self.status.setValue(settings.status_file_all_time_section_name,settings.status_file_option_success_rate,-0.01)
        publisher = DataPublisher(self.status);
        self.assertIs(publisher.getStatus().getValue(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls),0)
        self.assertIs(publisher.getStatus().getValue(settings.status_file_all_time_section_name,settings.status_file_option_failed_calls),0)
        self.assertEqual(publisher.getStatus().getValue(settings.status_file_all_time_section_name,settings.status_file_option_success_rate),100.0)

    def test_all_time_success_cannot_be_more_than_100_reset_global_status(self):
        self.status.setValue(settings.status_file_all_time_section_name,settings.status_file_option_success_rate,100.01)
        publisher = DataPublisher(self.status);
        self.assertIs(publisher.getStatus().getValue(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls),0)
        self.assertIs(publisher.getStatus().getValue(settings.status_file_all_time_section_name,settings.status_file_option_failed_calls),0)
        self.assertEqual(publisher.getStatus().getValue(settings.status_file_all_time_section_name,settings.status_file_option_success_rate),100.0)

    def tearDown(self):
        try:
            os.remove(os.path.join(self.workingDirectory,settings.status_file_directory,settings.status_file_name))
            os.removedirs(os.path.join(self.workingDirectory,settings.status_file_directory))
        except:
            pass

class CMCAPI_writing_status_files(unittest.TestCase):

    def setUp(self):
        self.workingDirectory = 'tests'
        self.status = ConfigChecker()
        makeDirectoriesAsNeeded(self.workingDirectory)
        setStatusFileOptions(self.status,self.workingDirectory)
        self.publisher = DataPublisher(self.status);

    def tearDown(self):
        try:
            os.remove(os.path.join(self.workingDirectory,settings.status_file_directory,settings.status_file_name))
            os.removedirs(os.path.join(self.workingDirectory,settings.status_file_directory))
        except:
            pass

    def test_good_status_updates_last_call_timestamp(self):
        self.publisher.writeStatus(goodStatus)
        savedValue =  self.publisher.getStatus().getValue(settings.status_file_last_call_section_name,settings.status_file_option_timeStamp)
        expectedValue = goodStatus[settings.CMC_status_timestamp]
        self.assertIs(savedValue,expectedValue)

    def test_good_status_updates_last_call_error_code(self):
        self.publisher.writeStatus(goodStatus)
        savedValue =  self.publisher.getStatus().getValue(settings.status_file_last_call_section_name,settings.status_file_option_error_code)
        expectedValue = goodStatus[settings.CMC_status_error_code]
        self.assertIs(savedValue,expectedValue)

    def test_good_status_updates_last_call_error_code(self):
        self.publisher.writeStatus(goodStatus)
        savedValue = self.publisher.getStatus().getValue(settings.status_file_last_call_section_name,settings.status_file_option_error_code)
        expectedValue = goodStatus[settings.CMC_status_error_code]
        self.assertIs(savedValue,expectedValue)

    def test_good_status_updates_last_call_error_message(self):
        self.publisher.writeStatus(goodStatus)
        savedValue =  self.publisher.getStatus().getValue(settings.status_file_last_call_section_name,settings.status_file_option_error_message)
        expectedValue = goodStatus[settings.CMC_status_error_message]
        self.assertIs(savedValue,expectedValue)

    def test_good_status_updates_last_call_elapsed(self):
        self.publisher.writeStatus(goodStatus)
        savedValue =  self.publisher.getStatus().getValue(settings.status_file_last_call_section_name,settings.status_file_option_elapsed)
        expectedValue = goodStatus[settings.CMC_status_elapsed]
        self.assertIs(savedValue,expectedValue)

    def test_good_status_updates_credits(self):
        self.publisher.writeStatus(goodStatus)
        savedValue =  self.publisher.getStatus().getValue(settings.status_file_last_call_section_name,settings.status_file_option_credit_count)
        expectedValue = goodStatus[settings.CMC_status_credit_count]
        self.assertIs(savedValue,expectedValue)

    def test_good_status_updates_successful_calls_current(self):
        expectedValueGood = self.publisher.getStatus().getValue(settings.status_file_current_session_section_name,settings.status_file_option_successful_calls) + 1
        self.publisher.writeStatus(goodStatus)
        newValueGood =  self.publisher.getStatus().getValue(settings.status_file_current_session_section_name,settings.status_file_option_successful_calls)
        self.assertIs(newValueGood,expectedValueGood)

    def test_good_status_updates_successful_calls_all_time(self):
        expectedValueGood = self.publisher.getStatus().getValue(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls) + 1
        self.publisher.writeStatus(goodStatus)
        newValueGood =  self.publisher.getStatus().getValue(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls)
        self.assertIs(newValueGood,expectedValueGood)

    def test_two_good_status_updates_successful_calls_all_time(self):
        expectedValueGood = self.publisher.getStatus().getValue(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls) + 2
        self.publisher.writeStatus(goodStatus)
        self.publisher.writeStatus(goodStatus)
        newValueGood =  self.publisher.getStatus().getValue(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls)
        self.assertIs(newValueGood,expectedValueGood)

    def test_two_good_status_updates_successful_calls_current(self):
        expectedValueGood = self.publisher.getStatus().getValue(settings.status_file_current_session_section_name,settings.status_file_option_successful_calls) + 2
        expectedValueBad = self.publisher.getStatus().getValue(settings.status_file_current_session_section_name,settings.status_file_option_failed_calls)
        self.publisher.writeStatus(goodStatus)
        self.publisher.writeStatus(goodStatus)
        newValueGood =  self.publisher.getStatus().getValue(settings.status_file_current_session_section_name,settings.status_file_option_successful_calls)
        newValueBad = self.publisher.getStatus().getValue(settings.status_file_current_session_section_name,settings.status_file_option_failed_calls)
        self.assertIs(newValueGood,expectedValueGood)
        self.assertIs(newValueBad,expectedValueBad)

    def test_two_bad_status_updates_failed_calls_current_only(self):
        expectedValueGood = self.publisher.getStatus().getValue(settings.status_file_current_session_section_name,settings.status_file_option_successful_calls)
        expectedValueBad = self.publisher.getStatus().getValue(settings.status_file_current_session_section_name,settings.status_file_option_failed_calls) + 2
        self.publisher.writeStatus(badStatus)
        self.publisher.writeStatus(badStatus)
        newValueGood =  self.publisher.getStatus().getValue(settings.status_file_current_session_section_name,settings.status_file_option_successful_calls)
        newValueBad = self.publisher.getStatus().getValue(settings.status_file_current_session_section_name,settings.status_file_option_failed_calls)
        self.assertIs(newValueGood,expectedValueGood)
        self.assertIs(newValueBad,expectedValueBad)

    def test_current_session_status_updated_for_good_calls(self):
        self.publisher.writeStatus(badStatus)
        self.publisher.writeStatus(goodStatus)
        self.publisher.writeStatus(goodStatus)
        actualValue = self.publisher.getStatus().getValue(settings.status_file_current_session_section_name,settings.status_file_option_success_rate)
        self.assertEqual(actualValue,66.67)

    def test_current_session_status_updated_for_good_calls(self):
        self.publisher.writeStatus(badStatus)
        self.publisher.writeStatus(badStatus)
        self.publisher.writeStatus(goodStatus)
        actualValue = self.publisher.getStatus().getValue(settings.status_file_all_time_section_name,settings.status_file_option_success_rate)
        self.assertEqual(actualValue,33.33)


if __name__ == '__main__':
    unittest.main();
