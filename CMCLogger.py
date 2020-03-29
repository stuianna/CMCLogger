#!/bin/python3

import sys
import os
sys.path.append(os.path.dirname(__file__))
import time
import socket
import settings
import logging
import argparse
import subprocess
from datetime import datetime
from modules.cmcapi_wrapper import CMCAPI_Wrapper
from modules.configChecker.configChecker import ConfigChecker
from modules.data_publisher import DataPublisher
from modules.DBOps.dbops import DBOps
from modules.data_reader import DataReader
import appdirs
import multiprocessing

log = logging.getLogger(__name__)

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

class CMCLogger():

    def __init__(self,workingDirectory,logLevel,apiKey = None):
        self.__workingDirectory = workingDirectory
        self.__makeDirectoriesAsNeeded()
        self.__setupLogging(logLevel)
        self.__config = self.__loadConfiguration(apiKey)
        self.__status = self.__setupStatusFile()
        self.__database = self.__setupDatabase()
        self.__api = None
        self.__publisher = None

    def startDaemon(self,forceStart = False):
        if daemonAlreadyRunning() and not forceStart:
            return

        self.__status.setValue(settings.status_file_current_session_section_name,settings.status_file_option_successful_calls,0)
        self.__status.setValue(settings.status_file_current_session_section_name,settings.status_file_option_failed_calls,0)
        self.__status.setValue(settings.status_file_current_session_section_name,settings.status_file_option_success_rate,100.0)
        self.__createAPIandPublisher()

        while True:
            goodResponse = self.__api.getLatest()
            self.__publisher.writeStatus(self.__api.getLatestStatus())
            if goodResponse is True:
                self.__publisher.writeData(self.__api.getLatestData())
            log.info("Scheduling next API call in {} seconds".format(self.__api.secondsToNextAPICall()))
            #for i in range(self.__api.secondsToNextAPICall()):time.sleep(1)
            time.sleep(self.__api.secondsToNextAPICall())


    def fetchAndStoreData(self,apiKey = None):
        self.__createAPIandPublisher()
        goodResponse = self.__api.getLatest(apiKey)
        self.__publisher.writeStatus(self.__api.getLatestStatus())
        if goodResponse is True:
            self.__publisher.writeData(self.__api.getLatestData())
        return goodResponse

    def writeCustomStatus(self,status):
        self.__createAPIandPublisher()
        self.__publisher.writeStatus(status)

    def dataRequest(self,request):
        reader = DataReader(self.__status,self.__database,self.__config)
        print(reader.processRequest(request))

    def getDatabase(self):
        return self.__database

    def getStatusFile(self):
        return self.__status

    def getConfigFile(self):
        return self.__config

    def __createAPIandPublisher(self):
        if self.__api is None:
            self.__api = CMCAPI_Wrapper(self.__config);
        if self.__publisher is None:
            self.__publisher = DataPublisher(self.__status,self.__database)

    def __setupLogging(self,logLevel):
        loggingFile = os.path.join(self.__workingDirectory,settings.log_file_directory,settings.log_file_name)
        try:
            logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s: %(message)s',
                                datefmt='%m/%d/%Y %I:%M:%S%p', level=logLevel, filename=loggingFile)
        except Exception as e:
            print("Failed to create logging file. Exception '{}'".format(e), file=sys.stderr)
            raise

    def __makeDirectoriesAsNeeded(self):
        targetDirectory = os.path.join(self.__workingDirectory,settings.data_file_directory)
        self.__makeDir(targetDirectory)
        targetDirectory = os.path.join(self.__workingDirectory,settings.log_file_directory)
        self.__makeDir(targetDirectory)
        targetDirectory = os.path.join(self.__workingDirectory,settings.status_file_directory)
        self.__makeDir(targetDirectory)

    def __makeDir(self,targetDirectory):
        if not os.path.exists(targetDirectory):
            try:
                log.debug("Creating new directory '{}'".format(targetDirectory))
                os.makedirs(targetDirectory)
            except OSError as e:
                log.error("Cannot create directory '{}'. Exception '{}'".format(targetDirectory,e))
                raise

    def __loadConfiguration(self,apiKey):
        config = ConfigChecker()
        config.setExpectation(settings.API_section_name,settings.API_option_private_key,str,settings.API_option_privatate_key_default)
        config.setExpectation(settings.API_section_name,settings.API_option_conversion_currency,str,settings.API_option_conversion_currency_default)
        config.setExpectation(settings.API_section_name,settings.API_option_conversion_currency_symbol,str,settings.API_option_conversion_currency_symbol_default)
        config.setExpectation(settings.API_section_name,settings.API_option_start_index,int,settings.API_option_start_index_default)
        config.setExpectation(settings.API_section_name,settings.API_option_end_index,int,settings.API_option_end_index_default)
        config.setExpectation(settings.API_section_name,settings.API_option_interval,int,settings.API_option_interval_default)
        config.setExpectation(settings.general_section_name,settings.general_option_status_file_format,str,settings.general_option_status_file_format_default)


        fileLocation = os.path.join(self.__workingDirectory, settings.input_configuation_filename)
        config.setConfigurationFile(fileLocation)

        if apiKey is not None:
            config.setValue(settings.API_section_name,settings.API_option_private_key,apiKey)

        if config.writeConfigurationFile(fileLocation) is False:
            log.critical("Failed to create required configuration file, exiting.")
            raise
        return config

    def __setupStatusFile(self):
        status = ConfigChecker()
        status.setExpectation(settings.status_file_last_call_section_name,settings.status_file_option_timeStamp,str,datetime.now().isoformat())
        status.setExpectation(settings.status_file_last_call_section_name,settings.status_file_option_error_code,int,0)
        status.setExpectation(settings.status_file_last_call_section_name,settings.status_file_option_error_message,str,'')
        status.setExpectation(settings.status_file_last_call_section_name,settings.status_file_option_elapsed,int,0)
        status.setExpectation(settings.status_file_last_call_section_name,settings.status_file_option_credit_count,int,0)
        status.setExpectation(settings.status_file_last_failed_secion_name,settings.status_file_option_timeStamp,str,'')
        status.setExpectation(settings.status_file_last_failed_secion_name,settings.status_file_option_error_code,int,0)
        status.setExpectation(settings.status_file_last_failed_secion_name,settings.status_file_option_error_message,str,'')
        status.setExpectation(settings.status_file_last_failed_secion_name,settings.status_file_option_elapsed,int,0)
        status.setExpectation(settings.status_file_last_failed_secion_name,settings.status_file_option_credit_count,int,0)
        status.setExpectation(settings.status_file_current_session_section_name,settings.status_file_option_health,float,100.0)
        status.setExpectation(settings.status_file_current_session_section_name,settings.status_file_option_successful_calls,int,0)
        status.setExpectation(settings.status_file_current_session_section_name,settings.status_file_option_failed_calls,int,0)
        status.setExpectation(settings.status_file_current_session_section_name,settings.status_file_option_success_rate,float,100.0)
        status.setExpectation(settings.status_file_all_time_section_name,settings.status_file_option_successful_calls,int,0)
        status.setExpectation(settings.status_file_all_time_section_name,settings.status_file_option_failed_calls,int,0)
        status.setExpectation(settings.status_file_all_time_section_name,settings.status_file_option_success_rate,float,100.0)

        fileLocation = os.path.join(self.__workingDirectory,settings.status_file_directory, settings.status_file_name)
        status.setConfigurationFile(fileLocation)
        if not status.writeConfigurationFile(fileLocation):
            log.critical("Failed to create required status file, exiting")
            raise
        return status

    def __setupDatabase(self):
        fileLocation = os.path.join(self.__workingDirectory,settings.data_file_directory,settings.database_file_name)
        database = DBOps(fileLocation)
        if not database.exists():
            log.critical("Failed to create required database file, exiting")
            raise
        return database

def createArguments(parser):
    parser.add_argument('-a','--api_key',
            nargs=1,
            help="Supply the Coin Market Cap API key to be used. This key is stored for subsequent use.",
            default = None)
    parser.add_argument('-q','--query',
            nargs='+',
            help="Query information about one or more cyptocurrency symbols. Can be combined with -j and -d to modify the output format.")
    parser.add_argument('-w','--working_directory',
            nargs=1,
            help="Specify the directory to setup the configuration, status and database files. If no supplied, set to user configuration directory.",
            default = None)
    parser.add_argument('-k','--kill',
            action='store_true',
            help="Kills any running CMCLogger daemon",
            default = False)
    parser.add_argument('-g','--generate_config',
            action='store_true',
            help="Generates the neccessary configuration files.")
    parser.add_argument('-s','--status',
            action='store_true',
            help="Get the status of the CMCLogger, can be combined with -j and -l to modify the output format.")
    parser.add_argument('-d','--detail',
            action='store_true',
            help="To be used with -s and -q options. Outputs verbose options for the specified symbols or logger status.")
    parser.add_argument('-j','--json',
            action='store_true',
            help="To be used with -s and -q options. Outputs symbol or status information in JSON format.")
    parser.add_argument('-l','--log',
            nargs=1,
            help="Specify the log level, must be one of either DEBUG, INFO, WARNING, ERROR or CRITICAL. The default level is INFO")

def processLogLevel(level):

    if level == 'DEBUG':
        return logging.DEBUG
    elif level == 'INFO':
        return logging.INFO
    elif level == 'WARNING':
        return logging.WARNING
    elif level == 'ERROR':
        return logging.ERROR
    elif level == 'CRITICAL':
        return logging.CRITICAL
    else:
        return logging.INFO

def processQuery(args,cmcLogger):

    request = dict()
    if args.json is True:
        request[settings.data_query_format] = settings.data_query_format_json
    else:
        request[settings.data_query_format] = settings.data_query_format_stdout

    if args.detail is True:
        request[settings.data_query_detail] = settings.data_query_detail_long
    else:
        request[settings.data_query_detail] = settings.data_query_detail_short

    request[settings.data_query_type] = settings.data_query_type_price

    if args.query is not None:
        for symbol in args.query:
            request[settings.data_query_tag] = symbol
            cmcLogger.dataRequest(request)

    if args.status is True:
        request[settings.data_query_type] = settings.data_query_type_status
        cmcLogger.dataRequest(request)

    sys.exit()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    createArguments(parser)
    args = parser.parse_args()

    if args.kill:
        subprocess.Popen(['killall','CMCLogger.py'])
        sys.exit()

    if args.working_directory is not None:
        workingDirectory = args.workingDirectory
    else:
        workingDirectory = appdirs.user_config_dir(settings.appNameDirectory)

    if args.log is not None:
        logLevel = processLogLevel(args.log[0])
    else:
        logLevel = logging.INFO

    if args.api_key is not None:
        api_key = args.api_key[0]
    else:
        api_key = None

    try:
        cmcLogger = CMCLogger(workingDirectory,logLevel,api_key)
    except:
        log.CRITICAL("Failed to start logger module, exiting")
        print("Failed to start logger module, exiting")
        sys.exit()

    if args.generate_config is True:
        sys.exit()

    if args.query is not None or args.status:
        processQuery(args,cmcLogger)

    cmcLogger.startDaemon()
