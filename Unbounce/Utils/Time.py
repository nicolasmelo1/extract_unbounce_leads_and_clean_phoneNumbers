import time

def startdate():
    if (time.strftime("%d") == '01'):
        today = '01'
        currmonth = time.strftime('%m')
        month = int(currmonth) - 1
        year = time.strftime('%Y')
        if month < 10:
            return year + '-' + '0' + str(month) + '-' + today + 'T00:00:00'
        else:
            return year + '-' + str(month) + '-' + today + 'T00:00:00'
    else:
        today = '01'
        currdate = time.strftime("%Y-%m")
        return currdate + '-' + str(today) + 'T00:00:00'


def enddate():
    if (time.strftime("%d") == '01'):
        today = '31'
        currmonth = time.strftime('%m')
        month = int(currmonth) - 1
        year = time.strftime('%Y')

        if month < 10:
            return year + '-' + '0'+ str(month) + '-' + today + 'T23:59:59.999Z'
        else:
            return year + '-' + str(month) + '-' + today + 'T23:59:59.999Z'
    else:
        today = time.strftime("%d")
        if today < '11':
            yesterday = int(today) - 1
            currdate = time.strftime("%Y-%m")
            return currdate + '-' + '0' + str(yesterday) + 'T23:59:59.999Z'
        else:
            yesterday = int(today) - 1
            currdate = time.strftime("%Y-%m")
            return currdate + '-' + str(yesterday) + 'T23:59:59.999Z'