#!/bin/python3

import sys
import os
import time
import logging
import socket
from datetime import datetime
from dbops.sqhelper import SQHelper
from configchecker import ConfigChecker
from cmclogger.api.getlatest import CMCGetLatest
from cmclogger.dataparser.publisher import Publisher
from cmclogger.dataparser.reader import Reader
import cmclogger.settings as settings

log = logging.getLogger(__name__)


def daemon_already_running():
    processName = "CMCLogger"
    daemon_already_running._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        daemon_already_running._lock_socket.bind('\0' + processName)
        log.info("New daemon logging instance started")
        return False
    except Exception as e:
        log.warning("Attempting to start daemon which is already running")
        return True


class CMCLogger():

    def __init__(self, workingDirectory, logLevel, apiKey=None):
        self.__workingDirectory = workingDirectory
        self.__make_directories_as_needed()
        self.__setup_logging(logLevel)
        self.__config = self.__load_configuration(apiKey)
        self.__status = self.__setup_status_file()
        self.__database = self.__setup_database()
        self.__api = None
        self.__publisher = None

    def start_daemon(self, forceStart=False):
        if daemon_already_running() and not forceStart:
            return

        self.__status.set_value(settings.status_file_current_session_section_name, settings.status_file_option_successful_calls, 0)
        self.__status.set_value(settings.status_file_current_session_section_name, settings.status_file_option_failed_calls, 0)
        self.__status.set_value(settings.status_file_current_session_section_name, settings.status_file_option_success_rate, 100.0)
        self.__create_API_and_publisher()

        while True:
            goodResponse = self.__api.getLatest()
            self.__publisher.writeStatus(self.__api.getLatestStatus())
            if goodResponse is True:
                self.__publisher.writeData(self.__api.getLatestData())

            log.info("Scheduling next API call in {} seconds".format(
                self.__api.secondsToNextAPICall()))

            time.sleep(self.__api.secondsToNextAPICall())


    def fetch_and_store_data(self, apiKey=None):
        self.__create_API_and_publisher()
        goodResponse = self.__api.getLatest(apiKey)
        self.__publisher.writeStatus(self.__api.getLatestStatus())
        if goodResponse is True:
            self.__publisher.writeData(self.__api.getLatestData())
        return goodResponse, self.__api.getLatestData(), self.__api.getLatestStatus()

    def write_custom_status(self, status):
        self.__create_API_and_publisher()
        self.__publisher.writeStatus(status)

    def data_request(self, request):
        reader = Reader(self.__status, self.__database, self.__config)
        print(reader.processRequest(request))

    def get_database(self):
        return self.__database

    def get_status_file(self):
        return self.__status

    def get_config_file(self):
        return self.__config

    def __create_API_and_publisher(self):
        if self.__api is None:
            self.__api = CMCGetLatest(self.__config)
        if self.__publisher is None:
            self.__publisher = Publisher(self.__status, self.__database)

    def __setup_logging(self, logLevel):
        loggingFile = os.path.join(self.__workingDirectory, settings.log_file_directory, settings.log_file_name)
        try:
            logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s: %(message)s',
                                datefmt='%m/%d/%Y %I:%M:%S%p', level=logLevel, filename=loggingFile)
        except Exception as e:
            print("Failed to create logging file. Exception '{}'".format(e), file=sys.stderr)
            raise

    def __make_directories_as_needed(self):
        targetDirectory = os.path.join(self.__workingDirectory, settings.data_file_directory)
        self.__make_dir(targetDirectory)
        targetDirectory = os.path.join(self.__workingDirectory, settings.log_file_directory)
        self.__make_dir(targetDirectory)
        targetDirectory = os.path.join(self.__workingDirectory, settings.status_file_directory)
        self.__make_dir(targetDirectory)

    def __make_dir(self, targetDirectory):
        if not os.path.exists(targetDirectory):
            try:
                log.debug("Creating new directory '{}'".format(targetDirectory))
                os.makedirs(targetDirectory)
            except OSError as e:
                log.error("Cannot create directory '{}'. Exception '{}'".format(targetDirectory, e))
                raise

    def __load_configuration(self, apiKey):
        config = ConfigChecker()
        config.set_expectation(settings.API_section_name, settings.API_option_private_key, str,
                               settings.API_option_privatate_key_default)
        config.set_expectation(settings.API_section_name, settings.API_option_conversion_currency, str,
                               settings.API_option_conversion_currency_default)
        config.set_expectation(settings.API_section_name, settings.API_option_conversion_currency_symbol, str,
                               settings.API_option_conversion_currency_symbol_default)
        config.set_expectation(settings.API_section_name, settings.API_option_start_index, int,
                               settings.API_option_start_index_default)
        config.set_expectation(settings.API_section_name, settings.API_option_end_index, int,
                               settings.API_option_end_index_default)
        config.set_expectation(settings.API_section_name, settings.API_option_interval, int,
                               settings.API_option_interval_default)
        config.set_expectation(settings.general_section_name, settings.general_option_status_file_format, str,
                               settings.general_option_status_file_format_default)


        fileLocation = os.path.join(self.__workingDirectory, settings.input_configuation_filename)
        config.set_configuration_file(fileLocation)

        if apiKey is not None:
            config.set_value(settings.API_section_name, settings.API_option_private_key, apiKey)

        if config.write_configuration_file(fileLocation) is False:
            log.critical("Failed to create required configuration file.")
            raise
        return config

    def __setup_status_file(self):
        status = ConfigChecker()
        status.set_expectation(settings.status_file_last_call_section_name,settings.status_file_option_timeStamp, str, datetime.now().isoformat())
        status.set_expectation(settings.status_file_last_call_section_name, settings.status_file_option_error_code, int, 0)
        status.set_expectation(settings.status_file_last_call_section_name, settings.status_file_option_error_message, str, '')
        status.set_expectation(settings.status_file_last_call_section_name, settings.status_file_option_elapsed, int, 0)
        status.set_expectation(settings.status_file_last_call_section_name, settings.status_file_option_credit_count, int, 0)
        status.set_expectation(settings.status_file_last_failed_secion_name, settings.status_file_option_timeStamp, str, '')
        status.set_expectation(settings.status_file_last_failed_secion_name, settings.status_file_option_error_code, int, 0)
        status.set_expectation(settings.status_file_last_failed_secion_name, settings.status_file_option_error_message, str, '')
        status.set_expectation(settings.status_file_last_failed_secion_name, settings.status_file_option_elapsed, int, 0)
        status.set_expectation(settings.status_file_last_failed_secion_name, settings.status_file_option_credit_count, int, 0)
        status.set_expectation(settings.status_file_current_session_section_name, settings.status_file_option_health, float, 100.0)
        status.set_expectation(settings.status_file_current_session_section_name, settings.status_file_option_successful_calls, int, 0)
        status.set_expectation(settings.status_file_current_session_section_name, settings.status_file_option_failed_calls, int, 0)
        status.set_expectation(settings.status_file_current_session_section_name, settings.status_file_option_success_rate, float,100.0)
        status.set_expectation(settings.status_file_all_time_section_name, settings.status_file_option_successful_calls, int, 0)
        status.set_expectation(settings.status_file_all_time_section_name, settings.status_file_option_failed_calls, int, 0)
        status.set_expectation(settings.status_file_all_time_section_name, settings.status_file_option_success_rate, float, 100.0)

        fileLocation = os.path.join(self.__workingDirectory, settings.status_file_directory, settings.status_file_name)
        status.set_configuration_file(fileLocation)
        if not status.write_configuration_file(fileLocation):
            log.critical("Failed to create required status file, exiting")
            raise
        return status

    def __setup_database(self):
        fileLocation = os.path.join(self.__workingDirectory, settings.data_file_directory, settings.database_file_name)
        database = SQHelper(fileLocation)
        if not database.exists():
            log.critical("Failed to create required database file, exiting")
            raise
        return database
