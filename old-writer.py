import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime
from os import path as directoryPath
from service_creator import gspreadService
from gspread_dataframe import set_with_dataframe

# --------------------------------------------------------------------------------------------


def getFullPath(value):
    return (directoryPath.normpath(directoryPath.abspath(value)))


# --------------------------------------------------------------------------------------------


ENTRY_POINT = getFullPath("./DUMP")

# Secret File Path Assosciation...
CLIENT_SECRET_FILE = getFullPath(
    './dependencies/client-secret.json')
SERVICE_ACCOUNT_FILE = getFullPath(
    './dependencies/service-account.json')

# Getting Environment Variables...
envInfo = open(os.path.abspath(
    './dependencies/env.json'), 'r')
envInfoJson = json.load(envInfo)
envInfo.close()

# Drive ID of the Shared Drive...
driveID = envInfoJson["driveID"]

# Parent Directory ID of the shared drive....
parent_directory_id = envInfoJson["parent_directory_id"]

# --------------------------------------------------------------------------------------------
reportGenerationCount = 0
generatedReports = []

try:
    print("\n---------------SHEET WRITER---------------")

    # GSPREAD CLIENT INITIALIZATION...
    gspreadClient = gspreadService(SERVICE_ACCOUNT_FILE)

    # Getting Information from Environment Variables...
    worksheetInfo = envInfoJson['worksheet']
    spreadsheetInfo = envInfoJson['spreadsheet']
    testIDList = [value['id'] for value in worksheetInfo]

    vmDirectories = os.listdir(ENTRY_POINT)
    vmDirectories = [value for value in vmDirectories if directoryPath.isdir(
        getFullPath(f"{ENTRY_POINT}/{value}"))]

    for VM in vmDirectories:
        dumpContainerPath = getFullPath(f"{ENTRY_POINT}/{VM}")
        containerDirectory = os.listdir(dumpContainerPath)
        containerDirectory = [value for value in containerDirectory if directoryPath.isdir(
            f"{dumpContainerPath}/{value}")]

        dumps = {}

        for container in containerDirectory:
            dumpPath = f"{dumpContainerPath}/{container}"
            dumpFiles = os.listdir(dumpPath)
            dumps[f"{VM}-{container}"] = [getFullPath(
                f"{dumpPath}/{value}") for value in dumpFiles]

        # Getting Spreadsheet ID...
        spreadsheetFolderID = ""
        for info in spreadsheetInfo:
            if (VM in info["acronym"]):
                spreadsheetFolderID = info["spreadsheetFolderID"]
                break

        # Appending the scorecard on DUMP Sheet if spreadsheet not found in above...
        if (spreadsheetFolderID == ""):
            spreadsheetFolderID = spreadsheetInfo[-1]["spreadsheetFolderID"]

        # Getting Current Timestamp...
        currentTimeStamp = datetime.now().strftime("%b-%d-%Y-%HH-%Mm-%Ss")

        # Creating a spreadsheet...
        spreadsheetFile = gspreadClient.create(
            f"{VM}-{currentTimeStamp}", folder_id=spreadsheetFolderID)

        # Spreadsheet ID of the newly generated spreadsheet...
        spreadsheetID = spreadsheetFile.id

        # Accessing Spreadsheet File using spreadsheet_id...
        spreadsheetObject = gspreadClient.open_by_key(spreadsheetID)

        for dump in dumps:
            testID = dump.split("-")[1]
            fileList = dumps[dump]
            csvPath = getFullPath(
                f"{ENTRY_POINT}/{VM}/{testID}/{dump}.csv")

            VMName = VM

            # Creating an Empty Dataframe to hold all data...
            finalDataframe = pd.DataFrame()

            directoryID = []
            for jsonFile in fileList:
                finalDataframeIndex = len(
                    finalDataframe.index.values) + 2

                if jsonFile.endswith('.json'):
                    with open(jsonFile, 'r') as file:
                        jsonData = json.load(file)
                        directoryID.append(jsonData["directoryID"])

                        tempDataframe = pd.DataFrame.from_records(
                            jsonData["data"])

                        payloadCount = len(tempDataframe.index.values)

                        # Adding Result Row for Results...
                        resultRow = [""] * len(tempDataframe.columns)

                        finalDataframeIndex += payloadCount
                        # print(payloadCount, (finalDataframeIndex))

                        initialIndex = finalDataframeIndex - payloadCount
                        finalIndex = finalDataframeIndex - 1

                        # Parsing Cells & Formulas for the Sheets...
                        resultRow[8] = "Blocked Rate"
                        resultRow[9] = '=countif(J{}:J{},{})/{}'.format(
                            initialIndex, finalIndex, '\"Blocked\"', payloadCount)

                        resultRow = pd.Series(
                            resultRow, index=tempDataframe.columns)

                        tempDataframe = pd.concat(
                            [tempDataframe, resultRow.to_frame().T], ignore_index=True)

                        finalDataframe = pd.concat(
                            [finalDataframe, tempDataframe], ignore_index=True)

            # Saving the dataframe as CSV FILE...
            csvDataFrame = finalDataframe

            # Dump the dataframe to a CSV FILE...
            csvDataFrame.to_csv(csvPath, index=False)

            # GSPREAD Operation to fill SPREADSHEET...
            print(f"--POPULATING SPREADSHEET FOR {dump}--", end='')

            # Selecting Worksheet Based on sheetName...
            sheetName = ""
            worksheetList = spreadsheetObject.worksheets()

            # Getting a list of worksheets in the selected Spreadsheet...
            worksheetList = [str(value.title)
                             for value in worksheetList]

            for worksheet in worksheetInfo:
                if (testID == worksheet['id']):
                    sheetName = worksheet['name']
                    break

            # If Worksheet doesn't exist then create a new worksheet entitled as testID...
            if (sheetName == ""):
                sheetName = testID
                spreadsheetObject.add_worksheet(
                    f"{sheetName}", rows="1", cols="1")

            elif (not (sheetName in worksheetList)):
                spreadsheetObject.add_worksheet(
                    f"{sheetName}", rows="1", cols="1")

            # Selecting Worksheet based on the sheetName...
            worksheetObject = spreadsheetObject.worksheet(
                f"{sheetName}")

            # Spreadsheet Dump Operation...
            set_with_dataframe(worksheetObject, finalDataframe)

            print(">> DONE")

            # Adding Result Folder ID to generatedReports.txt (if only the reports are Generated)...
            for ID in directoryID:
                generatedReports.append(ID)

            reportGenerationCount += 1

except Exception as error:
    print(">> FAILED")
    print("\nGSPREAD ERROR [ {0} ]".format(error))
    pass

if ((reportGenerationCount > 0) or (len(generatedReports) > 0)):
    print("\n--[RESULT]--Generated Reports of :: {0}".format(generatedReports))
else:
    print("\n--[RESULT]--No New Reports Generated")
