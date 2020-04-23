#!/bin/python3

import sys
import os
import time
import logging
import socket
import pandas as pd
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
        _ = e
        log.warning("Attempting to start daemon which is already running")
        return True


class CMCLogger():
    """API wrapper for fetching, logging, storing and querying Cryptocurreny using the
    Coin Market Cap (free) API

    This API is, at the moment, is primarily set-up to be used with the CMCLogger script provided
    in this package, however the API could be used stand-alone as follows:

    Example Usage:
    >>> working_directory = 'CMC_Logger'
    >>> api_key = 'my_free_api_key'
    >>> cmc = CMCLogger(working_directory, api_key = my_key)

    Initialising the class object creates, (if it doesn't already exist ), the configuration file
    and a data directory containing the cryptocurrency data, status file and log output. The
    configuration file should be edited to customise parameters, but it is not required for
    functionaility.

    Make an API call to CMC based on configuration file parameters, and store the results in the
    sql database.
    >>> cmc.fetch_and_store_data()

    Optionally, the daemon can be started, which makes a call for new data at the interval set in
    the configuratino file (default = 5 minutes)
    >>> cmc.start_daemon()

    See the module README for more detailed information
    """

    def __init__(self, working_directory, log_level=logging.WARNING, api_key=None):
        self.__workingDirectory = working_directory
        self.__make_directories_as_needed()
        self.__setup_logging(log_level)
        self.__config = self.__load_configuration(api_key)
        self.__status = self.__setup_status_file()
        self.__database = self.__setup_database()
        self.__api = None
        self.__publisher = None

    def start_daemon(self, force_start=False):
        """ Start the logging daemon, if it is not already running.

        The logging daemon uses the values found in config.ini in the working directory.
        Calls are made to the CMC API at the configuration interval set with the requried parameters.

        Parameters:
        force_start: Start the daemon even if it is already running. Warning, this could result in rate limiting.

        Return:
        This call doesn't return
        """
        if daemon_already_running() and not force_start:
            return

        self.__status.set_value(settings.status_file_current_session_section_name, settings.status_file_option_successful_calls, 0)
        self.__status.set_value(settings.status_file_current_session_section_name, settings.status_file_option_failed_calls, 0)
        self.__status.set_value(settings.status_file_current_session_section_name, settings.status_file_option_success_rate, 100.0)
        self.__create_API_and_publisher()

        self.__daemon()

    def __daemon(self):
        while True:
            goodResponse = self.__api.getLatest()
            self.__publisher.writeStatus(self.__api.getLatestStatus())
            if goodResponse is True:
                self.__publisher.writeData(self.__api.getLatestData())

            log.info("Scheduling next API call in {} seconds".format(
                self.__api.secondsToNextAPICall()))

            time.sleep(self.__api.secondsToNextAPICall())

    def fetch_and_store_data(self, api_key=None):
        """ Make an CMC API call and store the result in the database / status file

        The configuration will be sourced from config.ini in the working directory used
        when the object was created.

        Parameters:
        api_key: Optionally make this API call with a different key as specified.

        Returns:
        (respnse_status, latest_data, latest_status) (tuple)

        response_status (bool): True if the API call and storage completed successfully.
        latest_data (dict): Latest good data returned from coin market cap API. This data is
        guarenteed to be from the latest call only if response_status is True.
        status (dict): Dictionary containing the status of the last call.
        """
        self.__create_API_and_publisher()
        goodResponse = self.__api.getLatest(api_key)
        self.__publisher.writeStatus(self.__api.getLatestStatus())
        if goodResponse is True:
            self.__publisher.writeData(self.__api.getLatestData())
        return goodResponse, self.__api.getLatestData(), self.__api.getLatestStatus()

    def write_custom_status(self, status):
        """ Enter a custom status into the results API

        Parameters:
        status (dict): A correctly structured dictionary can be obtained from the
        returned status of fetch_and_store_data
        """
        self.__create_API_and_publisher()
        self.__publisher.writeStatus(status)

    def data_request(self, request):
        """ Request data from the database

        Parameters:
        request (dict): {"query_type", "query_tag", "output_format", "output_detail"}
        """
        reader = Reader(self.__status, self.__database, self.__config)
        print(reader.processRequest(request))

    def get_database(self):
        """ Get the dbops.SQHelper data base object being used."""
        return self.__database

    def get_status_file(self):
        """ Get the configchecker.ConfigChecker status file object being used."""
        return self.__status

    def get_config_file(self):
        """ Get the configchecker.ConfigChecker config file object being used."""
        return self.__config

    def to_excel(self):
        tables = self.__database.get_table_names()
        if len(tables) == 0:
            return False
        df_list = []
        for table in tables:
            df_list.append(self.__database.table_to_df(table))
        writer = pd.ExcelWriter(r"cryptoData.xlsx")
        _ = [A.to_excel(writer,sheet_name="{0}".format(tables[i])) for i, A in enumerate(df_list)]
        writer.save()
        return True

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
