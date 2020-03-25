import settings
import logging
from dateutil import parser,tz

allowedDataFormats = ['ini']
log = logging.getLogger(__name__)

class DataPublisher():

    def __init__(self,status):
        self.__status = status
        self.__checkstatus()
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
        pass
