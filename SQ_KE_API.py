import json
from datetime import datetime
import requests

from SQ_COMMON import readData
from SQ_COMMON import writeData


class KazanExpressPreRawData:
    def __init__(self,login):
        self.FOLDER = 'KE-API-Data'
        #self.name = name
        #self.shopID = shop
        #self.folder = folder
        #from KE
        self.login = login
        self.statement = None
        self.shop = None
        self.products = None
        self.boughts = None
        self.invoiceList = None
        self.invoice = None
        
        self.shopID = None
        self.invoiceID = None
    
    def save(self):
        writeData(f'{self.FOLDER}/{self.login}.statement.json',self.statement)
        writeData(f'{self.FOLDER}/{self.login}.shop.json',self.shop)
        writeData(f'{self.FOLDER}/{self.login}.boughts.json',self.boughts)
        
        #writeData(f'{self.FOLDER}/{self.login}.{self.shopID}.products.json',self.products)
        #writeData(f'{self.FOLDER}/{self.login}.{self.shopID}.invoiceList.json',self.invoiceList)
        #writeData(f'{self.FOLDER}/{self.login}.{self.shopID}.{self.inviceID}.invoice.json',self.invoice)
    def load(self):
        self.statement = readData(f"{self.FOLDER}/{self.login}.statement.json")
        self.shop =      readData(f"{self.FOLDER}/{self.login}.shop.json")   
        self.boughts =   readData(f"{self.FOLDER}/{self.login}.boughts.json")
        
        #self.products =  readData(f"{self.FOLDER}/{self.login}.{self.shopID}.products.json")
        #self.invoiceList=readData(f"{self.FOLDER}/{self.login}.{self.shopID}.invoiceList.json")
        #self.invoice =   readData(f"{self.FOLDER}/{self.login}.{self.shopID}.{self.inviceID}.invoice.json")
        
API_HOST = 'https://api.kazanexpress.ru/api/'

HEADERS_FOR_TOKEN = {
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,en-US;q=0.6,zh-CN;q=0.5,zh;q=0.4',
    'Authorization': 'Basic a2F6YW5leHByZXNzOnNlY3JldEtleQ==',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'api.kazanexpress.ru',
    'Origin': 'https://business.kazanexpress.ru',
    'Referer': 'https://business.kazanexpress.ru/',
    'sec-ch-ua': '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
    'sec-ch-ua-mobile': '?0',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
}

HEADERS = {
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,en-US;q=0.6,zh-CN;q=0.5,zh;q=0.4',
    'Authorization': 'Bearer 8a36237b-0335-46fe-b7e6-2b8030d3aef4',
    'Connection': 'keep-alive',
    'Host': 'api.kazanexpress.ru',
    'Origin': 'https://business.kazanexpress.ru',
    'Referer': 'https://business.kazanexpress.ru/',
    'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Cache-Control': 'no-cache',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
}

class KazanExpressAPI:
    def __init__(self,login,password):
        self.FOLDER = 'KE-API-Data'
        self.login = login
        self.password = password
        self.token = None
        self.access_token = None
        
        self.headers = None
        self.status_code = None
        self.data = None
        
        self.keRawData = KazanExpressPreRawData(self.login)
        
        self.token = readData(f"{self.FOLDER}/{self.login}.token.json")
        if self.token:
            self.access_token = self.token['access_token']
        else:
            self.getToken()
        if self.isTokenExpired():
            self.getToken()
    
    def load(self):
        #self.token = readData(f"{self.FOLDER}/{self.login}.token.json")
        #self.access_token = self.token['access_token'] if self.token else None
        self.keRawData.load()
    def save(self):
        #writeData(f"{self.FOLDER}/{self.login}.token.json",self.token)
        self.keRawData.save()
    
    def isTokenExpired(self):
        if self.token:
            now = round(datetime.now().timestamp())
            expiresIn = self.token['expires_in']+self.token['timestamp']
            if now>expiresIn:
                print(f'token expired {expiresIn-now} seconds')
            else:
                print(f'token valid {expiresIn-now} seconds = {round((expiresIn-now)/60/60/24)} days')
            return now>expiresIn
        else:
            print('no token to check')
            return None
    def getToken(self):
        payload = {
            'grant_type': 'password',
            'username': self.login,
            'password': self.password
        }
        headers = HEADERS_FOR_TOKEN
        r = None
        try:
            r = requests.post(API_HOST+'oauth/token', params=payload, headers=headers, timeout=25)
            self.status_code = r.status_code
            self.data = r
            self.headers = r.headers
            if r.status_code==200:
                if 'Content-Type' in r.headers:
                    if 'json' in r.headers['Content-Type']:
                        j = r.json()
                        j['timestamp'] = round(datetime.now().timestamp())
                        self.token = j
                        self.access_token = self.token['access_token']
                        writeData(f"{self.FOLDER}/{self.login}.token.json",self.token)
                        return j
                    else:
                        print(f"content in not json: {str(r)}")
                        return None
                else:
                    print(f"no Content-Type in headers")
                    return None
            else:
                print(f"status_code {r.status_code}")
                return None
        except (requests.ConnectionError, requests.Timeout) as exception:
            print("No internet connection.")
            return None
    def makeRequest(self,requestPath,first_try=True):
        headers = HEADERS
        headers['Authorization'] = 'Bearer '+self.access_token
        r = None
        try:
            r = requests.get(API_HOST+requestPath, headers=headers, timeout=25)
            self.status_code = r.status_code
            self.data = r
            self.headers = r.headers
            if r.status_code==200:
                if 'Content-Type' in r.headers:
                    if 'json' in r.headers['Content-Type']:
                        j = r.json()
                        return j
                    else:
                        print(f"content in not json: {str(r)}")
                        return None
                else:
                    print(f"no Content-Type in headers")
                    return None
            elif (r.status_code==401 and first_try):
                print(f"401 Unauthorized -> getToken")
                self.getToken()
                return self.makeRequest(requestPath,False)
            else:
                print(f"status_code {r.status_code}")
                return None
        except (requests.ConnectionError, requests.Timeout) as exception:
            print("No internet connection.")
            return None
    def getStatement(self):
        print("--getStatement")
        j = self.makeRequest('seller/finance/statement')
        if j!=None:
            self.keRawData.statement = j
            print(f"forWithdraw: {j['forWithdraw']}, processing: {j['processing']}")
            return j
        else:
            return None
    def getShop(self):
        j = self.makeRequest('seller/shop/')
        if j!=None:
            self.keRawData.shop = j
            return j
        else:
            return None
    def getBoughts(self,count = 200):
        j = self.makeRequest(f'seller/finance/orders?size={str(count)}&page=0&group=false&shopIds=')
        if j!=None:
            self.keRawData.boughts = j
            return j
        else:
            return None    
    def getProducts(self,shop,count = 500):
        j = self.makeRequest(f'seller/shop/{str(shop)}/product/getProducts?searchQuery=&filter=all&sortBy=id&order=descending&size={count}&page=0')
        if j!=None:
            self.keRawData.products = j
            return j
        else:
            return None    
    def getInvoices(self,shop):
        j = self.makeRequest(f'seller/shop/{str(shop)}/invoice/')
        if j!=None:
            self.keRawData.invoiceList = j
            return j
        else:
            return None
    def getInvoiceProducts(self,shop,id):
        j = self.makeRequest(f'seller/shop/{str(shop)}/invoice/getInvoiceProducts?invoiceId={str(id)}')
        if j!=None:
            self.keRawData.invoice = j
            return j
        else:
            return None
    def getProductPAGE1(self,shop,id):
        j = self.makeRequest(f'seller/shop/{str(shop)}/product?productId={str(id)}')
        if j!=None:
            return j
        else:
            return None
    def getProductPAGE2(self,shop,id):
        j = self.makeRequest(f'seller/shop/{str(shop)}/product/{str(id)}/description-response')
        if j!=None:
            self.keRawData.shop = j
            return j
        else:
            return None