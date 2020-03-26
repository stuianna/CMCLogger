import settings
import logging
import time
from dateutil import parser,tz
from modules.DBOps.dbops import DBOps

allowedDataFormats = ['ini']
log = logging.getLogger(__name__)

class DataPublisher():

    def __init__(self,status,database):
        self.__status = status
        self.__checkstatus()
        self.__database = database
        log.debug("Data publisher setup with inital status '{}'".format(status.getExpectations()))

    def __checkstatus(self):
        if self.__status.getValue(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls) < 0:
            self.__resetAllTimeStats()
        if self.__status.getValue(settings.status_file_all_time_section_name,settings.status_file_option_failed_calls) < 0:
            self.__resetAllTimeStats()
        if self.__status.getValue(settings.status_file_all_time_section_name,settings.status_file_option_success_rate) < 0:
            self.__resetAllTimeStats()
        if self.__status.getValue(settings.status_file_all_time_section_name,settings.status_file_option_success_rate) > 100.0:
            self.__resetAllTimeStats()

    def __resetAllTimeStats(self):
        log.warning("Status file {} sections conatins invalid values, restting to default".format(
            settings.status_file_all_time_section_name))
        self.__status.setValue(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls,0)
        self.__status.setValue(settings.status_file_all_time_section_name,settings.status_file_option_failed_calls,0)
        self.__status.setValue(settings.status_file_all_time_section_name,settings.status_file_option_success_rate,100.0)

    def getStatus(self):
        return self.__status

    def writeStatus(self,status):
        log.debug('Updating file status')

        if status[settings.CMC_status_error_code] == 0:
            self.__writeSuccessfulCallStats(status)
        else:
            self.__writeFailedCallStats(status)

        self.__writeCommonCallStats(status)
        self.__status.writeConfigurationFile();

    def __writeCommonCallStats(self,status):
        self.__status.setValue(settings.status_file_current_session_section_name,settings.status_file_option_success_rate,
                self.__calculatePercent(self.__status.getValue(settings.status_file_current_session_section_name,settings.status_file_option_successful_calls),
                self.__status.getValue(settings.status_file_current_session_section_name,settings.status_file_option_failed_calls)))

        self.__status.setValue(settings.status_file_all_time_section_name,settings.status_file_option_success_rate,
                self.__calculatePercent(self.__status.getValue(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls),
                self.__status.getValue(settings.status_file_all_time_section_name,settings.status_file_option_failed_calls)))

    def __writeSuccessfulCallStats(self,status):
        self.__incrementStatusValue(settings.status_file_current_session_section_name,settings.status_file_option_successful_calls)
        self.__incrementStatusValue(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls)
        self.__status.setValue(settings.status_file_last_call_section_name,settings.status_file_option_timeStamp,
                self.toLocalTime(status[settings.CMC_status_timestamp]))
        self.__status.setValue(settings.status_file_last_call_section_name,settings.status_file_option_error_code,status[settings.CMC_status_error_code])
        self.__status.setValue(settings.status_file_last_call_section_name,settings.status_file_option_error_message,status[settings.CMC_status_error_message])
        self.__status.setValue(settings.status_file_last_call_section_name,settings.status_file_option_elapsed,status[settings.CMC_status_elapsed])
        self.__status.setValue(settings.status_file_last_call_section_name,settings.status_file_option_credit_count,status[settings.CMC_status_credit_count])

    def __writeFailedCallStats(self,status):
        self.__incrementStatusValue(settings.status_file_current_session_section_name,settings.status_file_option_failed_calls)
        self.__incrementStatusValue(settings.status_file_all_time_section_name,settings.status_file_option_failed_calls)
        self.__status.setValue(settings.status_file_last_failed_secion_name,settings.status_file_option_timeStamp,
                self.toLocalTime(status[settings.CMC_status_timestamp]))
        self.__status.setValue(settings.status_file_last_failed_secion_name,settings.status_file_option_error_code,status[settings.CMC_status_error_code])
        self.__status.setValue(settings.status_file_last_failed_secion_name,settings.status_file_option_error_message,status[settings.CMC_status_error_message])
        self.__status.setValue(settings.status_file_last_failed_secion_name,settings.status_file_option_elapsed,status[settings.CMC_status_elapsed])
        self.__status.setValue(settings.status_file_last_failed_secion_name,settings.status_file_option_credit_count,status[settings.CMC_status_credit_count])

    def __calculatePercent(self,success,fail):
        return round(100 * success/(success+fail),2)

    def toLocalTime(self,iso8601):
        return str(parser.parse(iso8601).astimezone(tz.tzlocal()))

    def __incrementStatusValue(self,sectionName,optionName):
        self.__status.setValue(sectionName,optionName,self.__status.getValue(sectionName,optionName)+1)

    def writeData(self,data):
        if data is None:
            return
        self.__createDataBaseIfNotExist()
        for entry in data:
            dataCopy = dict(entry)
            self.__dropUnusedEntries(dataCopy)
            self.__createTablesAsNeeded(dataCopy)
            self.__createTimestamp(dataCopy)
            self.__convertTimeEntries(dataCopy)
            dataList = self.__convertToSortedList(dataCopy)
            self.__addToDatabase(dataCopy,dataList)
            log.debug("Adding a new entry in database for coin '{}'".format(dataCopy[settings.CMC_data_symbol]))
        log.info("Added {} new entries to the database".format(len(data)))

    def __addToDatabase(self,dataCopy,dataList):
         try:
            self.__database.append(dataCopy[settings.CMC_data_symbol],dataList)
         except Exception as e:
             log.error("Error adding coin '{}' to database, DBOps error {}".format(dataCopy[settings.CMC_data_symbol],e))

    def __convertToSortedList(self,entry):
        dataList = []
        for item in  sorted(entry.keys()):
            dataList.append(entry[item])
        return dataList

    def __convertTimeEntries(self,entry):
        entry[settings.CMC_data_data_added] = self.__convertISO860toUnixTime(entry[settings.CMC_data_data_added])
        entry[settings.CMC_data_last_updated] = self.__convertISO860toUnixTime(entry[settings.CMC_data_last_updated])

    def __convertISO860toUnixTime(self,iso8601):
        return int((parser.parse(iso8601).strftime('%s')))

    def __createTimestamp(self,entry):
        entry['timestamp'] = int(time.time())

    def __dropUnusedEntries(self,entry):
        self.__flattenJsonData(entry)
        entry.pop(settings.CMC_data_quote)
        entry.pop(settings.CMC_data_tags)
        entry.pop(settings.CMC_data_platform)

    def __flattenJsonData(self,entry):
        currencyEntry = next(iter(entry[settings.CMC_data_quote]))
        entry[settings.CMC_data_quote_price] = entry[settings.CMC_data_quote][currencyEntry][settings.CMC_data_quote_price]
        entry[settings.CMC_data_quote_volume_24h] = entry[settings.CMC_data_quote][currencyEntry][settings.CMC_data_quote_volume_24h]
        entry[settings.CMC_data_quote_market_cap] = entry[settings.CMC_data_quote][currencyEntry][settings.CMC_data_quote_market_cap]
        entry[settings.CMC_data_percent_change_1h] = entry[settings.CMC_data_quote][currencyEntry][settings.CMC_data_percent_change_1h]
        entry[settings.CMC_data_percent_change_24h] = entry[settings.CMC_data_quote][currencyEntry][settings.CMC_data_percent_change_24h]
        entry[settings.CMC_data_percent_change_7d] = entry[settings.CMC_data_quote][currencyEntry][settings.CMC_data_percent_change_7d]

    def __createDataBaseIfNotExist(self):
        if not self.__database.exists():
            log.error("Target database didn't exist at runtime, creating a new database")
            self.__database.createDatabase()

    def __createTablesAsNeeded(self,entry):
        ## TODO can check if table actually existed to save making the columns every time.
        self.__database.createTableIfNotExist(entry[settings.CMC_data_symbol],self.__makeDataBaseTableColumns())

    def __makeDataBaseTableColumns(self):
        columns = ''
        columns = columns + self.__columnEntry('timestamp','INTEGER')
        columns = columns + self.__columnEntry(settings.CMC_data_circulating_suuply,settings.CMC_data_circulating_suuply_type)
        columns = columns + self.__columnEntry(settings.CMC_data_cmc_rank,settings.CMC_data_cmc_rank_type)
        columns = columns + self.__columnEntry(settings.CMC_data_data_added,settings.CMC_data_data_added_type)
        columns = columns + self.__columnEntry(settings.CMC_data_id,settings.CMC_data_id_type)
        columns = columns + self.__columnEntry(settings.CMC_data_last_updated,settings.CMC_data_last_updated_type)
        columns = columns + self.__columnEntry(settings.CMC_data_max_supply,settings.CMC_data_max_supply_type)
        columns = columns + self.__columnEntry(settings.CMC_data_name,settings.CMC_data_name_type)
        columns = columns + self.__columnEntry(settings.CMC_data_quote_market_cap,settings.CMC_data_quote_market_cap_type)
        columns = columns + self.__columnEntry(settings.CMC_data_num_market_pairs,settings.CMC_data_num_market_pairs_type)
        columns = columns + self.__columnEntry(settings.CMC_data_percent_change_1h,settings.CMC_data_percent_change_1h_type)
        columns = columns + self.__columnEntry(settings.CMC_data_percent_change_7d,settings.CMC_data_percent_change_7d_type)
        columns = columns + self.__columnEntry(settings.CMC_data_percent_change_24h,settings.CMC_data_percent_change_24h_type)
        columns = columns + self.__columnEntry(settings.CMC_data_quote_price,settings.CMC_data_quote_price_type)
        columns = columns + self.__columnEntry(settings.CMC_data_slug,settings.CMC_data_slug_type)
        columns = columns + self.__columnEntry(settings.CMC_data_symbol,settings.CMC_data_symbol_type)
        columns = columns + self.__columnEntry(settings.CMC_data_total_supply,settings.CMC_data_total_supply_type)
        columns = columns + self.__columnEntry(settings.CMC_data_quote_volume_24h,settings.CMC_data_quote_volume_24h_type)
        columns = columns[0:-1]
        columns = self.__sortColumnNames(columns)
        return columns

    def __sortColumnNames(self,columns):
        arr = columns.split(',')
        arr = sorted(arr)
        return ','.join(arr)

    def __columnEntry(self,name,dataType):
        return ' ' +name + ' ' + dataType + ','

