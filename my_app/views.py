from my_app import fetcher
from django.http import HttpResponse
from django import forms
from django.views.decorators.csrf import csrf_exempt
import requests
import json
import sqlite3


def index(request):
    return HttpResponse('<html><body><form action="/submit" method="post"><textarea type="text" name="tickets"></textarea><br><input type="checkbox" name="search" value="Search">View database<br><input type="submit" value="Submit"></form><br><a href="./list" target="blank">Available tickers</a></body></html>')

@csrf_exempt
def post(request):
    ticketsToSearch = request.POST.get('tickets')
    search =  request.POST.get('search')

    if search == "Search":
        content  = "<html><body><table>"

        con = sqlite3.connect('db.sqlite')
        cur = con.cursor()
            
        for ticker in ticketsToSearch.splitlines():
            ticker = ticker.strip()
            if not ticker:
                continue
            cur.execute("select * from cash_flow where ticker=:ticker", {"ticker": ticker})
            data = cur.fetchall()
            for row in data:
                content  += "<tr>"
                content  += "<td>" + row[0] + "</td>"
                content  += "<td>" + row[1] + "</td>"
                content  += "<td>" + row[2] + "</td>"
                content  += "<td>" + str(row[3]) + "</td>"
                content  += "</td>"


        content  += "</table></body></html>"

        return HttpResponse(content)

    else:
        for ticker in ticketsToSearch.splitlines():
            ticker = ticker.strip()
            if not ticker:
                continue
            fetcher.get_edgar_data(ticker)
            

    return HttpResponse('<html><body><form action="/submit" method="post"><textarea type="text" name="tickets"></textarea><br><input type="checkbox" name="search" value="Search">View database<br><input type="submit" value="Submit"></form><br><a href="./list" target="blank">Available tickers</a></body></html>')



def list(request):
    content  = "<html><body><table>"

    con = sqlite3.connect('db.sqlite')
    cur = con.cursor()
        
    cur.execute("select distinct ticker from cash_flow")
    data = cur.fetchall()
    for row in data:
        content  += "<tr>"
        content  += "<td><a href='./view?ticker=" + row[0] + "' target='_blank'>" + row[0] + "</a></td>"
        content  += "</td>"

    content  += "</table></body></html>"
    return HttpResponse(content)



def view(request):
    content  = "<html><body><table>"

    con = sqlite3.connect('db.sqlite')
    cur = con.cursor()
        
    ticker = request.GET.get('ticker')

    cur.execute("select * from cash_flow where ticker=:ticker", {"ticker": ticker})
    data = cur.fetchall()
    for row in data:
        content  += "<tr>"
        content  += "<td>" + row[0] + "</td>"
        content  += "<td>" + row[1] + "</td>"
        content  += "<td>" + row[2] + "</td>"
        content  += "<td>" + str(row[3]) + "</td>"
        content  += "</td>"


    content  += "</table></body></html>"

    return HttpResponse(content)