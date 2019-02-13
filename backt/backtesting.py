#!/usr/bin/env python3
import datetime
import json
import requests
#import pandas as pd
#import matplotlib.pyplot as plt
#from coin import Coin, ZeroCloseException
#import csv
import sys
class NocoinException(Exception):
    def _init_(self, args):
        self.args = args

class ZeroCloseException(Exception):
    def _init_(self, args):
        self.args = args
class Coin:
    number = 0
    totalUSD0 = 0.0
    currentTotalUSD = 0
    afterRebalance = 0
    iterat = 0
    startUSD = 0
    tax = 0.0018
    profit = 0
    totalTrans = 0
    sumWeights = 0
    wwic = 0
    def __init__(self, crypto, totalU=0.0, exchange0=1.0000, percent=100.0, transactionFee = 0.0018, sumWeights = 100, marketCap = False):

            if exchange0 <= 0.0:
                raise ZeroCloseException(crypto,Coin.iterat)
            self.name = crypto
            self.part0 = percent
            self.exchange0 = exchange0
            print("Coin init:{0}: {1}".format(crypto, exchange0))
            Coin.number += 1
            self.currentCoin = Coin.number
            if totalU != 0.0:
                Coin.totalUSD0 = totalU
                Coin.startUSD = totalU
            self.amountUSD = Coin.totalUSD0*self.part0/sumWeights  #100.0
            if not self.exchange0:
                self.exchange0 = 0.000000001
            self.amount = Coin.totalUSD0*self.part0/sumWeights /self.exchange0 #100.0
            self.transactionFee = transactionFee
            self.closings = (self.exchange0,)
            self.totalFee = 0
            self.marketCap = marketCap
            ####
            Coin.sumWeights = sumWeights
            Coin.totalTrans = 0
            Coin.iterat = 0
            Coin.profit = 0

  
    def addClosing(self, close):
        #try:
            if not close:
                raise ZeroCloseException(self.name, Coin.iterat)
            self.currentClose = close
            self.closings = self.closings + (close,)
            self.currentPartUSD = self.amount * close
            Coin.currentTotalUSD = Coin.currentTotalUSD + self.currentPartUSD
        #except ZeroCloseException as e:
            #print(e.args)

    
    def calcRebalance(self):
        #call after all members of this class got their addClosing method called first
        self.currentProc = self.currentPartUSD/Coin.currentTotalUSD*Coin.sumWeights# 100.0
        self.deltaProc = self.part0 - self.currentProc
        self.deltaUSD = self.deltaProc * Coin.currentTotalUSD / Coin.sumWeights #100.0
        self.deltaCrypto = self.deltaUSD/self.currentClose
        self.taxForRebalance = abs(self.deltaCrypto * self.transactionFee)
        self.taxForRebalanceUSD = abs(self.deltaUSD * self.transactionFee)
        Coin.totalTrans += self.taxForRebalanceUSD
        self.totalFee += self.taxForRebalanceUSD
        Coin.wwic += self.deltaUSD
        #print("Cur Proc: {0}%, delta Proc: {1}%, rebalance: ${2}, rebalance ({4}): {3} {4}".format(self.currentProc,self.deltaProc,self.deltaUSD,self.deltaCrypto,self.name))
    
    def rebalance(self):
        self.amountUSD = (self.currentPartUSD + self.deltaUSD) - self.taxForRebalanceUSD
        self.amount = self.amountUSD/self.currentClose - self.taxForRebalance
        self.currentCoinAmount = self.currentPartUSD/self.currentClose

    def showRebalanced(arr):
        sum = 0.0
        for x in arr:
            sum +=x.amountUSD     
        Coin.afterRebalance = sum
        Coin.currentTotalUSD = 0
        Coin.totalUSD0 = sum
        Coin.profit =  sum - Coin.startUSD
        Coin.iterat += 1
    def what(self):
        #pass
        print(self.name)
        print(self.part0)
        print("Coin number", Coin.number)
        print("total amount $: {0}".format(Coin.totalUSD0))
        print("amount of {0}: ${1}".format(self.name ,self.amountUSD))
        print("amount of {0}: {1} {0}".format(self.name, self.amount))
    def printChange(self):
        #pass
        print("Current Amount: ${0}".format(Coin.currentTotalUSD))


class CoinCan:
    can = 0
    def __init__(self, coinlist, coinWeights, coinTotal = 0.0, timestamp = 1, iterations = 1992, endDate=0, transactionFees=[], marketCaps = False):
        self.coinWeights = coinWeights
        self.coinlist = coinlist
        self.coinTotal = coinTotal
        self.timestamp = timestamp
        self.iterations = iterations
        self.endDate = endDate
        self.coinObj = []
        self.wholeData = []
        self.decisions = []
        self.roi = 0
        self.sumWeights = sum(coinWeights)
        self.error_message = ''
        if transactionFees:
            self.transactionFees = transactionFees
        else:
            self.transactionFees = [0.0018]*len(coinlist)
        self.marketCaps = marketCaps
        CoinCan.can += 1
    def toEpoch(self, tup):
        if type(tup) == tuple:
            return str(datetime.datetime(*tup).timestamp())[:-2]
        elif type(tup) == int:
            #print("Ko, ma!")
            return str(int(tup/1000))
        else:
            return 0

    def price(self, symbol, comparison_symbols=['USD'], exchange='kraken'):
        url = 'https://min-api.cryptocompare.com/data/price?fsym={}&tsyms={}'\
                .format(symbol.upper(), ','.join(comparison_symbols).upper())
        if exchange:
            url += '&e={}'.format(exchange)
        page = requests.get(url)
        data = page.json()
        
        return data
    def daily_price_historical(self, symbol, comparison_symbol, until=0, limit=1, aggregate=1, exchange=''):
        url = 'https://min-api.cryptocompare.com/data/histoday?fsym={}&tsym={}&limit={}&aggregate={}'\
                .format(symbol.upper(), comparison_symbol.upper(), limit, aggregate)
        if exchange:
            url += '&e={}'.format(exchange)
        if until:
            url+='&toTs={}'.format(until)
        #print("{0} url: {1}".format(symbol,url))
        page = requests.get(url)
        data = page.json()['Data']
        return data
    def hourly_price_historical(self, symbol, comparison_symbol, until=0, limit=1, all_data = False, aggregate=1, exchange=''):
        url = 'https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym={}&limit={}&aggregate={}'\
                .format(symbol.upper(), comparison_symbol.upper(), limit, aggregate)
        if exchange:
            url += '&e={}'.format(exchange)
        if all_data:
            url += '&allData=true'
        if until:
            url+='&toTs={}'.format(until)
        print("link {0}: {1}".format(symbol, url))
        page = requests.get(url)
        
        data = page.json()['Data']
        if page.json()['Response'] == 'Error':
            raise NocoinException(page.json()['Message'])
        #if data['Response'] == 'Error':
         #   self.error_message = data['Message']
         #   raise NocoinException(data['Message'])
        #print("dat1: {0}: {1}".format(symbol,float(data[0]['close'])))

        return data

    
    def readApi(self):
        for co in self.coinlist:
            if len(self.transactionFees) > 0:
                self.decisions.append(self.hourly_price_historical(symbol=co, comparison_symbol='USD' , until=self.toEpoch(self.endDate),  limit = self.iterations))
            #decisions.append(self.hourly_price_historical(symbol=co, comparison_symbol='USD', limit=984))
            #decisions.append(self.hourly_price_historical(symbol=co, comparison_symbol='USD', limit=480))
            #decisions.append(self.daily_price_historical(symbol=co, comparison_symbol='USD', limit=83))
            #decisions.append(self.daily_price_historical(symbol=co, comparison_symbol='USD', limit=41))
            #decisions.append(self.daily_price_historical(symbol=co, comparison_symbol='USD', limit=20))
            #until =1538524800,
        self.closings = [["date", *self.coinlist]]

        #TEST API
    def testApi(self):    
        for a in range(0,len(self.decisions)):
            print("{0}: {1}".format(self.coinlist[a],len(self.decisions[a])))

    def formatInput(self):
        for i in range(0,len(self.decisions[0]),self.timestamp):
            self.closings.append(list([datetime.datetime.utcfromtimestamp(self.decisions[0][i]['time']).strftime('%Y-%m-%d %H:%M:%S')]))
            #datetime.datetime.utcfromtimestamp(self.decisions[0][i]['time']).strftime('%Y-%m-%d %H:%M:%S')
            for z in range(0,len(self.decisions)):
                self.closings[int(i/self.timestamp)+1].append(float(self.decisions[z][i]['close']))


    #closings = glist

    def createCoins(self):        
        self.columns = ['Date',"Total Portfolio","Profit"]
        for i in range(1,len(self.closings[0])):
            aCoin = Coin(crypto=self.closings[0][i], 
            percent = float(self.coinWeights[i-1]),
            exchange0=float(self.closings[1][i]),
            totalU = self.coinTotal,
            sumWeights = self.sumWeights)   
            #aCoin.what()
            self.columns += [aCoin.name+ ' Close',
            aCoin.name+' Total Value',
            aCoin.name +' Amount To Rebalance in USD',
            aCoin.name+' Quantity',
            aCoin.name+' To Rebalance',
            aCoin.name + ' Share',
            aCoin.name + ' Transaction Fee In USD',
            'Transaction Fee In ' + aCoin.name,
            'date']
            self.coinObj.append(aCoin)

    def rebalance(self):
        #print("Loading...")
        for it in range(1, len(self.closings)):
            
            for c in range(1,len(self.closings[it])):
                self.coinObj[c-1].addClosing(float(self.closings[it][c]))
            for c in range(1,len(self.closings[it])):
                if self.marketCaps:
                    self.coinObj[c-1].part0 = self.marketCaps[self.closings[it][0][:10]][self.coinObj[c-1].name]
                self.coinObj[c-1].calcRebalance()
            for c in range(1,len(self.closings[it])):
                self.coinObj[c-1].rebalance()
            Coin.showRebalanced(self.coinObj)
            #sys.stdout.write("\033[F")
            #print("iteration {0}".format(Coin.iterat))
            
            self.dic1 = {"Date":self.closings[it][0], "Total Portfolio":Coin.totalUSD0, "Profit":Coin.profit}
            for w in range(0, len(self.closings[0])-1):
                self.dic1 = {**self.dic1, 
                self.coinObj[w].name+ ' Close': float(self.closings[it][w+1]),
                self.coinObj[w].name +' Total Value':self.coinObj[w].amountUSD, 
                self.coinObj[w].name +' Amount To Rebalance in USD' : self.coinObj[w].deltaUSD,
                self.coinObj[w].name+' Quantity': self.coinObj[w].currentCoinAmount,
                self.coinObj[w].name+' To Rebalance':self.coinObj[w].deltaCrypto,
                self.coinObj[w].name + ' Share':self.coinObj[w].currentProc,
                self.coinObj[w].name + ' Transaction Fee In USD':self.coinObj[w].taxForRebalanceUSD,
                'Transaction Fee In '+ self.coinObj[w].name:self.coinObj[w].taxForRebalance}
            self.wholeData.append(self.dic1)
        #print(self.closings)  

    def writeToCSV(self):
        totalTranse = Coin.totalTrans
        roi = (Coin.totalUSD0-self.coinTotal)/self.coinTotal*100
        with open('backtest_results/'+datetime.datetime.now().strftime('%Y-%m-%d %H:%M')+'rebalance_in_'+str(self.timestamp)+'_hour_'+str(CoinCan.can)+'.csv', 'w', newline='') as csvfile:
            #fieldnames = oneCoin
            writer = csv.DictWriter(csvfile, fieldnames=self.columns)
            writer.writeheader()
            for row in self.wholeData:
                writer.writerow(row)
            writer.writerow({self.columns[0]:""})
            #writer.writerow({columns[0]:"Profit: ",columns[1]:Coin.totalUSD0, columns[8]:"Transaction fees total:",columns[9]:totalTranse})
            writer.writerow({self.columns[0]:"Profit: ",self.columns[1]:Coin.profit})
            writer.writerow({self.columns[0]:"ROI: ",self.columns[1]: roi})
            writer.writerow({self.columns[0]:"Transaction fees total:",self.columns[1]:totalTranse})
            writer.writerow({self.columns[0]:"WWIC:", self.columns[1]:Coin.wwic})
    def checkInput(self):
        hundred = sum(self.coinWeights)
        hundreds = False
        equality = len(self.coinWeights) == len(self.coinlist)
        fees = len(self.transactionFees) == len(self.coinlist)

        if int(hundred) == 100:
            hundreds = True
        else:
            print("The sum of the provided weights is equal to {0}%!".format(hundred))
        if not equality:
            print("Please provide same number of coins and weights!")
            print("coin weights length: {0}, coin list length: {1}.".format(len(self.coinWeights),len(self.coinlist) ))
        if not fees:
            print("Please provide same numbers of coins and transaction fees")
        return equality and fees

    def portfolio_changes(self):
        data_arr = []
        for i in range(0,len(self.wholeData)):
            data_arr.append([int(self.decisions[0][i*self.timestamp]['time'])*1000, float(self.wholeData[i]['Total Portfolio'])])
        roi = (Coin.totalUSD0-self.coinTotal)/self.coinTotal*100
        fees = Coin.totalTrans
        data = {"interval":self.timestamp, "portfolio": "{:.6f}".format(Coin.profit),"roi":"{:.6f}".format(roi),"fees":"{:.6f}".format(fees), "values":data_arr}
        return json.dumps(data)

    def get_market_cap(start, end, portfolio, interval, cnumber):
        #url='www'
        
        strstart = datetime.datetime.fromtimestamp(int(start)/1000).strftime('%Y-%m-%d')
        strend = datetime.datetime.fromtimestamp(int(end)/1000).strftime('%Y-%m-%d')
        #print(strstart)
        #page = requests.get(url)
        #cap = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/historical',headers={'X-CMC_PRO_API_KEY': '4de9f626-5904-4425-83ce-01b07e862802'})
        page = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest',headers={'X-CMC_PRO_API_KEY': '4de9f626-5904-4425-83ce-01b07e862802'})
        #cap = requests.get('https://www.cryptocurrencychart.com/api/coin/history/363/{0}/{1}/marketCap/USD'.format(strstart,strend),headers={'Key': '4102ea9c95681b5ff343b2c0707c01bf','Secret':'3983ce00ead746161d47c5055f5138ff'})
        #page = requests.get('https://www.cryptocurrencychart.com/api/coin/list',headers={'Key': '4102ea9c95681b5ff343b2c0707c01bf','Secret':'3983ce00ead746161d47c5055f5138ff'})
        #data = page.json()
        sortedcap = page.json()
        idcoins = {}
        with open('static/idcoins.json') as json_file:  
            idcoins = json.load(json_file)
        cap = []
        for i in range(0, cnumber):
            print(sortedcap['data'][i]['symbol'])
            currentid = sortedcap['data'][i]['symbol']
            bob = requests.get('https://www.cryptocurrencychart.com/api/coin/history/{0}/{1}/{2}/marketCap/USD'.format(idcoins[currentid], strstart,strend),headers={'Key': '4102ea9c95681b5ff343b2c0707c01bf','Secret':'3983ce00ead746161d47c5055f5138ff'})
            bod = bob.json()
            cap.append(bod)

        whole = {"dat":cap}
        return json.dumps(whole)

    def error_handler(self, e):
        data = {"message": e,"status":"error"}
        return data
    def calculate(self):
        try:
            if self.checkInput():
                self.readApi()
                self.formatInput()
                self.createCoins()
                self.rebalance()
                self.writeToCSV()
                return self.portfolio_changes()
        except ZeroCloseException as e:
            print("There is ZERO close price for {} at the {} iteration!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!".format(e.args[0], e.args[1]))
    def calc(self):
        try:
            if self.checkInput():
                self.readApi()
                self.formatInput()
                self.createCoins()
                self.rebalance()
                coins = {}
                for coi in range(len(self.coinlist)):
                    coins = {**coins, self.coinlist[coi]:"{:.6f}".format(self.coinWeights[coi])}
                data_arr = []
                for i in range(0,len(self.wholeData)):
                    data_arr.append([int(self.decisions[0][i*self.timestamp]['time'])*1000, float(self.wholeData[i]['Total Portfolio'])])
                roi = (Coin.totalUSD0-self.coinTotal)/self.coinTotal*100
                fees = Coin.totalTrans
                data = {"interval":self.timestamp, "portfolio": "{:.6f}".format(Coin.profit),"roi":"{:.6f}".format(roi),"fees":"{:.6f}".format(fees), "values":data_arr,"coins":coins}
                return data #json.dumps(data)
                #return self.portfolio_changes()
        except ZeroCloseException as e:
            error_message = "For some reason there is no data for {} at the {} step!".format(e.args[0], e.args[1])
            #print(error_message)
            return self.error_handler(error_message)
        except NocoinException as e:
            #print(e.args[0])
            return self.error_handler(e.args[0])
