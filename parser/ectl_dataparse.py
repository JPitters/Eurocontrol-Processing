# -*- coding: utf-8 -*-
"""
Created on Tues November 3 14:49 2020
@author: Jordan Pitters
@email : jordan.pitters@fliteplan.net
"""

# !/usr/bin/env python3
from datetime import date, datetime, timedelta
import argparse
import sys, os
import time
import glob
import psycopg2
import psycopg2.extras as extras
import logging
import csv
import pandas as pd
import subprocess
import traceback
#from sqlalchemy import create_engine
from io import StringIO
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import requests
from xml.dom import minidom


# -- Logging initiatives
logger = logging.getLogger("ectl_parser")
logging.basicConfig(level=logging.ERROR)
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
# #fh = logging.FileHandler('/home/jordan/ectl/logs/ectl.log')
# fh = logging.FileHandler('/var/log/ectl_parser.log')
fh = logging.FileHandler('ectl_parser.log')
fh.setLevel(logging.DEBUG)
# #   Create a console handler with a higher log level...
# ch = logging.StreamHandler()
# ch.setLevel(logging.ERROR)
# #   Create a formatter and add it to the handlers...
formatter = logging.Formatter('%(asctime)s - thread:%(thread)d - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# ch.setFormatter(formatter)
# #   Add the handlers to the logger...
logger.addHandler(fh)
# logger.addHandler(ch)
logger.warning(" Starting ectl_processing - Version BETA-0.0.1")

WATCH_INTERVAL_SECONDS = 10

WAIT_INTERVAL_BEFORE_FILE_READ = 10 #in seconds
FILE_RETRY_MAX=5
RETRY_DELAYS=[180,120,60,30,10]


def connectToAIXMDB():
    try:
        connection = psycopg2.connect(
            host='55c95685-66bb-427c-b840-50edaa7d0c4b.3c7f6c12a66c4324800651be37a77ceb.databases.appdomain.cloud',
            port='32076',
            database='aixm',
            user='admin',
            password='Flite_Post_2020'
        )

        print("\tConnected to IBMManaged Server! AIXM database is ready...")
    except Exception as e:
        print("--- Failure connecting to SIGMET Database...")
        print("Exception %s" % e)
        traceback.print_tb(e.__traceback__)
        sys.exit(1)

    return connection


def checkTable(aixmdb, tablename):
    pgCursor = aixmdb.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        #select_query = "SELECT EXISTS(SELECT 1 FROM airsigmets WHERE airsigmets_type = '')"
        select_query = "SELECT EXISTS(SELECT 1 FROM " + tablename + ")"
        pgCursor.execute(select_query)
        tableFound = pgCursor.fetchone()
        if tableFound:
            print("\t Table exists...")
        pgCursor.close()

    except (Exception, psycopg2.DatabaseError) as e:
        print("-- Query to SIGMET Database failed --")
        print("Exception %s" % e)
        traceback.print_tb(e.__traceback__)
        pgCursor.close()
        aixmdb.close()
        sys.exit(1)

    #END-OF-FNC


def pushData(aixmdbCon, data, tablename, getID):
    pgCursor = aixmdbCon.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        if not data.empty:
            #   5) Push to the table
            print("\t Pushing data entry to... ", tablename)

            # Create a list of tupples from the dataframe values
            tuples = [tuple(x) for x in data.to_numpy()]
            # Comma-separated dataframe columns
            cols = ','.join(list(data.columns))
            # SQL quert to execute
            query  = "INSERT INTO %s(%s) VALUES %%s" % (tablename, cols)

            if getID:
                query = query + " RETURNING id"
            #print(query)
            
            extras.execute_values(pgCursor, query, tuples)
            #print("\t Submitted values to: ", tablename)

            if getID:
                return pgCursor.fetchone()[0]

    except (Exception, psycopg2.DatabaseError)  as e:
        print("-- Push to SIGMET Database failed --")
        print("Exception %s" % e)
        traceback.print_tb(e.__traceback__)
        aixmdbCon.rollback()
        pgCursor.close()
        sys.exit(1)
    #END-OF-FNC


def get_input_dict(now):
    """
    ::params::date::string - today <yyyy-mm-dd>
    """
    if hasattr(now, "strftime"):
        date = now.strftime("%Y-%m-%d")
        input_dict = {
            "date": date,
            "mapping": {
                os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        f"ectl/datasets/{date}",
                    )
                ): {
                    "patterns": [
                        "Complete_*_20??",
                        "Incremental_*_20??",
                        #"*.PERMADELTA",
                    ],
                    "submit_to_db": True,
                },
                os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        f"ectl/datasets/{date}/Incremental_*_20??",
                    )
                ): {
                    "patterns": [
                        "Navaid.BASELINE",
                        #"*.PERMADELTA",
                    ],
                    "submit_to_db": False,
                }
            },
        }
        return input_dict
    else:
        return None


def prepData(aixmdb, pre_formatted_data, tablename):
    try:
        #pre_formatted_data = {}
        #pre_formatted_data = processNavaidXML(pre_formatted_data)
        data = pd.DataFrame(pre_formatted_data)
        #data.to_csv('test.csv')
        #print(data)

    except Exception as e:
        print("-- Attempt to process data failed --")
        print("Exception %s" % e)
        traceback.print_tb(e.__traceback__)
        sys.exit(1)

    return data
    #END-OF-FNC


def processNavaidXML(db_con):
    print("parsing Navaid...")
    # NavaidData = []
    xmldoc = minidom.parse('Navaid.BASELINE')

    # In some cases, Navaid object variables may or may not have data
    gmlIDList = []
    gmlBPList = []
    gmlEPList = []
    aixmInterpList = []
    aixmTypeList = []
    aixmDesignatorList = []
    aixmNameList = []
    gmlPosSRSNameList = []
    gmlPosLonList = []
    gmlPosLatList = []
    
    # In some cases the Time Slice has an extension
    aixmExtension = [] # in each TimeSlice there is 0..1
    pointUsageID = [] # in each NavaidExtension there is 1..*
    aixmTimeSheet = [] # TimeInterval -> TimeSheet
    aixmTRefList = [] # UTC?
    aixmDayList = []
    aixmStartTimeList = [] # 00:00 - 24:00
    aixmEndTimeList = []
    gmlTEValidTBList = [] # Valid Time Begin
    gmlTEValidTEList = [] #Valid time End
    adrextRoleList = [] 
    adrextReferenceAirspaceList = [] # data is stored in xlink:href attribute as urn:uuid(4) 
    adrextReferenceAirportHeliportList = [] # data is stored in xlink:href attribute as urn:uuid(4)


    navNodes = xmldoc.getElementsByTagName('aixm:Navaid')
    if len(navNodes) > 0:

        for navaid in navNodes:
            #base NavaidTimeSlice data fields
            validtimebegin = ""
            validtimeend = ""
            interpretation = ""
            aixmTypeData = ""
            designator = ""
            aixmLocSRSName = ""
            aixmLocLatitude = ""
            aixmLocLongitude = ""
            elevation = ""
            elevationUOM = ""
            aixmName = ""

            #Additions via Extensions
            aixmTSTRef = ""
            aixmTSStartDate = ""
            aixmTSEndDate = ""
            aixmTSDay = ""
            aixmTSStartTime = ""
            aixmTSEndTime = ""
            gmlTEValidTB = validtimebegin
            gmlTEValidTE = validtimeend
            aixmTSDaylightSavingsAdjust = ""
            aixmTSExcluded = ""
            adrextRole = ""
            adrextReferenceAirspace = "" 
            adrextReferenceAirportHeliport = ""

            # --gml identifier
            nodeList = navaid.getElementsByTagName("gml:identifier")
            gmlUUIDNode = nodeList[0]
            gmlIdentifier = gmlUUIDNode.firstChild.data

            # --Navaid timeslice -> NavaidTimeSlice
            timesliceNode = navaid.getElementsByTagName("aixm:timeSlice")[0].firstChild

            ## --Valid Time -> Time Period
            validTime = timesliceNode.getElementsByTagName("gml:validTime")[0].firstChild
            ### -- Begin Time Position
            beginPos = validTime.childNodes[0]
            validtimebegin = beginPos.firstChild.data
            ### -- End Time Position
            endPos = validTime.childNodes[1]
            if len(endPos.attributes.items()) == 0:
                validtimeend = endPos.firstChild.data
            else:
                validtimeend = None
                #if endPos.attributes['indeterminatePosition'] == 'unknown':


            ## --Interpretation, Type, Designator
            interpNode = timesliceNode.getElementsByTagName("aixm:interpretation")[0]
            interpretation = interpNode.firstChild.data
            aixmTypeNode = timesliceNode.getElementsByTagName("aixm:type")[0]
            aixmTypeData = aixmTypeNode.firstChild.data
            designatorNode = timesliceNode.getElementsByTagName("aixm:designator")[0]
            designator = designatorNode.firstChild.data

            ## --Levels vary from here on out
            nodeList = timesliceNode.getElementsByTagName("aixm:location")
            if len(nodeList) == 1:
                aixmLocationNode = nodeList[0]
                elevatedPointNode = aixmLocationNode.childNodes[0]
                posNode = elevatedPointNode.firstChild # Node containing position data
                aixmLocSRSName = posNode.attributes['srsName'].value
                locationPoint = posNode.firstChild.data.split()
                aixmLocLatitude = locationPoint[0]
                aixmLocLongitude = locationPoint[1]

                nodeList = elevatedPointNode.getElementsByTagName("aixm:elevation")
                if len(nodeList) == 1:
                    elevationNode = nodeList[0]
                    elevation = elevationNode.firstChild.data
                    elevationUOM = elevationNode.attributes['uom'].values
            
            nodeList = timesliceNode.getElementsByTagName("aixm:name")
            if len(nodeList) == 1:
                aixmNameNode = nodeList[0]
                aixmName = aixmNameNode.firstChild.data
            
            # nodeList = timesliceNode.getElementsByTagName("aixm:extension")
            # #for node in nodeList:
            #     #nlist = node.getElementsByTagName("aixm:extension")
            # if len(nodeList) > 0:
            #     print(len(nodeList))
            # if len(timesliceNode.childNodes) > 7:
            #     name = ""
            #     for node in timesliceNode.childNodes:
            #         if node.tagName == 'aixm:extension':
            #             name = name + "========\n"
            #             name = name + node.tagName + ""
            #     print(name)

            nodeList = timesliceNode.getElementsByTagName("aixm:extension")
            if len(nodeList) > 0:
                adrExtensionNode = nodeList[0] # Some extensions have depth with nested extensions, the frist occurance is the outer most 
                for pointUNode in adrExtensionNode.childNodes:
                    pointUNode = pointUNode.childNodes[0] #ignore the container and get the real PointUsage Node
                    
                    timeIntervalNode = pointUNode.getElementsByTagName("aixm:timeInterval") # timeInterval -> timesheet
                    if len(timeIntervalNode) == 1:
                        timesheetNode = timeIntervalNode[0].getElementsByTagName("aixm:Timesheet")[0]
                        #print(timesheetNode)

                        aixmTRefNode = timesheetNode.getElementsByTagName("aixm:timeReference")[0]
                        aixmTSTRef = aixmTRefNode.firstChild.data
                        aixmDayNode = timesheetNode.getElementsByTagName("aixm:day")[0]
                        aixmTSDay = aixmDayNode.firstChild.data
                        aixmStartTimeNode = timesheetNode.getElementsByTagName("aixm:startTime")[0]
                        aixmTSStartTime = aixmStartTimeNode.firstChild.data
                        aixmEndTimeNode = timesheetNode.getElementsByTagName("aixm:endTime")[0]
                        aixmTSEndTime = aixmEndTimeNode.firstChild.data

                        # should exist in XML but occasionally may not?
                        nodeList = timesheetNode.getElementsByTagName("aixm:excluded")
                        if len(nodeList) == 1:
                            aixmTSExcludedNode = nodeList[0]
                            aixmTSExcluded = aixmTSExcludedNode.firstChild.data
                        
                        #in SPRINGTIME and WINTERTIME we get additional elements
                        nodeList = timesheetNode.getElementsByTagName("aixm:startDate")
                        if len(nodeList) == 1:
                            aixmTSStartDateNode = nodeList[0]
                            aixmTSStartDate = aixmTSStartDateNode.firstChild.data
                        nodeList = timesheetNode.getElementsByTagName("aixm:endDate")
                        if len(nodeList) == 1:
                            aixmTSEndDateNode = nodeList[0]
                            aixmTSEndDate = aixmTSEndDateNode.firstChild.data
                        nodeList = timesheetNode.getElementsByTagName("aixm:daylightSavingsAdjust")
                        if len(nodeList) == 1:
                            aixmTSDaylightSavingsAdjustNode = nodeList[0]
                            aixmTSDaylightSavingsAdjust = aixmTSDaylightSavingsAdjustNode.firstChild.data


                    # timesheetExtensionNode = timesheetNode.childNodes[4].firstChild
                    # timeExtensionTPNode = timesheetExtensionNode.childNodes[0].firstChild
                    # gmlTETPBeginNode = timeExtensionTPNode.childNodes[0]
                    # gmlTEValidTB = gmlTETPBeginNode.firstChild.data

                    adrextRoleNode = pointUNode.getElementsByTagName("adrext:role")[0]
                    adrextRole = adrextRoleNode.firstChild.data #childNodes[0].nodeValue
                    
                    adrextReferenceAirspaceNode = pointUNode.getElementsByTagName("adrext:reference_airspace")
                    if len(adrextReferenceAirspaceNode) == 1:
                        node = adrextReferenceAirspaceNode[0]
                        adrextReferenceAirspace = node.attributes['xlink:href'].value

                    adrextReferenceAirportHeliportNode = pointUNode.getElementsByTagName("adrext:reference_airportHeliport")
                    if len(adrextReferenceAirportHeliportNode) == 1:
                        node = adrextReferenceAirportHeliportNode[0]
                        adrextReferenceAirportHeliport = node.attributes['xlink:href'].value
                
        
            gmlIDList.append(gmlIdentifier)
            gmlBPList.append(validtimebegin)
            gmlEPList.append(validtimeend)
            aixmInterpList.append(interpretation)
            aixmTypeList.append(aixmTypeData)
            aixmDesignatorList.append(designator)
            aixmNameList.append(aixmName)
            gmlPosSRSNameList.append(aixmLocSRSName)
            gmlPosLatList.append(aixmLocLatitude)
            gmlPosLonList.append(aixmLocLongitude)


            """
                Push to database order:
                1. Point
                2. Elevated Point
                3. Navaid
                4. Time Slice
                5. Navaid TimeSlice
            """
            
            #Pushing to point
            tablename = "point"
            getID = True
            srid = 4326
            geom = "SRID=4326;POINT(" + aixmLocLongitude + " " + aixmLocLatitude + ")"
            pdata = {
                'latitude':aixmLocLatitude,
                'longitude':aixmLocLongitude,
                'srid':srid,
                'geom':geom
            }
            df = prepData(db_con, [pdata], tablename)
            pointID = pushData(db_con, df, tablename, getID)
            #print(pointID)

            #Pushing to ElevatedPoint
            tablename = "elevatedpoint"
            getID = True
            valDistanceVerticalType = ()
            #valDistanceSignedType = ()
            #verticalDatum = ""
            #veritcalAccuracy = (45,"FT")

            if elevation == "":
                valDistanceVerticalType = None
            else:
                valDistanceVerticalType = (elevation, "FLOOR", elevationUOM)

            pdata = {
                'id':pointID,
                'elevation':valDistanceVerticalType
            }
            df = prepData(db_con, [pdata], tablename)
            print(df)
            elevatedPointID = pushData(db_con, df, tablename, getID)

            #Pushing to timeSlice
            # tablename = "timeslice"
            # getID = True
            # pdata = {
            #     'validtimebegin':validtimebegin,
            #     'validtimeend':validtimeend,
            #     'interpretation':interpretation
            # }
            # df = prepData(db_con, pdata, tablename)
            # timesliceID = pushData(db_con, df, tablename, getID)

            # #Pushing to NavaidTimeSlice
            # tablename = "navaidtimeslice"
            # getID = False
            # pdata = {
            #     'idtimeslice':timesliceID,
            #     'gmlidentifier':gmlIdentifier,
            #     'type':aixmTypeData,
            #     'designator':designator,
            #     'name':aixmName,
            #     'idelevatedpoint':elevatedPointID,
            # }
            # df = prepData(db_con, pdata, tablename)
            # pushData(db_con, df, tablename, getID)

            
            ids = "point: " + pointID + " - ElevationPoint: " + elevatedPointID
            print(ids)

            # --End of loop

    # pdata = {'gmlIdentifier':gmlIDList, 
    #     'validTimeBegin':gmlBPList,
    #     'validTimeEnd':gmlEPList, 
    #     'interpretation':aixmInterpList, 
    #     'type':aixmTypeList, 
    #     'designator':aixmDesignatorList, 
    #     'name':aixmNameList,
    #     'srs_name': gmlPosSRSNameList,
    #     'longitude':gmlPosLonList,
    #     'latitude':gmlPosLatList,
    # }

    """
        elevation:
         (value, "", unit of measure)

         verticalAccuracy:
         (value, unit of measure)
    """
    #   --EOF


def processAirportHeliport(filePath):
    logger.info("parsing AirportHeliport...")
    # NavaidData = []
    xmldoc = minidom.parse(filePath)

    # Data lists that can be found in each AirportHeliport XML
    gmlIDList = []
    gmlBeginPosList = []
    gmlEndPosList = []
    aixmInterpList = []
    aixmNameList = []
    aixmLocationIndicatorICAOList = []
    aixmDesignatorIATAList = []
    aixmTypeList = []
    aixmControlTypeList = []
    gmlEPPosSRSList = [] 
    gmlEPPosLonList = [] #longitude
    gmlEPPosLatList = [] #latitude
    gmlEPElevationList = []
    gmlEPElevationUOMList = [] #unit of measure

    rootNodes = xmldoc.getElementsByTagName('aixm:AirportHeliport')
    if len(rootNodes) > 0:

        for ahPort in rootNodes:
            #base AirportHeliportTimeSlice data fields
            gmlIdentifier = ""
            validtimebegin = ""
            validtimeend = ""
            interpretation = ""
            aixmType = ""
            aixmAHName = ""
            locationIndicatorICAO = ""
            designatorIATA = ""
            controlType = ""

            #Elevated Point
            elevation = ""
            elevationUOM = ""
            positionSRSName = ""
            positionLatitude = ""
            positionLongitude = ""

            #AirportHeliportExtension
            defaultTaxiTimeUOM = ""
            defaultTaxiTime = ""
            
            #Parsing the XML...
            gmlIDNode = ahPort.getElementsByTagName('gml:identifier')
            gmlIdentifier = gmlIDNode[0].firstChild.data

            airportHeliportTimeSliceNode = ahPort.getElementsByTagName('aixm:AirportHeliportTimeSlice')
            
            timePeriodNode = airportHeliportTimeSliceNode.getElementsByTagName('gml:validTime')[0].firstChild
            beginPositionNode = timePeriodNode.childNodes[0]
            validtimebegin = beginPositionNode.firstChild.data
            endPositionNode = timePeriodNode.childNodes[0]
            if len(endPositionNode.attributes.items()) == 0:
                validtimeend = endPositionNode.firstChild.data
            else:
                validtimeend = None
                #if endPos.attributes['indeterminatePosition'] == 'unknown':

            ## --Interpretation, Type, Designator
            interpNode = airportHeliportTimeSliceNode.getElementsByTagName("aixm:interpretation")[0]
            interpretation = interpNode.firstChild.data
            aixmNameNode = airportHeliportTimeSliceNode.getElementsByTagName("aixm:name")[0]
            aixmAHName = aixmNameNode.firstChild.data
            aixmLocIndicatorNode = airportHeliportTimeSliceNode.getElementsByTagName("aixm:locationIndicatorICAO")[0]
            locationIndicatorICAO = aixmLocIndicatorNode.firstChild.data
            designatorNode = airportHeliportTimeSliceNode.getElementsByTagName("aixm:designatorIATA")[0]
            designatorIATA = designatorNode.firstChild.data
            aixmTypeNode = airportHeliportTimeSliceNode.getElementsByTagName("aixm:type")[0]
            aixmType = aixmTypeNode.firstChild.data
            aixmTypeNode = airportHeliportTimeSliceNode.getElementsByTagName("aixm:controlType")[0]
            controlType = aixmTypeNode.firstChild.data

            #Served City -> City -> +name

            #Elevated Point OBJ extension
            # Can establish connection via gml identifier
            arpNode = airportHeliportTimeSliceNode.getElementsByTagName("aixm:ARP")
            if len(arpNode) == 1:
                elevatedPointNode = airportHeliportTimeSliceNode.getElementsByTagName("aixm:ElevatedPoint")
                
                if len(elevatedPointNode) == 1:
                    posNode = elevatedPointNode[0].getElementsByTagName("gml:pos")[0]
                    positionSRSName = posNode.attributes['srsName'].value
                    locationPoint = posNode.firstChild.data.split()
                    positionLatitude = locationPoint[0]
                    positionLongitude = locationPoint[1]

                    elevationNode = elevatedPointNode[0].getElementsByTagName("aixm:elevation")[0]
                    elevationUOM = elevationNode.attribute['uom'].value
                    elevation = elevationNode.firstChild.data

            # Airport Heliport extension
            extensionNode = airportHeliportTimeSliceNode.getElementsByTagName("aixm:AirportHeliportExtension")
            if len(extensionNode) > 0:
                defaultTaxiTimeNode = extensionNode[0].firstChild
                defaultTaxiTimeUOM = defaultTaxiTimeNode.attributes['uom'].value
                defaultTaxiTime = defaultTaxiTimeNode.firstChild.data
        #end Of Parsing

    #EOF


def handleCompleteDataSet(completeDirPath):
    """
        Looks into the directory contents and processes whichever aixm feature file
        is specified. Processing is done by a service specific function.

        .BASELINE
        .PERMADELTA
    """
    #get list of files added
    filePattern = completeDirPath
    aixmFileList = glob.glob("*.BASELINE *.PERMDELTA")

    for fileName in aixmFileList:
        filePath = completeDirPath + fileName
        if "AirportHeliport" in fileName:
            #may pick up various name patterns containing this
            filePattern = filePattern
        elif "Navaid" in fileName:
            processNavaidXML(filePath)


class AIXMHandler(PatternMatchingEventHandler):
    """
        This class encapsulates the handling of fs events
        related to ectl application dowloading aixm data.
    """
    # def __init__(self, url, username, password):

    def __init__(self, dataSource, aixmdb):
        super().__init__(dataSource["patterns"])
        self.dataSource = dataSource
        self.db_con = aixmdb

    def process(self, event, fileRetry=FILE_RETRY_MAX):
        """
        event.event_type
            'modified' | 'created'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        try:
            if self.dataSource["submit_to_db"]:
                try:
                    logger.debug("Sleeping for " + str(WAIT_INTERVAL_BEFORE_FILE_READ) + " seconds...")
                    time.sleep(WAIT_INTERVAL_BEFORE_FILE_READ)
                    
                    #path = event.src_path + "/" + self.dataSoucre["patterns"]
                    path = event.src_path + "/*20??"
                    dirListing = glob.glob(path)

                    for aixmDir in dirListing:
                        path = aixmDir
                        # Submit record
                        if "Complete" in aixmDir:
                            # This is a Complete data update, this should only occur once every month.
                            logger.info(" Handling Complete data set: %s", aixmDir)
                            handleCompleteDataSet(aixmDir)
                            
                        elif "Incremental" in aixmDir:
                            # This is an Incremental data update.
                            logger.info(" Handling Incremental data set: %s", aixmDir)
                            #handleIncrementalDataSet(aixmDir)

                        else:
                            # By process of elimination, this is an unknown
                            path = ""
                            #return ?

                except pd.errors.EmptyDataError:
                    if "Complete" in event.src_path:
                        if fileRetry>0:
                            delayTime = RETRY_DELAYS[max(0,min(len(RETRY_DELAYS)-1, (fileRetry-1) ))]
                            logger.warning("File is empty. Retry number {}. Sleeping {} seconds.".format(fileRetry,delayTime))
                            time.sleep(delayTime)
                            self.process(event,fileRetry-1)
                        else:
                            logger.critical("Empty file, feed is likely corrupted...")
                    else:
                        logger.error("Empty file. Something has likely gone wrong...")
                except Exception as e:
                    logger.debug("Unexpected exception when parsing csv file")
                    logger.error(e)
            else:
                logger.debug("Not submitting records to db")
        except Exception as e:
            logger.error("Encountered an error accessing %s", event.src_path)
            logger.exception(e)

    def on_modified(self, event):
        """
        Handle files modified in watched directory
        """
        #logger.debug("On modified detected -CC")
        pass

    def on_created(self, event):
        """
        Handle new files created in watched directory
        """
        if( "info" in event.src_path ):
            #fileName= event.src_path.split('/')[-1]
            logger.info("New file addition...") # + fileName)
        self.process(event)

    def on_any_event(self, event):
        """
        Handle new files created in watched directory
        """
        #logger.debug("On any detected - CC")
        logger.debug(event)
        pass

    def on_deleted(self, event):
        """
        Handle new files created in watched directory
        """
        #logger.debug("ON deleted detected - CC")
        pass

    def on_moved(self, event):
        """
        Handle new files created in watched directory
        """
        #logger.debug("On moved detected - CC")
        pass


def main(input_dict):
    """
        Main func.
    """
    #processNavaidXML({})

    logger.debug("\t Connecting to AIXM database...")
    aixmdb = connectToAIXMDB()

    processNavaidXML(aixmdb)

    #aixmdb.commit()
    #aixmdb.close()

    # if aixmdb:
    #     observer_list = list()
    #     if "mapping" in input_dict:
    #         for key, val in input_dict["mapping"].items():
    #             # incase the dirs dont exist create them
    #             if not os.path.exists(key):
    #                 logger.info(" Creating directory: %s", key)
    #             os.makedirs(key, exist_ok=True)
    #             os.chmod(key, 0o777)
                
    #             # Create an observer to watch directories for new files / dir
    #             observer = Observer()
    #             logger.debug(" Created empty fs event watcher object: %s", str(observer))
    #             observer.schedule(AIXMHandler(val, aixmdb), key)
    #             logger.debug(" Scheduled fs event watcher: %s: %s", str(observer), key)
    #             observer.start()
    #             logger.debug(" Started fs event watcher daemon: %s", str(observer))
    #             observer_list.append(observer)
            
    #         try:
    #             while True:
    #                 time.sleep(WATCH_INTERVAL_SECONDS)
    #                 if "date" in input_dict:
    #                     if datetime.utcnow().strftime("%Y-%m-%d") != input_dict["date"]:
    #                         msg = "Interrupting program to change date."
    #                         logger.info(msg)
    #                         raise ValueError(msg)
    #                 else:
    #                     msg = "Input dictionary must contain key: 'date'"
    #                     logger.debug(msg)
    #                     raise KeyError(msg)
    #         except ValueError:
    #             for observer in observer_list:
    #                 observer.stop()
    #                 logger.info(" Stopped fs event watcher daemon: %s", key)
    #             now = datetime.utcnow()
    #             logger.info(" Re-initializing ectl_processing: date rollover:")
    #             input_dict = get_input_dict(now)
    #             main(input_dict)
    #     else:
    #         msg = "Input dictionary must contain key: 'mapping'"
    #         logger.debug(msg)
    #         raise KeyError(msg)
    # else:
    #     logger.info(" Retrying connection: %i seconds", WATCH_INTERVAL_SECONDS)
    #     logger.info(" Re-initializing ectl_parser: failed to connect to database:")
    #     time.sleep(WATCH_INTERVAL_SECONDS)
    #     now = datetime.utcnow()
    #     input_dict = get_input_dict(now)
    #     main(input_dict)


    #   --EOF


if __name__ == "__main__":
    now = datetime.utcnow()
    #main()

    # global input_dict
    input_dict = get_input_dict(now)

    if input_dict:
        logger.warning(" {} ---  Running Eurocontrol AIXM Processing script:".format(now.strftime("%d/%m/%Y %H:%M:%S")))
        main(input_dict)
    # logger.error("Could not initialize ectl processing script: no input dict:")



