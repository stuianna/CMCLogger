import logging
import cmclogger.settings as settings
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import datetime
import time

log = logging.getLogger(__name__)

allowedCurrencies = [
        'USD','ALL','DZD','ARS','AMD','AUD','AZN','BHD','BDT','BYN','BMD','BOB','BAM','BRL','BGN','KHR','CAD','CLP',
        'CNY','COP','CRC','HRK','CUP','CZK','DKK','DOP','EGP','EUR','GEL','GHS','GTQ','HNL','HKD','HUF','ISK','INR',
        'IDR','IRR','IQD','ILS','JMD','JPY','JOD','KZT','KES','KWD','KGS','LBP','MKD','MYR','MUR','MXN','MDL','MNT',
        'MAD','MMK','NAD','NPR','TWD','NZD','NIO','NGN','NOK','OMR','PKR','PAB','PEN','PHP','PLN','GBP','QAR','RON',
        'RUB','SAR','RSD','SGD','ZAR','KRW','SSP','VES','LKR','SEK','CHF','THB','TTD','TND','TRY','UGX','UAH','AED',
        'UYU','UZS','VND']

class CMCGetLatest():

    def __init__(self,config):
        self.__configuration = {
                'privateKey' : config.get_value(settings.API_section_name,settings.API_option_private_key),
                'conversionCurrency' : config.get_value(settings.API_section_name,settings.API_option_conversion_currency),
                'startIndex' : config.get_value(settings.API_section_name,settings.API_option_start_index),
                'endIndex' : config.get_value(settings.API_section_name,settings.API_option_end_index),
                'callInterval' : config.get_value(settings.API_section_name,settings.API_option_interval)
                }
        self.__checkConfigurationValues()
        log.debug("API wrapper initialised with confg '{}'".format(str(self.__configuration)))
        self.__getLatestSession = Session()
        self.__configureGetLatestSession()
        self.__getLatestData = None
        self.__getLatestStatus = None
        self.__lastCallTimestamp = None;

    def getLatestStatus(self):
        return self.__getLatestStatus

    def getLatestData(self):
        return self.__getLatestData

    def __configureGetLatestSession(self,apiKey = None):
        getLatestHeaders = settings.getLatest_Headers
        if apiKey is None:
            getLatestHeaders['X-CMC_PRO_API_KEY'] = self.__configuration['privateKey']
        else:
            getLatestHeaders['X-CMC_PRO_API_KEY'] = apiKey
        self.__getLatestSession.headers.update(getLatestHeaders)
        log.debug("Setting getLatest session headers to {}".format(getLatestHeaders))

    def __checkConfigurationValues(self):
        if self.__configuration['startIndex'] < 1 or self.__configuration['startIndex'] > 4999:
            log.warning('Start index cannot be less than one or great than 4999, using default value of {}'.format(
                settings.API_option_start_index_default))
            self.__configuration['startIndex'] = settings.API_option_start_index_default

        if self.__configuration['endIndex'] < self.__configuration['startIndex']:
            log.warning('End index cannot be less than start index, using start index')
            self.__configuration['endIndex'] = self.__configuration['startIndex']

        if self.__configuration['callInterval'] <= 0:
            log.warning('API call interval cannot be less than 0, using default value of {}'.format(
                settings.API_option_interval_default))
            self.__configuration['callInterval'] = settings.API_option_interval_default

        if self.__configuration['conversionCurrency'] not in allowedCurrencies:
            log.warning("Conversion currancy '{}' not valid, using default of {}".format(
                self.__configuration['conversionCurrency'],settings.API_option_conversion_currency_default))
            self.__configuration['conversionCurrency'] = settings.API_option_conversion_currency_default

        if self.__configuration['privateKey'] == '':
            log.warning("API private key cannot be empty, using default value")
            self.__configuration['privateKey'] = settings.API_option_privatate_key_default

    def getConfiguration(self):
        return self.__configuration;

    def getLatest(self,apiKey = None):

        if apiKey is not None:
            self.__configureGetLatestSession(apiKey)

        self.__lastCallTimestamp = int(datetime.datetime.now().timestamp())
        successfullRequest,response = self.__getAPIResponse()
        if not successfullRequest:
            return False

        return self.__parseSuccessfulGetLatestRequest(response)

    def __getAPIResponse(self):

        parameters = self.__updateRequesetParameters()
        log.debug("Attempting API call at '{}' with parameters '{}'".format(settings.getLatest_Url,parameters))
        retries = settings.API_callRetriesOnFailure
        attempt = 1;
        while retries >= 0:
            try:
                response = self.__getLatestSession.get(settings.getLatest_Url,params=parameters,timeout=settings.API_call_timeout_seconds)
                retries = -1;
            except ConnectionError:
                retries,attempt,done = self.__evaluateAttempt(retries,attempt)
                if not done:
                    continue
                self.__getLatestStatus = self.__makeCustomStatusError(3,"Internal error: Connection exception when conduction API call")
                self.__getLatestData = None
                return False,None
            except Timeout:
                retries,attempt,done = self.__evaluateAttempt(retries,attempt)
                if not done:
                    continue
                self.__getLatestStatus = self.__makeCustomStatusError(4,"Internal error: Timeout exception when conduction API call, no internet connection?")
                self.__getLatestData = None
                return False,None
            except TooManyRedirects:
                retries,attempt,done = self.__evaluateAttempt(retries,attempt)
                if not done:
                    continue
                self.__getLatestStatus = self.__makeCustomStatusError(5,"Internal error: Too many redirects exception when conduction API call")
                self.__getLatestData = None
                return False,None

        return True,response

    def __evaluateAttempt(self,retries,attempt):
        if retries >= 1:
            retries = retries - 1;
            time.sleep(2*attempt)
            log.warning("Exception occurred on API call attempt {} of {}".format(attempt,settings.API_callRetriesOnFailure));
            attempt = attempt + 1
            done = False
        else:
            done = True
        return retries,attempt,done

    def __parseSuccessfulGetLatestRequest(self,response):
        try:
            jsonFields = json.loads(response.text)
        except json.decoder.JSONDecodeError:
            self.__getLatestStatus = self.__makeCustomStatusError(2,"Internal error: Error parsion JSON object from received response")
            self.__getLatestData = None
            return False

        if response.status_code == 200:
            try:
                self.__getLatestData = jsonFields['data']
                self.__getLatestStatus = jsonFields['status']
            except KeyError:
                self.__getLatestStatus = self.__makeCustomStatusError(1,"Internal error: Error parsing main dictionary keys from received response")
                self.__getLatestData = None
                return False
            return self.__checkGoodStatusKeys() and self.__checkGoodDataKeys()
        else:
            try:
                self.__getLatestStatus = jsonFields['status']
                self.__checkGoodStatusKeys()
                log.warning("Failed API request, Receved HTTP code {} from server".format(response.status_code))
            except KeyError:
                self.__getLatestStatus = self.__makeCustomStatusError(1,"Internal error: Error parsing main dictionary keys from received response")
                self.__getLatestData = None
            return False

    def __checkGoodDataKeys(self):
        if len(self.getLatestData()) != (self.__configuration['endIndex'] - self.__configuration['startIndex'] + 1):
            self.__getLatestStatus = self.__makeCustomStatusError(8,"Internal error: Number of received crypto data points doesn't match that requested.")
            self.__getLatestData = None
            return False
        try:
            for i in range(0,len(self.getLatestData())):
                dummy = self.getLatestData()[i][settings.CMC_data_id]
                dummy = self.getLatestData()[i][settings.CMC_data_name]
                dummy = self.getLatestData()[i][settings.CMC_data_symbol]
                dummy = self.getLatestData()[i][settings.CMC_data_slug]
                dummy = self.getLatestData()[i][settings.CMC_data_cmc_rank]
                dummy = self.getLatestData()[i][settings.CMC_data_num_market_pairs]
                dummy = self.getLatestData()[i][settings.CMC_data_circulating_suuply]
                dummy = self.getLatestData()[i][settings.CMC_data_total_supply]
                dummy = self.getLatestData()[i][settings.CMC_data_max_supply]
                dummy = self.getLatestData()[i][settings.CMC_data_last_updated]
                dummy = self.getLatestData()[i][settings.CMC_data_data_added]
                dummy = self.getLatestData()[i][settings.CMC_data_tags]
                dummy = self.getLatestData()[i][settings.CMC_data_platform]
                dummy = self.getLatestData()[i][settings.CMC_data_quote][self.__configuration['conversionCurrency']][settings.CMC_data_quote_price]
                dummy = self.getLatestData()[i][settings.CMC_data_quote][self.__configuration['conversionCurrency']][settings.CMC_data_quote_volume_24h]
                dummy = self.getLatestData()[i][settings.CMC_data_quote][self.__configuration['conversionCurrency']][settings.CMC_data_quote_market_cap]
                dummy = self.getLatestData()[i][settings.CMC_data_quote][self.__configuration['conversionCurrency']][settings.CMC_data_percent_change_1h]
                dummy = self.getLatestData()[i][settings.CMC_data_quote][self.__configuration['conversionCurrency']][settings.CMC_data_percent_change_24h]
                dummy = self.getLatestData()[i][settings.CMC_data_quote][self.__configuration['conversionCurrency']][settings.CMC_data_percent_change_7d]
                dummy = self.getLatestData()[i][settings.CMC_data_quote][self.__configuration['conversionCurrency']][settings.CMC_data_last_updated]
            log.info("Successful API call returned {} crypto entries".format(len(self.getLatestData())))
        except KeyError:
            self.__getLatestStatus = self.__makeCustomStatusError(7,"Internal error: Error parsing API received data keys")
            self.__getLatestData = None
            return False
        return True

    def __checkGoodStatusKeys(self):
        try:
            dummy = self.getLatestStatus()[settings.CMC_status_timestamp]
            dummy = self.getLatestStatus()[settings.CMC_status_elapsed]
            dummy = self.getLatestStatus()[settings.CMC_status_error_code]
            dummy = self.getLatestStatus()[settings.CMC_status_credit_count]
            dummy = self.getLatestStatus()[settings.CMC_status_error_message]
        except KeyError:
            self.__getLatestStatus = self.__makeCustomStatusError(6,"Internal error: Error parsing API received status keys")
            self.__getLatestData = None
            return False
        return True

    def __makeCustomStatusError(self,errNo,message):
       customStatus = dict();
       customStatus[settings.CMC_status_timestamp] = str(datetime.datetime.now().isoformat())
       customStatus[settings.CMC_status_error_code] = errNo
       customStatus[settings.CMC_status_error_message] = message
       customStatus[settings.CMC_status_elapsed] = 0
       customStatus[settings.CMC_status_credit_count] = 0
       log.error(message)
       return customStatus;

    def __updateRequesetParameters(self):
        defaultParameters = settings.getLatest_Parameters
        defaultParameters['start'] = self.__configuration['startIndex']
        defaultParameters['limit'] = self.__configuration['endIndex'] - self.__configuration['startIndex'] + 1
        defaultParameters['convert'] = self.__configuration['conversionCurrency']
        return defaultParameters

    def prettyPrint(self,jsonObject):
        print(json.dumps(jsonObject,sort_keys=True,indent=2))

    def secondsToNextAPICall(self):
        if self.__lastCallTimestamp is None:
            return 0
        nextCall = self.__lastCallTimestamp + self.__configuration['callInterval'] * 60;
        remainingTime = nextCall - int(datetime.datetime.now().timestamp())
        return remainingTime if remainingTime >= 0 else 0
