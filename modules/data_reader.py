from modules.DBOps.dbops import DBOps
from modules.configChecker.configChecker import ConfigChecker
from dateutil import parser,tz
from io import StringIO
import settings
import logging
import json
import time
import sys
import math

log = logging.getLogger(__name__)
millnames = ['',' Thousand',' Million',' Billion',' Trillion']

class DataReader():

    def __init__(self,statusFile,database,config):

        self.__statusFile = statusFile
        self.__database = database
        self.__config = config

        log.debug("Starting a new data reader instance")

    def getStatusFile(self):
        return self.__statusFile

    def processRequest(self,request):
        log.info("Processing data request {}".format(request))
        if request[settings.data_query_type] == settings.data_query_type_price:
            return self.__processPriceRequest(request)
        elif request[settings.data_query_type] == settings.data_query_type_status:
            return self.__processStatusRequest(request)
        else:
            log.warning("Request with type {} is not valid".format(request[settings.data_query_type]))
            return "Request with type {} is not valid".format(request[settings.data_query_type])

    def __processStatusRequest(self,request):
        if request[settings.data_query_format] == settings.data_query_format_stdout:
            return self.__processStatusStdout(request)
        elif request[settings.data_query_format] == settings.data_query_format_json:
            return self.__processStatusJson(request)
        else:
            log.warning("Request with data format {} is not valid".format(request[settings.data_query_format]))
            return "Request with data format {} is not valid".format(request[settings.data_query_format])

    def __processStatusJson(self,request):
        if request[settings.data_query_detail] == settings.data_query_detail_short:
            return self.__shortStatusJson(request)
        elif request[settings.data_query_detail] == settings.data_query_detail_long:
            return self.__longStatusJson(request)
        else:
            log.warning("JSON status request with detail {} not valid".format(request[settings.data_query_detail]))
            return "JSON status request with detail {} not valid".format(request[settings.data_query_detail])

    def __processStatusStdout(self,request):
        if request[settings.data_query_detail] == settings.data_query_detail_short:
            return self.__shortStatusStdout(request)
        elif request[settings.data_query_detail] == settings.data_query_detail_long:
            return self.__longStatusStdout(request)
        else:
            log.warning("STDOUT status request with detail {} not valid".format(request[settings.data_query_detail]))
            return "STDOUT status request with detail {} not valid".format(request[settings.data_query_detail])

    def __longStatusStdout(self,request):
        results = StringIO()
        self.__statusFile.getConfigParserObject().write(results)
        return results.getvalue()

    def __longStatusJson(self,request):
        return  json.dumps(self.__statusFile.getConfigParserObject()._sections)

    def __shortStatusStdout(self,request):
        minutes = self.__calculateMinutesSinceLastCall()
        return "Last successful call {} minutes ago, health {}%.".format(minutes,
                self.__statusFile.getValue(settings.status_file_current_session_section_name,settings.status_file_option_health))

    def __shortStatusJson(self,request):
        minutes = self.__calculateMinutesSinceLastCall()
        health = self.__statusFile.getValue(settings.status_file_current_session_section_name,settings.status_file_option_health)
        output = dict({settings.output_json_last_call : minutes, settings.output_json_health : health})
        return json.dumps(output)

    def __calculateMinutesSinceLastCall(self):
        lastCall = int((parser.parse(self.__statusFile.getValue(
            settings.status_file_last_call_section_name,
            settings.status_file_option_timeStamp)).strftime('%s')))
        currentTime = int(time.time());
        return int((currentTime - lastCall) / 60)

    def __processPriceRequest(self,request):
        entry = self.__database.getLastTimeEntry(request[settings.data_query_tag])
        if entry is None:
            log.error("Cannot request symbol {} from database, as it does not exist.".format(request[settings.data_query_tag]))
            return "{} not a valid stored cryptocurreny symbol.".format(request[settings.data_query_tag])
        if request[settings.data_query_detail] == settings.data_query_detail_short:
            return self.__processShortPriceRequest(entry[0],request)
        elif request[settings.data_query_detail] == settings.data_query_detail_long:
            return self.__processLongPriceRequest(entry[0],request)
        else:
            log.warning("Price request detail '{}' not found".format(request[settings.data_query_detail]))
            return '{} is an invalid output detail request.'.format(request[settings.data_query_detail])

    def __processLongPriceRequest(self,entry,request):
        if request[settings.data_query_format] == settings.data_query_format_stdout:
            return self.__longPriceStdout(entry)
        elif request[settings.data_query_format] == settings.data_query_format_json:
            return self.__longPriceJson(entry)
        else:
            log.warning("Price request format '{}' not found".format(request[settings.data_query_format]))
            return "{} is an invalid price request format".format(request[settings.data_query_format])

    def __processShortPriceRequest(self,entry,request):
        if request[settings.data_query_format] == settings.data_query_format_stdout:
            return self.__shortPriceStdout(entry)
        elif request[settings.data_query_format] == settings.data_query_format_json:
            return self.__shortPriceJson(entry)
        else:
            log.warning("Price request format '{}' not found".format(request[settings.data_query_format]))
            return "{} is an invalid price request format".format(request[settings.data_query_format])

    def __shortPriceStdout(self,entry):
        return str(entry[14]) + \
            ": " + \
            self.__config.getValue(settings.API_section_name,settings.API_option_conversion_currency_symbol) + \
            self.__getListAndRoundValue(entry,12) + \
            " (" +  \
            self.__getListAndRoundValue(entry,10) + \
            "%)"

    def __shortPriceJson(self,entry):
        symbol = self.__config.getValue(settings.API_section_name,settings.API_option_conversion_currency_symbol)
        outputDict = {
                settings.CMC_data_symbol : str(entry[14]),
                settings.CMC_data_quote_price : symbol + self.__getListAndRoundValue(entry,12),
                settings.CMC_data_percent_change_24h : self.__getListAndRoundValue(entry,10) + '%'
                }
        return str(json.dumps(outputDict))

    def __longPriceJson(self,entry):
        symbol = self.__config.getValue(settings.API_section_name,settings.API_option_conversion_currency_symbol)
        outputDict = {
                settings.CMC_data_symbol : str(entry[14]),
                settings.CMC_data_quote_price : symbol + self.__getListAndRoundValue(entry,12),
                settings.CMC_data_percent_change_1h : self.__getListAndRoundValue(entry,9) + "%",
                settings.CMC_data_percent_change_24h : self.__getListAndRoundValue(entry,10) + "%",
                settings.CMC_data_percent_change_7d : self.__getListAndRoundValue(entry,11) + "%",
                settings.CMC_data_quote_market_cap : self.__currencyToNiceFormat(entry)
                }
        return str(json.dumps(outputDict))

    def __longPriceStdout(self,entry):
        return str(entry[14]) + \
            ": " + \
            self.__config.getValue(settings.API_section_name,settings.API_option_conversion_currency_symbol) + \
            self.__getListAndRoundValue(entry,12)+ \
            ' 1H: ' + \
            self.__getListAndRoundValue(entry,9)+ \
            '% 1D: ' + \
            self.__getListAndRoundValue(entry,10)+ \
            '% 7D: ' + \
            self.__getListAndRoundValue(entry,11)+ \
            '% 24h Volume: ' + \
            self.__currencyToNiceFormat(entry)

    def __getListAndRoundValue(self,entry,index):
        try:
            value = round(entry[index],2)
            return str(value)
        except:
            return "NULL"

    def __currencyToNiceFormat(self,entry):
        n = float(entry[17])
        millidx = max(0,min(len(millnames)-1,int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
        return '{:.2f}{}'.format(n / 10**(3 * millidx), millnames[millidx])


