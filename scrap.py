import requests  # get requests
import urllib3  # block ssl errore
import json  # markup for python
import csv  # write in csv file
import os  # for some nice picture in console
import time  # time sleep
# system exit - if we have problems with get url (after 10 attempts)
import sys


def retry_request(link, header):
    """ site can block user for a while if he have to much connections \n
    so we add timeout between request\n
    we have 10 attempts, then we quit from script \n
    or (if all OK) return result
     """
    i = 0
    while i < 10:
        try:
            response = requests.get(
                link, headers=header, verify=False, timeout=5)
            return response
        except:
            time.sleep(i)
            i += 1
    print('Ошибка открытия страницы - ', link)
    sys.exit()


link = 'https://www.mediawiki.org/w/api.php?action=query&prop=revisions&generator=allpages&rvprop=timestamp&gaplimit=max&format=json'

# Let them think that we are not a bot :)
header = {
    'accept': 'text/plain',
    'accept-encoding': 'gzip, deflate',
    'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,en;q=0.7',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
}

# turn of ssl errors
urllib3.disable_warnings()
# for some nice output - we count max console length (symbols)
console_columns = int(os.get_terminal_size().columns)

response = retry_request(link, header)
i = 1
print('%4d - \033[33mGet request from\033[37m \033[31m%s\033[37m' %
      (i, link[:console_columns-24]))

response_text = json.loads(response.text)

# Here we collect all results
result = {}
result.update(response_text['query']['pages'])


# Get all results, while we have more
while 'continue' in response_text:
    next_link = link + '&continue={}&gapcontinue={}'.format(
        response_text['continue']['continue'], response_text['continue']['gapcontinue'])
    response = retry_request(next_link, header)
    response_text = json.loads(response.text)
    i += 1
    # colorfull output with max length as console length
    print('%4d - \033[33mGet request from\033[37m \033[31m%s\033[37m' %
          (i, next_link[:console_columns-24]))
    result.update(response_text['query']['pages'])


print('Jobs DONE!')
print('Writing CSV file...')


# write result in csv
with open('data.csv', 'w', newline='', encoding='utf-8') as f:
    csv_file = csv.writer(f)

    for item in result:
        csv_file.writerow([result[item]['pageid'], result[item]['ns'],
                          result[item]['title'], result[item]['revisions'][0]['timestamp']])

print('Done... \nHave a nice day!')
