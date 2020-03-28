#!/bin/python3

import atexit

import time
import sys
import os
import socket

import json

import settings
import logging
from modules.cmcapi_wrapper import CMCAPI_Wrapper
from modules.configChecker.configChecker import ConfigChecker
from modules.data_publisher import DataPublisher
from modules.DBOps.dbops import DBOps
from modules.data_reader import DataReader

log = logging.getLogger(__name__)

def setupDatabase(workingDirectory):
    fileLocation = os.path.join(workingDirectory,settings.data_file_directory,settings.database_file_name)
    database = DBOps(fileLocation)
    if not database.exists():
        return None,False
    return database,True

def setStatusFileOptions(status,workingDirectory,newSession=True):

    status.setExpectation(
            settings.status_file_last_call_section_name,
            settings.status_file_option_timeStamp,
            str,
            '')
    status.setExpectation(
            settings.status_file_last_call_section_name,
            settings.status_file_option_error_code,
            int,
            0)
    status.setExpectation(
            settings.status_file_last_call_section_name,
            settings.status_file_option_error_message,
            str,
            '')
    status.setExpectation(
            settings.status_file_last_call_section_name,
            settings.status_file_option_elapsed,
            int,
            0)
    status.setExpectation(
            settings.status_file_last_call_section_name,
            settings.status_file_option_credit_count,
            int,
            0)
    status.setExpectation(
            settings.status_file_last_failed_secion_name,
            settings.status_file_option_timeStamp,
            str,
            '')
    status.setExpectation(
            settings.status_file_last_failed_secion_name,
            settings.status_file_option_error_code,
            int,
            0)
    status.setExpectation(
            settings.status_file_last_failed_secion_name,
            settings.status_file_option_error_message,
            str,
            '')
    status.setExpectation(
            settings.status_file_last_failed_secion_name,
            settings.status_file_option_elapsed,
            int,
            0)
    status.setExpectation(
            settings.status_file_last_failed_secion_name,
            settings.status_file_option_credit_count,
            int,
            0)
    status.setExpectation(
            settings.status_file_current_session_section_name,
            settings.status_file_option_health,
            float,
            100.0)
    status.setExpectation(
            settings.status_file_current_session_section_name,
            settings.status_file_option_successful_calls,
            int,
            0)
    status.setExpectation(
            settings.status_file_current_session_section_name,
            settings.status_file_option_failed_calls,
            int,
            0)
    status.setExpectation(
            settings.status_file_current_session_section_name,
            settings.status_file_option_success_rate,
            float,
            100.0)
    status.setExpectation(
            settings.status_file_all_time_section_name,
            settings.status_file_option_successful_calls,
            int,
            0)
    status.setExpectation(
            settings.status_file_all_time_section_name,
            settings.status_file_option_failed_calls,
            int,
            0)
    status.setExpectation(
            settings.status_file_all_time_section_name,
            settings.status_file_option_success_rate,
            float,
            100.0)

    fileLocation = os.path.join(workingDirectory,settings.status_file_directory, settings.status_file_name)
    status.setConfigurationFile(fileLocation)

    if newSession is True:
        ## Reset the current session values to zero
        status.setValue(settings.status_file_current_session_section_name,settings.status_file_option_successful_calls,0)
        status.setValue(settings.status_file_current_session_section_name,settings.status_file_option_failed_calls,0)
        status.setValue(settings.status_file_current_session_section_name,settings.status_file_option_success_rate,100.0)

    return status.writeConfigurationFile(fileLocation)

def makeDir(targetDirectory):
    if not os.path.exists(targetDirectory):
        try:
            log.debug("Creating new directory '{}'".format(targetDirectory))
            os.makedirs(targetDirectory)
        except OSError as e:
            log.error("Cannot create directory '{}'. Exception '{}'".format(targetDirectory,e))
            raise

def makeDirectoriesAsNeeded(workingDirectory):
    try:
        targetDirectory = os.path.join(workingDirectory,settings.data_file_directory)
        makeDir(targetDirectory)
        targetDirectory = os.path.join(workingDirectory,settings.log_file_directory)
        makeDir(targetDirectory)
        targetDirectory = os.path.join(workingDirectory,settings.status_file_directory)
        makeDir(targetDirectory)
        return True
    except:
        return False


def getConfigurationOptions(config,workingDirectory):

    config.setExpectation(
            settings.API_section_name,
            settings.API_option_private_key,
            str,
            settings.API_option_privatate_key_default)
    config.setExpectation(
            settings.
            API_section_name,
            settings.API_option_conversion_currency,
            str,
            settings.API_option_conversion_currency_default)
    config.setExpectation(
            settings.
            API_section_name,
            settings.API_option_conversion_currency_symbol,
            str,
            settings.API_option_conversion_currency_symbol_default)
    config.setExpectation(
            settings.API_section_name,
            settings.API_option_start_index,
            int,
            settings.API_option_start_index_default)
    config.setExpectation(
            settings.API_section_name,
            settings.API_option_end_index,
            int,
            settings.API_option_end_index_default)
    config.setExpectation(
            settings.API_section_name,
            settings.API_option_interval,
            int,
            settings.API_option_interval_default)

    config.setExpectation(
            settings.general_section_name,
            settings.general_option_status_file_format,
            str,
            settings.general_option_status_file_format_default)

    fileLocation = os.path.join(workingDirectory, settings.input_configuation_filename)
    config.setConfigurationFile(fileLocation)
    return config.writeConfigurationFile(fileLocation)


def daemonAlreadyRunning():
    processName = "CMCLogger"
    daemonAlreadyRunning._lock_socket = socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
    try:
        daemonAlreadyRunning._lock_socket.bind('\0' + processName)
        log.info("New daemon logging instance started")
        return False
    except:
        log.warning("Attempting to start daemon which is already running")
        return True

def setupLogging(logLevel,outputFile,workingDirectory):
    try:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s: %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S%p', level=logLevel, filename=outputFile)
    except Exception as e:
        print("Failed to create logging file. Exception '{}'".format(e), file=sys.stderr)

if __name__ == '__main__':

    # Process command line options
        # Generate config
        # restart daemon
        # stop daemon
        # Get status
        # Query price tag
        # Get next tag
        # Help
        # version

    if len(sys.argv) > 1:
        dataRequest = True
    else:
        dataRequest = False

    # Setup logging and settings
    workingDirectory = os.path.dirname(__file__)
    loggingFile = os.path.join(workingDirectory,settings.log_file_directory,settings.log_file_name)
    setupLogging(logging.DEBUG,loggingFile,workingDirectory)

    if not makeDirectoriesAsNeeded(workingDirectory):
        log.critical("Cannot create required directories for normal operation, exiting.")
        sys.exit()

    # Setup output streams
    status = ConfigChecker()
    if not setStatusFileOptions(status,workingDirectory,not dataRequest):
        log.error("Failed to create required status file, exiting")
        sys.exit()

    # Generate and load configuration
    config = ConfigChecker()
    if not getConfigurationOptions(config,workingDirectory):
        log.error("Failed to create required configuration file, exiting.")
        sys.exit()

    database, success = setupDatabase(workingDirectory)
    if not success:
        log.error("Failed to create required database file, exiting")
        sys.exit()

    if dataRequest:
        request = dict()
        request[settings.data_query_type] = settings.data_query_type_price
        request[settings.data_query_tag] = sys.argv[1]
        request[settings.data_query_format] = settings.data_query_format_stdout
        request[settings.data_query_detail] = settings.data_query_detail_long
    else:
        dataRequest = False

    if dataRequest is True:
        reader = DataReader(status,database,config)
        output = reader.processRequest(request)
        print(output)
        sys.exit();

    # Check if process already running
    if daemonAlreadyRunning():
        sys.exit();

    # Setup API
    api = CMCAPI_Wrapper(config);
    publisher = DataPublisher(status,database)

    # Start main functionality
    while True:
        goodResponse = api.getLatest()
        publisher.writeStatus(api.getLatestStatus())
        if goodResponse is True:
            publisher.writeData(api.getLatestData())
        log.info("Scheduling next API call in {} seconds".format(api.secondsToNextAPICall()))
        for i in range(api.secondsToNextAPICall()):time.sleep(1)

