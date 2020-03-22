import unittest
import logging
from modules.cmcapi_wrapper import CMCAPI_Wrapper
from modules.configChecker.configChecker import ConfigChecker
import settings

logging.disable(logging.CRITICAL)

class CMCAPI_wrapper_tests(unittest.TestCase):

    def setUp(self):
        self.config = ConfigChecker()
        self.config.setExpectation(
                settings.API_section_name,
                settings.API_option_private_key,
                str,
                settings.API_option_privatate_key_default)
        self.config.setExpectation(
                settings.
                API_section_name,
                settings.API_option_conversion_currency,
                str,
                settings.API_option_conversion_currency_default)
        self.config.setExpectation(
                settings.API_section_name,
                settings.API_option_start_index,
                int,
                settings.API_option_start_index_default)
        self.config.setExpectation(
                settings.API_section_name,
                settings.API_option_end_index,
                int,
                settings.API_option_end_index_default)
        self.config.setExpectation(
                settings.API_section_name,
                settings.API_option_interval,
                int,
                settings.API_option_interval_default)

        ## Setting an empty filename automatically loads the default values
        self.config.setConfigurationFile('');

        self.api = CMCAPI_Wrapper(self.config)

    def test_configuration_is_saved_correctly(self):
        apiConfig = self.api.getConfiguration()
        self.assertIs(apiConfig['privateKey'],settings.API_option_privatate_key_default)
        self.assertIs(apiConfig['conversionCurrency'],settings.API_option_conversion_currency_default)
        self.assertIs(apiConfig['startIndex'],settings.API_option_start_index_default)
        self.assertIs(apiConfig['endIndex'],settings.API_option_end_index_default)
        self.assertIs(apiConfig['callInterval'],settings.API_option_interval_default)

    def test_configuration_start_index_cant_be_less_than_one(self):
        self.config.setValue(settings.API_section_name,settings.API_option_start_index,-1)
        self.api = CMCAPI_Wrapper(self.config)
        apiConfig = self.api.getConfiguration()
        self.assertIs(apiConfig['startIndex'],settings.API_option_start_index_default)

    def test_configuration_end_index_cant_be_less_than_start_index(self):
        self.config.setValue(settings.API_section_name,settings.API_option_start_index,10)
        self.config.setValue(settings.API_section_name,settings.API_option_end_index,1)
        self.api = CMCAPI_Wrapper(self.config)
        apiConfig = self.api.getConfiguration()
        self.assertIs(apiConfig['endIndex'],11)

    def test_configuration_start_index_cant_be_greater_than_4999(self):
        self.config.setValue(settings.API_section_name,settings.API_option_start_index,5000)
        self.api = CMCAPI_Wrapper(self.config)
        apiConfig = self.api.getConfiguration()
        self.assertIs(apiConfig['startIndex'],settings.API_option_start_index_default)

    def test_configuration_call_interval_must_be_greater_than_zero(self):
        self.config.setValue(settings.API_section_name,settings.API_option_interval,0)
        self.api = CMCAPI_Wrapper(self.config)
        apiConfig = self.api.getConfiguration()
        self.assertIs(apiConfig['callInterval'],settings.API_option_interval_default)

    def test_configuration_conversion_currency_must_be_of_allowed_type(self):
        self.config.setValue(settings.API_section_name,settings.API_option_conversion_currency,'asdf')
        self.api = CMCAPI_Wrapper(self.config)
        apiConfig = self.api.getConfiguration()
        self.assertIs(apiConfig['conversionCurrency'],settings.API_option_conversion_currency_default)

    def test_configuration_api_key_cannot_be_blank(self):
        self.config.setValue(settings.API_section_name,settings.API_option_private_key,'')
        self.api = CMCAPI_Wrapper(self.config)
        apiConfig = self.api.getConfiguration()
        self.assertIs(apiConfig['privateKey'],settings.API_option_privatate_key_default)






if __name__ == '__main__':
    unittest.main();
