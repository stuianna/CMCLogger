from modules.DBOps.dbops import DBOps
from modules.configChecker.configChecker import ConfigChecker
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

    def getDatabase(self):
        return self.__database

    def processRequest(self,request):
        log.info("Processing data request {}".format(request))
        if request[settings.data_query_type] == settings.data_query_type_price:
            return self.__processPriceRequest(request)

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
            str(round(entry[12],2))

    def __shortPriceJson(self,entry):
        symbol = self.__config.getValue(settings.API_section_name,settings.API_option_conversion_currency_symbol)
        outputDict = {
                settings.CMC_data_symbol : str(entry[14]),
                settings.CMC_data_quote_price : symbol + str(round(entry[12],2))
                }
        return str(json.dumps(outputDict))

    def __longPriceJson(self,entry):
        symbol = self.__config.getValue(settings.API_section_name,settings.API_option_conversion_currency_symbol)
        outputDict = {
                settings.CMC_data_symbol : str(entry[14]),
                settings.CMC_data_quote_price : symbol + str(round(entry[12],2)),
                settings.CMC_data_percent_change_1h : str(round(entry[9],2)) + "%",
                settings.CMC_data_percent_change_24h : str(round(entry[10],2)) + "%",
                settings.CMC_data_percent_change_7d : str(round(entry[11],2)) + "%",
                settings.CMC_data_quote_market_cap : self.__currencyToNiceFormat(entry)
                }
        return str(json.dumps(outputDict))

    def __longPriceStdout(self,entry):
        return str(entry[14]) + \
            ": " + \
            self.__config.getValue(settings.API_section_name,settings.API_option_conversion_currency_symbol) + \
            str(round(entry[12],2)) + \
            ' 1H: ' + \
            str(round(entry[9],2)) + \
            '% 1D: ' + \
            str(round(entry[10],2)) + \
            '% 7D: ' + \
            str(round(entry[11],2)) + \
            '% 24h Volume: ' + \
            self.__currencyToNiceFormat(entry)

    def __currencyToNiceFormat(self,entry):
        n = float(entry[17])
        millidx = max(0,min(len(millnames)-1,int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
        return '{:.2f}{}'.format(n / 10**(3 * millidx), millnames[millidx])


