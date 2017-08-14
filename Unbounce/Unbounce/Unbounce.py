import requests
import json
from requests.auth import HTTPBasicAuth
from pandas.io.json import json_normalize
from Utils.Time import startdate as startdate
from Utils.Time import enddate as enddate
import numpy
import pandas


#count = 1

def retrieveUnbounceLeads(pages, api_key):
    count = 0
    data = pandas.DataFrame()
    allData = pandas.DataFrame()
    #THIS FUNCTION IS THE ONE CALLED, THE WHILE RUNS TO GIVE ALL THE PAGE NAMES I WANT TO EXTRACT DATA FROM
    while (count < len(pages)):
        dataFrame2 = dataFrameLeads(data, api_key, pages[count], startdate(), enddate())
        #ALLDATA IS USED BECAUSE OF ALL THE DATAFRAMES APPENDED TO ONE ANOTHER
        allData = allData.append(dataFrame2,ignore_index=True)
        count += 1

    #SINCE THE ALLDATA DOES NOT YET HAVE ALL THE PHONE NUMBERS CLEANED I RETURN THE DATAFRAME CLEANED
    return cleanData(allData)

'''
data.to_csv('brutedata.csv', sep=',', float_format='%.0f')
'''


#RECURSIVE METHOD TO CALL API 'desde' and 'dataframe' ARE UPDATED INSIDE THE METHOD, 'page' AND 'ate' ARE RECIEVED AND DOESN'T CHANGE
def dataFrameLeads(dataFrame, api_key, page, desde, ate):

    #TRY TO CALL API, THE PROBLEM IS:
    # I CAN HAVE EXACTLY n*1000 LEADS, SO SINCE "DESDE" IS THE LAST DATE
    # IT WILL TRY TO MAKE A CALL AND IT'LL RESULT IN AN ERROR
    # THIS RETURNS A MESSAGE TO TRY LATER SO YOU CAN MAKE ALL CALLS

    try:
        #THE LIMIT IS 1000 CALLS SO THE MAX NUMBER OF ROWS IN THE DATAFRAME = 999
        response = requests.get('https://api.unbounce.com/pages/' + page + '/leads',
                                auth=HTTPBasicAuth(api_key, 'pass'),
                                params={
                                    'from': desde + '.000Z',
                                    'limit': '1000',
                                    'to': ate,
                                    'sort_order': 'asc',
                                }).json()
    except:
        return dataFrame

    #NORMALIZE JSON RESPONSE
    data = json_normalize(response, 'leads')
    '''
    datafrom = json_normalize(data['formData'])
    print datafrom
    '''

    #X AND Y ARE VARIABLES TO KNOW EXACTLY HOW MANY ROWS GOT EXTRACTED IF data['submitterIp'].str.contains('127.0.0.1') == TRUE
    x = len(data['createdAt'])

    #FILTER DATA THAT DOESNT CONTAINS 127.0.0,1 IN submitterIp Column (THAT MEANS THE LEAD WAS NOT CREATED VIA API, SO THE RESPONSE WILL BE THE SAME AS THE OTHERS)
    data = data[data['submitterIp'].str.contains('127.0.0.1') == False]
    y = len(data['createdAt'])
    maxNumber = x-y

    #DATAFORM IS A DATAFRAME CONSISTING OF ONLY FORMDATA COLUMN FROM DATA
    dataForm = data['formData']

    #NORMALIZE DATAFORM SO I CAN RETRIEVE ALL PHONE NUMBERS
    dataPhone = json_normalize(dataForm,'phone')

    #NORMALIZE DATAFORM SO I CAN RETRIEVE ALL SOURCES
    dataSource = json_normalize(dataForm,'utm_source')

    #I GOT 3 DATAFRAMES, ONE CALLED DATA WHERE I'LL RETRIEVE 'CREATEDAT' COLUMN AND 2 OTHER 1 COLUMN DATAFRAMES, ONE ONLY WITH PHONE NUMBERS AND THE OTHER WITH SOURCES
    dataFrame2 = pandas.concat([data, dataPhone, dataSource], axis=1)
    dataFrame2.drop(['extraData', 'formData', 'id', 'metadata', 'pageUuid', 'submitterIp', 'variantId'], inplace=True,
                    axis=1)

    #UPDATE 'desde' WITH THE VALUE FROM THE LAST ROW EXCLUDING WHAT COMES AFTER '+' CHARACTER IN STRING
    desde = dataFrame2.iloc[-1]['createdAt'].partition("+")[0]

    #APPEND A LOCAL DATAFRAME (DATAFRAME2) TO A DATAFRAME WHERE I STORE ALL THE DATA (DATAFRAME)
    dataFrame = dataFrame.append(dataFrame2, ignore_index=True)


    #I CAN HAVE A MAXIMUM OF 999 ROWS, EXCEPT IF I FILTER THE DATAFRAME, IF I FILTER I'LL HAVE 999-NUMBEROFROWSEXCLUDED
    # SO IF IT'S LESS FROM THIS VALUE IT MEANS I DON'T HAVE MORE DATA TO EXTRACT SO RETURN FULL DATAFRAME
    if dataFrame2['createdAt'].count() < (999-maxNumber):
        return dataFrame

    #THE SAME HAPPENS IF THE DESDE DATE IS EQUAL TO ATE
    if desde.partition("T")[0] == ate.partition("T")[0]:
        return dataFrame


    #IF NOT RETURN DATAFRAME UPDATED AND DESDE UPDATED AND CALL FUNCTION AGAIN
    return dataFrameLeads(dataFrame, api_key, page, desde, ate)

#FUNCTION TO CLEAN ALL THE NUMBER DATA
def cleanData (allData):
    #RENAME COLUMNS
    allData.columns = ['createdAt', 'phone', 'source']
    #REMOVE NULL VALUES
    allData = allData[allData['createdAt'].notnull()]
    #RETRIEVE ONLY DATA AND NOT THE TIME
    allData['createdAt'] = allData['createdAt'].apply(lambda x: x.split('T')[0])
    #FILTER ALL VALUES THAT ARE != ''
    allData = allData[allData['phone'] != '']

    #REPLACE CHARACTERS IN STRING
    allData['phone'] = allData['phone'].str.replace('-', '')
    allData['phone'] = allData['phone'].str.replace('(', '')
    allData['phone'] = allData['phone'].str.replace(')', '')
    allData['phone'] = allData['phone'].str.replace(' ', '')
    allData['phone'] = allData['phone'].str.replace('+', '')


    #RETRIEVE ALL NUMBER OF CHARACTERS
    allData['numCaract'] = allData['phone'].str.len()

    #FILTER DATA THAT ARE UPPER THAN 9 AND BELOW THAN 13
    allData = allData[allData['numCaract'] > 9]
    allData = allData[allData['numCaract'] < 13]
    allData['phone'][allData['numCaract'] == 9] = '11'+allData['phone']
    allData['phone'][allData['numCaract'] == 13] = allData['phone'].str[2:]
    allData['phone'][allData['numCaract'] == 12] = allData['phone'].str[1:]

    #UPDATE NUMBER OF CHARACTERS AFTER THE CHANGES
    allData['numCaract'] = allData['phone'].str.len()

    #FILTER EVERYTHING THAT HAVE 11 CHARACTERS AND DROP NUMCARACT COLUMN FROM DATAFRAME
    allData = allData[allData['numCaract'] == 11]
    allData.drop(['numCaract'], inplace=True, axis=1)
    return allData



#############################################################################################################
###FUNCTION FOR FUTURE RELEASES AND TO EXTRACT ALL THE DATA FROM OTHER LANDING PAGES AND NOT ONLY OPTIMISE###
#############################################################################################################
'''
def dataFrameLeads(dataFrame):
    global count
    global desde
    if (count == 1):
        response = requests.get('https://api.unbounce.com/pages/e6c87511-8eb5-4032-b353-48296c79402f/leads',
                                auth=HTTPBasicAuth('397305ee445988845498ca26fa6f16ca','pass'),
                                params={
                                'limit':'1000',
                                'sort_order':'asc',
                                }).json()




        data = json_normalize(response,'leads')
        dataform = data['formData']
        dataPhone = json_normalize(dataform, 'phone')
        dataSource = json_normalize(dataform, 'utm_source')
        dataFrame = pandas.concat([data, dataPhone, dataSource], axis=1)
        dataFrame.drop(['extraData','formData','id','metadata','pageUuid','submitterIp','variantId'], inplace=True, axis=1)
        #dataFrame.to_csv('data.csv', sep=',', float_format='%.0f')
        desde = dataFrame.iloc[-1]['createdAt'].partition("+")[0]

        if dataFrame['createdAt'].count() < 999:
            return dataFrame

        count = count+1

        return dataFrameLeads(dataFrame)
    else:

        response = requests.get('https://api.unbounce.com/pages/e6c87511-8eb5-4032-b353-48296c79402f/leads',
                            auth=HTTPBasicAuth('397305ee445988845498ca26fa6f16ca', 'pass'),
                            params={
                                'from': desde+'.000Z',
                                'limit': '1000',
                                'sort_order': 'asc',
                            }).json()
        data = json_normalize(response, 'leads')
        dataform = data['formData']
        dataPhone = json_normalize(dataform, 'phone')
        dataSource = json_normalize(dataform, 'utm_source')
        dataFrame2 = pandas.concat([data, dataPhone, dataSource], axis=1)
        dataFrame2.drop(['extraData', 'formData', 'id', 'metadata', 'pageUuid', 'submitterIp', 'variantId'], inplace=True,
                       axis=1)

        desde = dataFrame2.iloc[-1]['createdAt'].partition("+")[0]



        dataFrame = dataFrame.append(dataFrame2, ignore_index=True)

        if dataFrame2['createdAt'].count() < 999:
            return dataFrame



        return dataFrameLeads(dataFrame)
'''