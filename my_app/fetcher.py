import requests
from bs4 import BeautifulSoup
from xlrd import open_workbook, XLRDError
from pprint import pprint
from datetime import datetime
import os
import sqlite3


head =  {'referer': 'https://www.sec.gov/', 'origin': 'https://www.sec.gov','accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9','accept-encoding': 'gzip, deflate, br','accept-language': 'en','cache-control': 'no-cache','pragma': 'no-cache','sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"','sec-ch-ua-mobile': '?0','sec-fetch-dest': 'document','sec-fetch-mode': 'navigate','sec-fetch-site': 'none','sec-fetch-user': '?1','upgrade-insecure-requests': '1','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}


def get_10k_report(link, ticker):
    r = requests.get(link, headers=head)
    fname = '{0}_10k.xlsx'.format(ticker)
    open(fname, 'wb').write(r.content)
    
    try:
        wb = open_workbook(fname)
    except XLRDError as err:
        print (err)
        return
    
    cashSheets =  [s for s in wb.sheets() if 'CONSOLI' in s.name.upper() and  'STATE' in s.name.upper() and 'CAS' in s.name.upper()]
    for sheet in cashSheets:
        dates = [sheet.cell(1, 1).value, sheet.cell(1, 2).value,sheet.cell(1, 3).value]
        print('(' + dates[0] + ')'+ '(' + dates[1] + ')' + '(' + dates[2] + ')')

        con = sqlite3.connect('db.sqlite')
        cur = con.cursor()

        for row in range(3, sheet.nrows):
            label = sheet.cell(row, 0).value
            values = [sheet.cell(row, 1).value,sheet.cell(row, 2).value,sheet.cell(row, 3).value]
            
            for vD in zip(dates, values):
                if not vD[1] or (type(vD[1]) != float and type(vD[1]) != int):
                    continue

                cur.execute("SELECT * FROM cash_flow WHERE ticker = '" + ticker + "' and yearDate = '" + vD[0] + "' and label = '" + label + "' ")
                
                if cur.fetchone():
                    continue

                query = "INSERT INTO cash_flow (ticker, yearDate, label, value) VALUES ('" +  ticker + "', '" + vD[0] + "', '" + label + "', " + str(vD[1]) + ")"
                cur.execute(query)
        
        con.commit()
        con.close() 

def get_edgar_data(ticker):
    count = 0
    is_10k = None
    excel_link = None
    found = True

    while found: 
        found = False
        while not is_10k and count < 100:

            u = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={0}&type=10-k&dateb=&owner=include&start={1}&count=100'.format(ticker, str(count))
            print(u)
            r = requests.get(u, headers=head)
            soup = BeautifulSoup(str(r.text))
            rows = soup.find_all('tr')
            comp_num = None
            for ro in rows:
                count += 1
                if not is_10k:
                    td = ro.find_all('td')
                    for d in td:
                        if str(d.text).strip() == '10-K':
                            is_10k = True

                    if is_10k:
                        links = ro.find_all('a', {"id": "interactiveDataBtn"})
                        if len(links) > 0:
                            href = links[0]['href']
                            comp_num = href.split("&cik=")[1].split("&accession_number")[0]
                            access_number = str(href.split("&accession_number=")[1].split("&")[0]).replace("-","")
                            excel_link = 'https://www.sec.gov/Archives/edgar/data/{0}/{1}/Financial_Report.xlsx'.format(comp_num, access_number)
                        
                if excel_link:
                    print(excel_link)
                    get_10k_report(excel_link, ticker)

                    is_10k = None
                    excel_link = None
                    found = True

    return print('This ticker is not available.')

#get_edgar_data('TSLA')
#get_edgar_data('AAPL')