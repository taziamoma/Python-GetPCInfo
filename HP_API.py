###
# warranty-example-python.py
# Author: Damon Kaswell, HP Developers Portal (Inspired by Robert Olsen)
# Description: Gets warranty information based on product number and serial number.
###

import requests
import json
import time
import dateutil.parser
import datetime

apiKey = 'Enter API key here'
apiSecret = 'Enter API secret here'
tokenBody = {'apiKey': apiKey, 'apiSecret': apiSecret, 'grantType': 'client_credentials', 'scope': 'warranty'}

###
# Input values
#
# These can come from any source. In this example, we create a dictionary of dummy
# values, but any source can be used to populate a dictionary that contains usable
# warranty information.
###
data = [
    {'sn': '[SERIAL_NUMBER]', 'pn': '[PART_NUMBER]'},
    {'sn': '[SERIAL_NUMBER_2]', 'pn': '[PART_NUMBER_2]'}
]


def _url(path):
    return 'https://css.api.hp.com' + path


# Get the access token
tokenHeaders = {'Accept': 'application/json'}
tokenResponse = requests.post(_url('/oauth/v1/token'), data=tokenBody, headers=tokenHeaders)
tokenJson = tokenResponse.json()
token = tokenJson['access_token']

# Create the batch job
jobHeaders = {
    'Accept': 'application/json',
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
}
print('Creating new batch job...')
jobResponse = requests.post(_url('/productWarranty/v2/jobs/'), data=json.dumps(data), headers=jobHeaders)
job = jobResponse.json()
print('Batch job created successfully.')
print('--------------------')
print('Job ID: ' + job['jobId'])
print('Estimated time in seconds to completion: ' + str(job['estimatedTime']))
print('')

# Wait before monitoring the job
if (job['estimatedTime'] > 1200):
    time.sleep(40)
else:
    time.sleep(20)

# Monitor the job
headers = {
    'Authorization': 'Bearer ' + token,
    'Accept-Encoding': 'gzip,deflate'
}
status = 'incomplete'
while (status == 'incomplete'):
    monitorResponse = requests.get(_url('/productWarranty/v2/jobs/' + job['jobId']), headers=headers)
    monitor = monitorResponse.json()
    if (monitor['status'] != "completed"):
        if (monitor['estimatedTime'] > 1200):
            print('Estimated time in seconds to completion: ' + str(
                monitor['estimatedTime']) + '\nNext job check in 10 minutes...\n')
            time.sleep(200)
        elif (monitor['estimatedTime'] > 600):
            print('Estimated time in seconds to completion: ' + str(
                monitor['estimatedTime']) + '\nNext job check in 5 minutes...\n')
            time.sleep(100)
        else:
            print('Estimated time in seconds to completion: ' + str(
                monitor['estimatedTime']) + '\nNext job check in 1 minute...\n')
            time.sleep(10)
    else:
        status = 'complete'

# Retrieve results
resultsResponse = requests.get(_url('/productWarranty/v2/jobs/' + job['jobId'] + '/results'), headers=headers)
results = resultsResponse.json()

print
'Batch job complete:'
print
''

today = datetime.date.today()

for r in results:
    warrantyString = ''
    statusString = 'No active warranty'
    for offer in r['offers']:
        warrantyString += warrantyString + '  Warranty: ' + offer['offerDescription'] + '\n    Start Date: ' + offer[
            'serviceObligationLineItemStartDate'] + '\n    End Date: ' + offer['serviceObligationLineItemEndDate']
        parsed = dateutil.parser.parse(offer['serviceObligationLineItemEndDate']).date()
        if today < parsed:
            statusString = 'Warranty active'

    print
    '--------'
    print
    'SERIAL NUMBER: ' + r['product']['serialNumber']
    print
    'STATUS: ' + statusString
    print
    'WARRANTIES: \n' + warrantyString + '\n'

try:
    f = open(job['jobId'] + '.json', 'w')
    print >> f, json.dumps(results)
    print
    '\nWarranty information was retrieved for ' + str(len(results)) + ' objects.\nTo view raw data, see ' + job[
        'jobId'] + '.json.'
    f.close()
except Exception:
    print
    '\nWarranty information was retrieved for ' + str(
        len(results)) + ' objects.\nRaw data could not be written to file.'
