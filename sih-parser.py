import sys
from datetime import datetime, timedelta
import os
import requests
from bs4 import BeautifulSoup
import csv

def fetch_last_execution():
    if os.path.exists("last_execution.log"):
        with open("last_execution.log", 'r') as file:
            time = file.read().strip()
            return datetime.fromisoformat(time)

def fetch_new_batch():
    last_exec_time = fetch_last_execution()
    if last_exec_time is not None:
        time_interval = timedelta(hours=24)
        if datetime.now() - last_exec_time < time_interval:
            print("It's too soon, son.")
            print("Time since last fetch: ", (datetime.now() - last_exec_time))
            print("Ideally keep fetches to once per day")
            sys.exit()
            return
        
    print("Fetching...")
    # Seems to reject requests with missing User Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
    }
    
    data = requests.request(method='GET', url='https://www.sih.gov.in/sih2024PS', verify=False, headers=headers)
    if data.status_code != 200:
        print("Failed to fetch new data")
        sys.exit(data.status_code)
        
    # print(data.content)

    with open('response.html', 'w', encoding='utf-8') as file:
        file.write(data.text)
    


def parse(PS):

    PS = PS.find_all("td", recursive=False) 
    # print(PS)
    SrNo = PS[0].text
    
    Organisation = PS[1].text
    # print(f"Problem Statement (yet to handle) : {PS[2]}")
    
    # extracting the title from the weird col
    Title = PS[2].find('a').text
    
    Category = PS[3].text
    PSno = PS[4].text
    Submissions = PS[5].text
    Theme = PS[6].text
    
    
    row =[SrNo,Organisation,Title,Category, PSno, Submissions,Theme, datetime.now().strftime("%Y-%m-%d %H:%M:%S")] #adding a timestamp so I can drill down in power BI
    
    # print(row)
    return row

def write_data():
    with open('response.html', 'r', encoding='utf-8') as HTML_FILE:
        response = HTML_FILE.read()
        print(f"Length of file:  {len(response):,} lines")  # too fucking long of a file 😭
                                                            # this makes me want to leave the country (日本で住む方がいい)
        
        soup = BeautifulSoup(response, 'lxml')
        
        PS_LIST = soup.select('tbody > tr')
        print(f"No. of PS: {len(PS_LIST):,}")
        
        rows = []
        for PS in PS_LIST:
            row = parse(PS) 
            rows.append(row)        
        
        with open('sih-data.csv', 'a', newline='') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
            # heading = ['Sr No', 'Organisation', 'Title', 'Category', 'PS No', 'Submissions', 'Theme', 'Time']
            # writer.writerow(heading) 
            writer.writerows(rows) 
           
           
    

        with open('last_execution.log', 'w') as file:
            file.write(datetime.now().isoformat())
    
             
        

    
def main():
    fetch_new_batch()
    write_data()
    
    
if __name__ == '__main__':
    main()
    
    

