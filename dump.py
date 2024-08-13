import io
import os
import sys
import json
import time
import subprocess
import numpy as np
import pandas as pd
from datetime import datetime
from os import path as directoryPath
from service_creator import Create_Service, Create_Service2

# --------------------------------------------------------------------------------------------


def getFullPath(pathValue):
    return (os.path.normpath(os.path.abspath(pathValue)))


# --------------------------------------------------------------------------------------------

# Secret File Path Assosciation...
CLIENT_SECRET_FILE = getFullPath(
    './dependencies/client-secret.json')
SERVICE_ACCOUNT_FILE = getFullPath(
    './dependencies/service-account.json')

# API Specification...
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

# subDirectories = {"key_name":"Enter the directory name to be listed in the report"}

# Example of subDirectories/Files...
subDirectories = {
    "video": "recordings",
    # "response": "responses",
    "image": "screenshots",
    "pcap": "packetcaptures",
    "urlInfo": "urlInfo.csv"
}

# Getting Environment Variables...
envInfo = open(getFullPath(
    './dependencies/env.json'), 'r')
envInfoJson = json.load(envInfo)
envInfo.close()

# Drive ID of the Shared Drive...
driveID = envInfoJson["driveID"]

# Variable to store Parent Directory ID of the shared drive....
VMInfo = envInfoJson["VMInfo"]

# Validating script arguments...
CODE = ""
try:
    CODE = sys.argv[1].strip()

except Exception as error:
    print("--ERROR--'python dump.py <ENTRY_POINT>' IS REQUIRED")
    exit()

FILTER = ""
try:
    FILTER = sys.argv[2].strip()

except Exception as error:
    print("--ERROR--'FILTER IS REQUIRED")
    exit()

# Getting parent_directory_id based on VM Name...
parent_directory_id = ""
for item in VMInfo:
    if (CODE == item["name"]):
        parent_directory_id = item["parent_directory_id"]
        break

if (parent_directory_id == ""):
    print("--ERROR--INVALID ENTRY POINT")
    exit()

# --------------------------------------------------------------------------------------------

# service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
service = Create_Service2(SERVICE_ACCOUNT_FILE, API_NAME, API_VERSION, SCOPES)


def idreturner(id, df, column):
    try:
        if id in df[column].unique():  # Faster check for existence in the column
            index = df[df[column] == id].index[0]
            return df.iat[index, df.columns.get_loc('id')]
        else:
            return None
    except Exception as error:
        print("Error in ID Returner Function::: ", error)


def sharetoanyone(drive_service, folderId):
    try:
        # Create permission for anyone with the link
        permission = {
            'type': 'anyone',
            'role': 'reader',
        }

        # Create the permission for the folder
        drive_service.permissions().create(
            fileId=folderId,
            body=permission
        ).execute()

        return

    except Exception as error:
        print("Error in sharetoanyone Function::: ", error)
        pass


def lister(service, driveId, parentId, sleeptime=None):

    if sleeptime:
        time.sleep(sleeptime)

    try:
        query = f"parents ='{parentId}' and trashed=False"

        response = service.files().list(
            q=query,
            orderBy='name',
            fields="files(id, name, mimeType)",
            includeItemsFromAllDrives=True,
            corpora='drive',
            driveId=driveId,
            supportsAllDrives=True,
            pageSize=1000
        ).execute()

        files = response.get('files', [])

        df = pd.DataFrame(files)
        df.fillna('N/A', inplace=True)

        return df.to_dict('records')

    except Exception as error:
        print("Error in lister Function::: ", error)


def directoryInfo(directoryObject, directoryName):
    try:
        return next((obj for obj in directoryObject if directoryName in obj.get('name', '')), None)
    except Exception as error:
        print("Error in directoryInfo Function::: ", error)
        return None


def subDirectoryInfo(parentDirectory):
    try:
        test_name = parentDirectory['name']
        test_folder_id = parentDirectory['id']
        # test_name = directory['name']
        # print("\nTest Name:::", test_name)

        # Getting Sub-Directories & Files within Test Results
        test_subDirectories = lister(service, driveID, test_folder_id, 1)

        keys_mapping = {
            "recordingFolderID": subDirectories["video"],
            # "responseFolderID": subDirectories["response"], # commented-out key for future use
            "screenshotFolderID": subDirectories["image"],
            "pcapFolderID": subDirectories["pcap"],
            "urlInfoID": subDirectories["urlInfo"]
        }

        resultObject = {
            "test_name": test_name,
            "test_folder_id": test_folder_id,
        }

        for key, dir_name in keys_mapping.items():
            info = directoryInfo(test_subDirectories, dir_name)
            resultObject[key] = info['id'] if info else None
            # Print statements corresponding to each directory (commented-out for future use)
            # print(f"{key}:::", resultObject[key])

        return resultObject

    except Exception as error:
        print("Error in subDirectoryInfo Function::: ", error)
        pass


# --------------------------------------------------------------------------------------------

# currentDate = datetime.now().strftime('%b-%d-%Y')
# Gets list of directories within the parent_directory...
resultDirectories = lister(service, driveID, parent_directory_id)

# Checking and creating file 'generatedDumps.txt' if not exists
dumps_path = getFullPath('./dependencies/generatedDumps.txt')
if not directoryPath.isfile(dumps_path):
    print("--generatedDumps.txt File Created!--")
    with open(dumps_path, "x"):
        pass

# Creating Directory to Store DataFrame Dumps
dump_dir_path = getFullPath(f"./DUMP")
if not directoryPath.exists(dump_dir_path):
    os.mkdir(dump_dir_path)

# Creating .gitignore file if accidentally deleted
gitignore_path = getFullPath(f"./DUMP/.gitignore")
if not directoryPath.exists(gitignore_path):
    with open(gitignore_path, "w") as f:
        f.write("*\n!.gitignore")

# Reading the file and creating a list
with open(dumps_path, 'r', encoding="utf-8") as reportFile:
    alreadyDumpedList = [value.strip()
                         for value in reportFile if value.strip()]

dumpCount = 0
generatedDumps = []

print("\n-------------DUMP GENERATOR-------------")


for directory in resultDirectories:
    try:
        directoryID = str(directory["id"])
        directoryName = str(directory["name"])
        if (not (directoryName in alreadyDumpedList) and (FILTER in directoryName) and (directory["mimeType"] == 'application/vnd.google-apps.folder')):

            testDirectory = subDirectoryInfo(directory)

            # Gathering IDs for further Operation...
            testDirectoryID = testDirectory['test_folder_id']
            test_name = testDirectory['test_name']
            recordingFolderID = testDirectory['recordingFolderID']
            # responseFolderID = testDirectory['responseFolderID']
            screenshotFolderID = testDirectory['screenshotFolderID']
            pcapFolderID = testDirectory['pcapFolderID']
            urlInfoID = testDirectory['urlInfoID']

            if (urlInfoID):

                jsonData = {
                    "timestamp": "",
                    "directoryID": f"{testDirectoryID}"
                }

                # Populating jsonData with Test Information...
                splitValue = test_name.split("_")
                testName = splitValue[0]
                timestamp = splitValue[1]
                testInfo = testName.split("-")
                testID = testInfo[1]

                jsonData["timestamp"] = f"{timestamp}"
                jsonData["VMName"] = f"{testInfo[0]}"
                jsonData["testID"] = f"{testInfo[1]}"
                jsonData["batchID"] = f"{testInfo[2]}"
                jsonData["iterationID"] = f"{testInfo[3]}"

                dumpContainer = f"./DUMP/{testInfo[0]}"

                # Creating Directory For VM Specific Dumps...
                if (directoryPath.exists(getFullPath(dumpContainer)) is False):
                    os.mkdir(getFullPath(dumpContainer))

                print("\nTest Name::: [ {0} ]".format(test_name))

                # Retrieving List of Files in Respective Directories as Pandas Dataframes...
                print("\n--Retrieving Files List from Subdirectories--", end='')

                recordingList = lister(service, driveID, recordingFolderID, 1)
                recordingList = pd.DataFrame(recordingList)

                # responseList = lister(service, driveID, responseFolderID, 1)
                # responseList = pd.DataFrame(responseList)

                screenshotList = lister(
                    service, driveID, screenshotFolderID, 1)
                screenshotList = pd.DataFrame(screenshotList)

                pcapList = lister(service, driveID, pcapFolderID, 1)
                pcapList = pd.DataFrame(pcapList)

                print(">> DONE")

                # List Information...
                # print("\nRecording List:::", recordingList)
                # print("\nResponse List:::", responseList)
                # print("\nScreenshot List:::", screenshotList)
                # print("\nPCAP List:::", pcapList)

                print("--Gathering urlInfo.csv Information--", end='')

                # Getting urlInfo.csv File Contents...
                request = service.files().get_media(fileId=urlInfoID)
                csvFile = request.execute()
                csvFile = csvFile.decode("utf-8")
                csvFile = io.StringIO(csvFile)

                # Converting CSV File contents to Pandas Dataframe...
                resultDataframe = pd.read_csv(csvFile)
                resultDataframe = resultDataframe.replace(np.nan, '')
                resultDataframe = resultDataframe.astype(str)

                print(">> DONE")

                # Formatting Columns of the resultDataframe...
                resultDataframe = resultDataframe.rename(
                    columns=lambda x: x.replace('.1', '') if '.1' in x else x)

                print("--PARSING SPREADSHEET INFORMATION--", end='')

                for index, result in resultDataframe.iterrows():
                    index = int(index)
                    resultId = f"{result['ID']}-{result['Payload ID']}"

                    # if (len(str((result['Response Code']))) == 0):
                    #     resultDataframe.loc[index, 'Response Code'] = 'N/A'

                    if (result['File Downloaded'] == "False"):
                        resultDataframe.loc[index,
                                            'Downloaded File Name'] = 'N/A'
                        # resultDataframe.loc[index,
                        #                     'Downloaded File MD5'] = 'N/A'
                        resultDataframe.loc[index,
                                            'Downloaded File Sha256'] = 'N/A'
                        resultDataframe.loc[index,
                                            'Downloaded File Size'] = 'N/A'
                        resultDataframe.loc[index,
                                            'File First Submission Date'] = 'N/A'
                        resultDataframe.loc[index,
                                            'File Last Submission Date'] = 'N/A'
                        resultDataframe.loc[index,
                                            'File Last Analysis Date'] = 'N/A'

                    # Parsing Search IDs...
                    recordingSearchId = f"{resultId}.mp4"
                    # responseSearchId = f"{resultId}.json"
                    screenshotSearchId = f"{resultId}.jpeg"
                    pcapSearchId = f"{resultId}.pcap"

                    # Gathering File IDs...
                    recordingID = idreturner(
                        recordingSearchId, recordingList, 'name')
                    # responseID = idreturner(
                    #     responseSearchId, responseList, 'name')
                    screenshotID = idreturner(
                        screenshotSearchId, screenshotList, 'name')
                    pcapID = idreturner(pcapSearchId, pcapList, 'name')

                    # Generating shareable links for above File IDs...
                    if (recordingID != None):
                        resultDataframe.loc[index,
                                            'Video Link'] = rf"https://drive.google.com/file/d/{recordingID}"
                    else:
                        resultDataframe.loc[index, 'Video Link'] = 'N/A'

                    # if (responseID != None):
                    #     resultDataframe.loc[index,
                    #                         'Response Link'] = rf"https://drive.google.com/file/d/{responseID}"
                    # else:
                    #     resultDataframe.loc[index, 'Response Link'] = 'N/A'

                    if (screenshotID != None):
                        resultDataframe.loc[index,
                                            'Screenshot Link'] = rf"https://drive.google.com/file/d/{screenshotID}"
                    else:
                        resultDataframe.loc[index, 'Screenshot Link'] = 'N/A'

                    if (pcapID != None):
                        resultDataframe.loc[index,
                                            'PCAP Link'] = rf"https://drive.google.com/file/d/{pcapID}"
                    else:
                        resultDataframe.loc[index, 'PCAP Link'] = 'N/A'

                finalDataframe = resultDataframe

                # Replacing all np.nan values with "N/A"
                finalDataframe.fillna('N/A', inplace=True)

                print(">> DONE")

                print("--DUMPING DATAFRAME AS JSON--", end='')

                # Storing PD to DF into jsonData...
                jsonData["data"] = finalDataframe.to_dict(orient='records')

                # folderName = "-".join(testInfo)
                jsonName = test_name + ".json"

                # Creating Directory to store JSON Data...
                jsonDumpDirectory = f"{dumpContainer}/{testID}"

                if (directoryPath.exists(getFullPath(jsonDumpDirectory)) is False):
                    os.mkdir(getFullPath(jsonDumpDirectory))

                # Dump JSON variable to JSON file...
                with open(getFullPath(f"./{jsonDumpDirectory}/{jsonName}"), 'w') as json_file:
                    json.dump(jsonData, json_file,
                              ensure_ascii=False,
                              indent=2,
                              separators=(',', ': '))

                generatedDumps.append(test_name)
                print(">> DONE")

                file = open(getFullPath(
                    './dependencies/generatedDumps.txt'), 'a')
                file.write(f"{directoryName}\n")
                file.close()

                # sharetoanyone(service, directoryID)

            else:
                print(f"\n--ERROR--urlInfo.csv Missing in [ {test_name} ]")

    except Exception as error:
        print("Error in Driver Code ::: ", error)
        pass

if ((dumpCount > 0) or (len(generatedDumps) > 0)):
    print("\n--[RESULT]--Generated Dumps of :: {0}".format(generatedDumps))
else:
    print("\n--[RESULT]--No New Dumps Generated")
