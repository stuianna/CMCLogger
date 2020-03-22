import logging
from modules.configChecker.configChecker import ConfigChecker
import os
import settings

log = logging.getLogger(__name__)

allowedCurrencies = [
        'USD','ALL','DZD','ARS','AMD','AUD','AZN','BHD','BDT','BYN','BMD','BOB','BAM','BRL','BGN','KHR','CAD','CLP',
        'CNY','COP','CRC','HRK','CUP','CZK','DKK','DOP','EGP','EUR','GEL','GHS','GTQ','HNL','HKD','HUF','ISK','INR',
        'IDR','IRR','IQD','ILS','JMD','JPY','JOD','KZT','KES','KWD','KGS','LBP','MKD','MYR','MUR','MXN','MDL','MNT',
        'MAD','MMK','NAD','NPR','TWD','NZD','NIO','NGN','NOK','OMR','PKR','PAB','PEN','PHP','PLN','GBP','QAR','RON',
        'RUB','SAR','RSD','SGD','ZAR','KRW','SSP','VES','LKR','SEK','CHF','THB','TTD','TND','TRY','UGX','UAH','AED',
        'UYU','UZS','VND']

class CMCAPI_Wrapper():

    def __init__(self,config):
        self.__configuration = {
                'privateKey' : config.getValue(settings.API_section_name,settings.API_option_private_key),
                'conversionCurrency' : config.getValue(settings.API_section_name,settings.API_option_conversion_currency),
                'startIndex' : config.getValue(settings.API_section_name,settings.API_option_start_index),
                'endIndex' : config.getValue(settings.API_section_name,settings.API_option_end_index),
                'callInterval' : config.getValue(settings.API_section_name,settings.API_option_interval)
                }
        self.__checkConfigurationValues()

    def __checkConfigurationValues(self):
        if self.__configuration['startIndex'] < 1 or self.__configuration['startIndex'] > 4999:
            logging.warning('Start index cannot be less than one or great than 4999, using default value of {}'.format(
                settings.API_option_start_index_default))
            self.__configuration['startIndex'] = settings.API_option_start_index_default

        if self.__configuration['endIndex'] <= self.__configuration['startIndex']:
            logging.warning('End index cannot be less than start index, using start index + 1')
            self.__configuration['endIndex'] = self.__configuration['startIndex'] + 1

        if self.__configuration['callInterval'] <= 0:
            logging.warning('API call interval cannot be less than 0, using default value of {}'.format(
                settings.API_option_interval_default))
            self.__configuration['callInterval'] = settings.API_option_interval_default

        if self.__configuration['conversionCurrency'] not in allowedCurrencies:
            logging.warning("Conversion currancy '{}' not valid, using default of {}".format(
                self.__configuration['conversionCurrency'],settings.API_option_conversion_currency_default))
            self.__configuration['conversionCurrency'] = settings.API_option_conversion_currency_default

        if self.__configuration['privateKey'] == '':
            logging.warning("API private key cannot be empty, using default value")
            self.__configuration['privateKey'] = settings.API_option_privatate_key_default


    # Get configuration
    def getConfiguration(self):
        return self.__configuration;

    # Get lastest -> Return json

    # Get status -> Return last call status (dictionary)

    # Get delay to next API call (seconds)
