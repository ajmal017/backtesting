import json
import requests

def select(data):
    from backt.backtesting import CoinCan
    try:

        start = int(data['start'])
        end = int(data['end'])
        portfolio = int(data['portfolio'])
        interval = int(data['interval'])
        # Convert end date
        iterations = int((end - start)/3600/1000)   
        coinSequence = data['coins']   
        coinWeights = []
        coinlist = []   
        for key, value in coinSequence.items():
            coinWeights.append(value)
            coinlist.append(key)
        sumTotal = 0
        for c in coinWeights:
            sumTotal += c
        if start and end and portfolio and interval:
            second = CoinCan(coinlist= coinlist, coinWeights=coinWeights, timestamp = interval, iterations = iterations, endDate=end, coinTotal = int(portfolio))   
            return second.calc()
    except TypeError:
        return {"message":"Some of the parameters doesn' look like numbers"}



def equalyWeighted(date):
    import datetime
    from backt.backtesting import CoinCan
    try:
        start = int(date['start'])
        end = int(date['end'])
        portfolio = int(date['portfolio'])
        interval = int(date['interval'])
        cnumber = int(date['cnumber'])
        strstart = datetime.datetime.fromtimestamp(int(start)/1000).strftime('%Y-%m-%d')
        strend = datetime.datetime.fromtimestamp(int(end)/1000).strftime('%Y-%m-%d')
        # Convert end date
        iterations = int((end - start)/3600/1000)
            #page = requests.get(url)
            #cap = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/historical',headers={'X-CMC_PRO_API_KEY': '4de9f626-5904-4425-83ce-01b07e862802'})
        page = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest',headers={'X-CMC_PRO_API_KEY': '4de9f626-5904-4425-83ce-01b07e862802'})
            #cap = requests.get('https://www.cryptocurrencychart.com/api/coin/history/363/{0}/{1}/marketCap/USD'.format(strstart,strend),headers={'Key': '4102ea9c95681b5ff343b2c0707c01bf','Secret':'3983ce00ead746161d47c5055f5138ff'})
            #page = requests.get('https://www.cryptocurrencychart.com/api/coin/list',headers={'Key': '4102ea9c95681b5ff343b2c0707c01bf','Secret':'3983ce00ead746161d47c5055f5138ff'})
            #data = page.json()
        sortedcap = page.json()
        idcoins = {}
        with open('backt/static/idcoins.json') as json_file:  
            idcoins = json.load(json_file)
        cap = []
        coinWeights = []
        coinlist = []
        for i in range(0, cnumber):
            currentid = sortedcap['data'][i]['symbol']
            coinlist.append(currentid)
            coinWeights.append(100/cnumber)
        sumTotal = 0
        for c in coinWeights:
            sumTotal += c
        if start and end and portfolio and interval:
            second = CoinCan(coinlist= coinlist, coinWeights=coinWeights, timestamp = interval, iterations = iterations, endDate=end, coinTotal = int(portfolio))   
            return second.calc()
    except TypeError:
        return {"message":"Some of the parameters doesn' look like numbers"}

def check_cap(date):
    import datetime
    from backt.backtesting import CoinCan
    try:
        start = int(date['start'])
        end = int(date['end'])
        portfolio = int(date['portfolio'])
        interval = int(date['interval'])
        cnumber = int(date['cnumber'])
        strstart = datetime.datetime.fromtimestamp(int(start)/1000).strftime('%Y-%m-%d')
        strend = datetime.datetime.fromtimestamp(int(end)/1000).strftime('%Y-%m-%d')
        # Convert end date
        iterations = int((end - start)/3600/1000)
            #page = requests.get(url)
            #cap = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/historical',headers={'X-CMC_PRO_API_KEY': '4de9f626-5904-4425-83ce-01b07e862802'})
        page = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest',headers={'X-CMC_PRO_API_KEY': '4de9f626-5904-4425-83ce-01b07e862802'})
            #cap = requests.get('https://www.cryptocurrencychart.com/api/coin/history/363/{0}/{1}/marketCap/USD'.format(strstart,strend),headers={'Key': '4102ea9c95681b5ff343b2c0707c01bf','Secret':'3983ce00ead746161d47c5055f5138ff'})
            #page = requests.get('https://www.cryptocurrencychart.com/api/coin/list',headers={'Key': '4102ea9c95681b5ff343b2c0707c01bf','Secret':'3983ce00ead746161d47c5055f5138ff'})
            #data = page.json()
        sortedcap = page.json()
        idcoins = {}
        with open('backt/static/idcoins.json') as json_file:  
            idcoins = json.load(json_file)
        cap = []
        for i in range(cnumber):
            #print(sortedcap['data'][i]['symbol'])
            currentid = sortedcap['data'][i]['symbol']
            print(currentid)
            bob = requests.get('https://www.cryptocurrencychart.com/api/coin/history/{0}/{1}/{2}/marketCap/USD'.format(idcoins[currentid], strstart,strend),headers={'Key': '4102ea9c95681b5ff343b2c0707c01bf','Secret':'3983ce00ead746161d47c5055f5138ff'})
            bod = bob.json()
            cap.append(bod)
            capcent = {}
            coinWeights = []
            coinlist = []
            for d in range(0,len(cap[0]['data'])):
                temptime = cap[0]['data'][d]['date']
                capcent = {**capcent, temptime:{}}
                elcoin = {}
                percents = {}
                for cc in range(0,len(cap)):
                    elcoin = {**elcoin, cap[cc]['coin']['code']:float(cap[cc]['data'][d]['marketCap'])}
                wholecap = sum(elcoin.values())
                for c in range(0,len(cap)):
                    #capcent[cap[0]['data'][d]['date']].append(cap[c]['data'][d]['marketCap'])            
                    currcoin = cap[c]['coin']['code']
                    currentWeight = elcoin[currcoin]/wholecap*100
                    capcent[temptime] = {**capcent[temptime], currcoin: currentWeight}
                    if d == 0:
                        coinlist.append(currcoin)
                        coinWeights.append(currentWeight)
        sumTotal = 0
        for c in coinWeights:
            sumTotal += c
        #print(sumTotal)
        if start and end and portfolio and interval and cnumber:
            second = CoinCan(coinlist= coinlist, coinWeights=coinWeights, timestamp = interval, iterations = iterations, endDate=end, coinTotal = int(portfolio), marketCaps = capcent)   
        return second.calc() 
    except TypeError:
        return {"message":"You may have mistyped a number or a date"}

def search(query):
    results = {}
    with open('backt/static/clean.json', 'r') as json_file:
        cryptos = json.load(json_file)
        

        for key, value in cryptos.items():
            if len(query) < 2:
                if not key.find(query, 0, 1) or not value.find(query, 0, 1):
                    results[key] = value
            elif len(query) > 1:
                if key.find(query) != -1 or value.find(query) != -1:
                    results[key] = value
    
        #return json.dumps(results)
        return results


searchCoin = search
runBacktesting = select
byMarketcap = check_cap