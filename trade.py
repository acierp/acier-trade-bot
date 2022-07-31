import json
import threading
import requests
import httpx
import hashlib
import time
from pypresence import Presence 
from datetime import timedelta
import datetime
import dateutil.parser as dp
from itertools import cycle
import math
import random 
import psutil
import dhooks
import ctypes
import os


os.system('color')

VERSION = 2.3

with open('config.json', 'r+', encoding='utf-8') as cfgfile:
    try:
        config = json.load(cfgfile)
    except:
        print(f'{datetime.datetime.now().time()}: Your config file is in invalid format. Please troubleshoot it using jsonformatter.curiousconcept.com')

try:
    with open("values.json", "r") as jsonFile:
        json.load(jsonFile)
except:
    with open("values.json", "w") as valuetest:
        valuetest.truncate(0)
        valuetest.write('{}')
    print(f'{datetime.datetime.now().time()}: Successfully reformatted values.json')

try:
    with open("cooldown.json", "r") as jsonFile:
        json.load(jsonFile)
except:
    with open("cooldown.json", "w") as valuetest:
        valuetest.truncate(0)
        valuetest.write('{}')
    print(f'{datetime.datetime.now().time()}: Successfully reformatted cooldown.json')

try:
    with open("cached_inbounds.json", "r") as jsonFile:
        json.load(jsonFile)
except:
    with open("cached_inbounds.json", "w") as valuetest:
        valuetest.truncate(0)
        valuetest.write('[]')
    print(f'{datetime.datetime.now().time()}: Successfully reformatted cached_inbounds.json')

with open('proxies.txt','r+', encoding='utf-8') as f:
    ProxyPool = cycle(f.read().splitlines())
  
proxies = []

defaultCookie = {'.ROBLOSECURITY': config['authentication']['cookie']}
selfinventory = []
cachedinventory = []
queue = []

offerblacklist = []
requestblacklist = []

blacklistusers = []

useridtoname = {}
token = []

algorithmqueue = []

outboundsent = []
outboundsentcheck = []

firstInventory = []
secondInventory = []

with open("values.json", "r") as jsonFile:
    values = json.load(jsonFile)

if config['save_cooldown'] == True:
    with open("cooldown.json", "r") as jsonFile:
        cooldown = json.load(jsonFile)
else:
    cooldown = {}

with open("cached_inbounds.json", "r") as jsonFile:
    alreadyinboundchecked = json.load(jsonFile)

try:
    itemdetails = httpx.get("https://www.rolimons.com/itemapi/itemdetails")
except:
    print('Failed to fetch values from rolimons.')
# REMEMBER TO CHANGE

def my_value(number):
    return ("{:,}".format(number))

def firstInventoryCheck():
    global firstInventory
    r = requests.get(f'https://inventory.roblox.com/v1/users/{config["authentication"]["userid"]}/assets/collectibles?sortOrder=Asc&limit=100').json()
    firstInventory = [f"{item['assetId']}:{item['userAssetId']}" for item in r['data']]


def secondInventoryCheck():
    global secondInventory
    r = requests.get(f'https://inventory.roblox.com/v1/users/{config["authentication"]["userid"]}/assets/collectibles?sortOrder=Asc&limit=100').json()
    secondInventory = [f"{item['assetId']}:{item['userAssetId']}" for item in r['data']]

def compareInventories():
    itemLost = [item for item in firstInventory if not item in secondInventory]
    itemGained = [item for item in secondInventory if not item in firstInventory]
    if itemLost != [] and itemGained != []:
        formattedgive = []
        formattedgot = []
        for item in itemLost:
            formattedgive.append(item.split(':')[0])
        for item in itemGained:
            formattedgot.append(item.split(':')[0])
        Webhooks.sendCompleted(formattedgive, formattedgot)
        firstInventoryCheck()

def updateToken():
        getToken = httpx.post('https://auth.roblox.com/v1/logout', cookies={'.ROBLOSECURITY': config['authentication']['cookie']})
        if 'x-csrf-token' in getToken.headers:
            token.clear();token.append(getToken.headers['x-csrf-token'])
            #print(f'{datetime.datetime.now().time()}: Successfully updated token hash ' + Auth.md5(getToken.headers['x-csrf-token']))
            return True
        else:
            print(f'Invalidated cookie returned in updateToken; {getToken.headers}');return False

class Algo:
    def ballgAgo(myInv, harrsingInv):
        combinationsSending = []
        combinationsRecieving = []
        for i in range(1, 5):
            combinationsSending += Algo.combinations(myInv, i)
            combinationsRecieving += Algo.combinations(harrsingInv, i)
        
        for sending in combinationsSending:
            totalSending = Algo.getTotalPrice(sending)
            for recieving in combinationsRecieving:
                totalRecieving = Algo.getTotalPrice(recieving)
                multiplier = float(totalRecieving / totalSending)

                same = False
                for item in sending:
                    for item2 in recieving:
                        if(item["assetId"] == item2["assetId"]):
                            same = True
                
                if not same:
                    if totalRecieving >= config['valuation']['minimum_trade_value']:
                        if len(sending) == 2 and len(recieving) == 1 or len(sending) == 3 and len(recieving) == 1 or len(sending) == 4 and len(recieving) == 1:
                            if config['trading']['experimental_algorithm']['upgrade']['send_upgrade'] == True: #new
                                if(multiplier >= config['trading']['experimental_algorithm']['upgrade']['upgrade_minimum_request_multiplier'] and multiplier <= config['trading']['experimental_algorithm']['upgrade']['upgrade_maximum_request_multiplier']):
                                    return {"sending": sending, "recieving": recieving, "multiplier": multiplier, "type": "upgrade"}
                        elif len(sending) == 1 and len(recieving) == 1 or len(sending) == 2 and len(recieving) == 2 or len(sending) == 2 and len(recieving) == 3 or len(sending) == 2 and len(recieving) == 4 or len(sending) == 4 and len(recieving) == 2 or len(sending) == 3 and len(recieving) == 2:
                            if config['trading']['experimental_algorithm']['mixed']['send_mixed'] == True: #new
                                if(multiplier >= config['trading']['experimental_algorithm']['mixed']['mixed_minimum_request_multiplier'] and multiplier <= config['trading']['experimental_algorithm']['mixed']['mixed_maximum_request_multiplier']):
                                    return {"sending": sending, "recieving": recieving, "multiplier": multiplier, "type": "mixed"}
                        else:
                            if config['trading']['experimental_algorithm']['downgrade']['send_downgrade'] == True: #new
                                if(multiplier >= config['trading']['experimental_algorithm']['downgrade']['downgrade_minimum_request_multiplier'] and multiplier <= config['trading']['experimental_algorithm']['downgrade']['downgrade_maximum_request_multiplier']):
                                    return {"sending": sending, "recieving": recieving, "multiplier": multiplier, "type": "downgrade"}
        

    def acierhothotAlgo(myInv, harrsingInv, minMultiplier, maxMultiplier):
        combinationsSending = []
        combinationsRecieving = []
        validTrades = []
        for i in range(4):
            i += 1
            combinationsSending += Algo.combinations(myInv, i)
            combinationsRecieving += Algo.combinations(harrsingInv, i)
        
        for sending in combinationsSending:
            totalSending = Algo.getTotalPrice(sending)
            for recieving in combinationsRecieving:
                totalRecieving = Algo.getTotalPrice(recieving)
                if totalSending == 0 or totalRecieving == 0:
                    print(f'{sending} {totalSending}')
                multiplier = float(totalRecieving / totalSending)
                if(multiplier >= minMultiplier and multiplier <= maxMultiplier):
                    same = False
                    for item in sending:
                        for item2 in recieving:
                            if(item["assetId"] == item2["assetId"]):
                                same = True
                    if not same:
                        return {"sending": sending, "recieving": recieving, "multiplier": multiplier}
        return validTrades
    
    def acieroldalgo(myInv, harrsingInv, minMultiplier, maxMultiplier):
        combinationsSending = []
        combinationsRecieving = []
        validTrades = []
        for i in range(4):
            i += 1
            combinationsSending += Algo.combinations(myInv, i)
            combinationsRecieving += Algo.combinations(harrsingInv, i)
        
        for sending in combinationsSending:
            totalSending = Algo.getTotalPrice(sending)
            for recieving in combinationsRecieving:
                totalRecieving = Algo.getTotalPrice(recieving)
                if totalSending == 0 or totalRecieving == 0:
                    print(f'{sending} {totalSending}')
                multiplier = float(totalRecieving / totalSending)
                if(multiplier >= minMultiplier and multiplier <= maxMultiplier):
                    same = False
                    for item in sending:
                        for item2 in recieving:
                            if(item["assetId"] == item2["assetId"]):
                                same = True
                    if not same:
                        return {"sending": sending, "recieving": recieving, "multiplier": multiplier}
        
        return validTrades

    def getTotalPrice(inv):
        value = 0
        for asset in inv:
            if asset["value"]:
                value += int(asset["value"])
        return value

    def combinations(inv, n):
        if n == 0:
            return [[]]
        combs = []
        for i in range(0, len(inv)):
            item = inv[i]
            restItems = inv[i+1:]
            for c in Algo.combinations(restItems, n-1):
                combs.append([item] + c)
        return combs

class Cooldown:
    def writenewCooldown(user):
        if str(user) in cooldown:
               cooldown[str(user)] = str(datetime.datetime.now() + timedelta(seconds=config['resend_cooldown']))
        else:
            cooldown[str(user)] = str(datetime.datetime.now() + timedelta(seconds=config['resend_cooldown']))

    def newcooldownOver(user):
        if str(user) in cooldown:
            if datetime.datetime.fromisoformat(cooldown[str(user)]) <= datetime.datetime.now():
                return True
            else:
                return False
        else:
            return True

    def getsavedValue(typec, item):
        if typec == 'offer':
            if Valuation.iscustomOffer(item):
                val = config['custom_values']['custom_offer_values'][str(item)]
                if "+" in val or "-" in val:
                    plus_minus = val[:1]
                    int_val = int(val[1:])
                    if plus_minus == "-":
                        int_val *= -1
                
                    return Valuation.getroliValue(item) + int_val
                return val
        if typec == 'request':
            if Valuation.iscustomRequest(item):
                val = config['custom_values']['custom_request_values'][str(item)]
                if "+" in val or "-" in val:
                    plus_minus = val[:1]
                    int_val = int(val[1:])
                    if plus_minus == "-":
                        int_val *= -1
                
                    return Valuation.getroliValue(item) + int_val
                return val

        if str(item) in values:
            if Cooldown.valuecooldownOver(item) == False:
                if typec == 'offer':
                    return values[str(item)]['offervalue']
                else:
                    return values[str(item)]['requestvalue']
            else:
                Valuation.generateValue(item)
                return Cooldown.getsavedValue(typec, item)
        else:
            Valuation.generateValue(item)
            return Cooldown.getsavedValue(typec, item)

    def valuecooldownOver(item):
        if str(item) in values:
            if datetime.datetime.fromisoformat(values[str(item)]['next_update']) <= datetime.datetime.now():
                return True
            else:
                return False
        else:
            return True


class Valuation:
    def isRare(item):
        global itemdetails
        if str(itemdetails.json()['items'][str(item)][-1]) == '1':
            return True
        else:
            return False

    def getVolume(item):
        if str(item) in values:
            return values[str(item)]['volume']
        else:
            Valuation.generateValue(item)
            return Valuation.getVolume(item)
    def iscustomOffer(item):
        if str(item) in config['custom_values']['custom_offer_values']:
            return True
        else:
            return False
    
    def iscustomRequest(item):
        if str(item) in config['custom_values']['custom_request_values']:
            return True
        else:
            return False

    def getroliValue(item):
        global itemdetails
        try:
            itemcheck = itemdetails.json()['items'][str(item)][3]
            if str(itemcheck) != "-1":
                return itemdetails.json()['items'][str(item)][3]
            else:
                return itemdetails.json()['items'][str(item)][2]
        except:
            print('Failed to fetch values from rolimons.')

    def ismarkedProjected(item):
        status = itemdetails.json()['items'][str(item)][7]
        if str(status) == '1':
            return True
        else:
            return False

    def initializeBlacklist():
        tempofferblacklist = []
        temprequestblacklist = []
        tempuserblacklist = []
        for item in config['do_not_trade']['static']:
            tempofferblacklist.append(str(item))
        for item in config['do_not_trade_for']['static']:
            temprequestblacklist.append(str(item))
        for item in itemdetails.json()['items']:
            if config['do_not_trade']['trade_rares'] ==  False: 
                if str(itemdetails.json()['items'][str(item)][-1]) == '1':
                    tempofferblacklist.append(str(item))
            
            if config['do_not_trade_for']['trade_for_rares'] == False: 
                if str(itemdetails.json()['items'][str(item)][-1]) == '1':
                    temprequestblacklist.append(str(item))

            value = itemdetails.json()['items'][str(item)][3]
            if str(value) == '-1':
                value = itemdetails.json()['items'][str(item)][2]
            if int(value) < config['do_not_trade']['items_under']:
                tempofferblacklist.append(str(item)) 
            if int(value) > config['do_not_trade']['items_over']:
                tempofferblacklist.append(str(item))
            
            if int(value) < config['do_not_trade_for']['items_under']:
                temprequestblacklist.append(str(item)) 
            if int(value) > config['do_not_trade_for']['items_over']:
                temprequestblacklist.append(str(item))

            if str(itemdetails.json()['items'][str(item)][7]) == '1':
                if config['valuation']['projecteds']['owned_projecteds']['trade'] == False:
                    tempofferblacklist.append(str(item))

                if config['valuation']['projecteds']['request_projecteds']['trade_for'] == False:
                    temprequestblacklist.append(str(item))
                else:
                    if int(value) >= int(config['valuation']['projecteds']['request_projecteds']['dont_trade_for_projecteds_over']):
                        temprequestblacklist.append(str(item))
            
        
        if config['scraping']['send_to_trade_botters'] == False:
            for user in httpx.get('https://gist.githubusercontent.com/codetariat/03043d47689a6ee645366d327b11944c/raw/').json():
                tempuserblacklist.append(str(user[0]))
        
        for user in config['scraping']['dont_send_to']:
            tempuserblacklist.append(str(user))
        
        try:
            for itemcheck in httpx.get('https://backend.aequet.fr/recent_limiteds').json()['data']:
                if config['do_not_trade_for']['blacklist_new_limiteds'] == True:
                    if str(itemcheck) not in temprequestblacklist:
                        temprequestblacklist.append(str(itemcheck))
                if config['do_not_trade']['blacklist_new_limiteds'] == True:
                    if str(itemcheck) not in tempofferblacklist:
                        tempofferblacklist.append(str(itemcheck))
        except Exception as e:
            print(f'Failed to blacklist newly released roblox limiteds ... {e}')

        for o in tempofferblacklist:
            if str(o) not in offerblacklist:
                offerblacklist.append(o)

        for i in temprequestblacklist:
            if str(i) not in requestblacklist:
                requestblacklist.append(i)

        for u in tempuserblacklist:
            if str(u) not in blacklistusers:
                blacklistusers.append(u)
        print(f'{datetime.datetime.now().time()}: Successfully blacklisted {len(offerblacklist)} offer items, {len(requestblacklist)} request items, and {len(blacklistusers)} users.')


    def isValued(item):
        if str(itemdetails.json()['items'][str(item)][3]) == '-1':
            return False
        else:
            return True

    def generateValue(item):
        requestvalue = 0
        offervalue = 0
        salesData = httpx.get(f'https://economy.roproxy.com/v1/assets/{item}/resale-data')
        rap = salesData.json()['recentAveragePrice']
        print(f'{datetime.datetime.now().time()}: Generating value for {item} ...')
        if config['valuation']['value_offer_items_at_rap'] == False:
            checkisvalued = Valuation.isValued(item)
            ismarkedprojected = Valuation.ismarkedProjected(item)
            if checkisvalued == False and ismarkedprojected == False:
                if salesData.status_code == 200:
                    saleprice = 0
                    amount = 0
                    for salePoint in salesData.json()['priceDataPoints']:
                        date = salePoint['date']
                        date = datetime.datetime.fromisoformat(date[:-1] + "+00:00")
                        now = datetime.datetime.now(tz=datetime.timezone.utc)
                        diff_days = abs(date - now).days
                        if diff_days <= int(config['valuation']['average_days']):
                            amount += 1
                            saleprice += salePoint['value']
                    if amount != 0:
                        average = int(math.ceil(float(saleprice) / float(amount)))
                        if average >= rap:
                            offervalue = average
                        else:
                            offervalue = rap
                    else:
                        offervalue = rap
                    
                else:
                    print(salesData.text)
            elif ismarkedprojected == True and checkisvalued == False:
                if salesData.status_code == 200:
                    offervalue = int(math.ceil(float(rap) * float(config['valuation']['projecteds']['owned_projecteds']['owned_projected_multiplier'])))
                else:
                    print(f'{salesData.text}')
            else:
                #offervalue = int(itemdetails.json()['items'][str(item)][3])
                offervalue = Valuation.getroliValue(item)
        else:
            checkisvalued = Valuation.isValued(item)
            ismarkedprojected = Valuation.ismarkedProjected(item)
            if checkisvalued == False and ismarkedprojected == False:
                offervalue = Valuation.getroliValue(item)
            elif ismarkedprojected == True and checkisvalued == False:
                offervalue = int(math.ceil(float(rap) * float(config['valuation']['projecteds']['owned_projecteds']['owned_projected_multiplier'])))
            else:
                offervalue = Valuation.getroliValue(item)

        checkisvalued = Valuation.isValued(item)
        ismarkedprojected = Valuation.ismarkedProjected(item)
        if checkisvalued == False and ismarkedprojected == False or config['valuation']['only_rap_trade'] == True:
            if salesData.status_code == 200:
                saleprice = 0
                amount = 0

                for salePoint in salesData.json()['priceDataPoints']:
                    date = salePoint['date']
                    date = datetime.datetime.fromisoformat(date[:-1] + "+00:00")
                    now = datetime.datetime.now(tz=datetime.timezone.utc)
                    diff_days = abs(date - now).days
                    if diff_days <= int(config['valuation']['average_days']):
                        amount += 1
                        saleprice += salePoint['value']
                if amount != 0:
                    average = int(math.ceil(float(saleprice) / float(amount)))
                else:
                    average = rap
                if config['valuation']['undervalue_request_rap']['enabled'] == False:
                    if average > rap:
                        requestvalue = rap
                    else:
                        requestvalue = average
                else:
                    if average > rap:
                        requestvalue = rap * config['valuation']['undervalue_request_rap']['rap_worth_multiplier']
                    else:
                        requestvalue = average * config['valuation']['undervalue_request_rap']['rap_worth_multiplier']
            else:
                print(salesData.text)

        elif ismarkedprojected == True and checkisvalued == False:
            if salesData.status_code == 200:
                writevalue = int(math.ceil(float(rap) * float(config['valuation']['projecteds']['request_projecteds']['request_projected_multiplier'])))
                requestvalue = writevalue
            else:
                print(f'{salesData.text}')
        else:
            writevalue = int(itemdetails.json()['items'][str(item)][3])
            requestvalue = writevalue


        totalamountSold = 0

        for salePoint in salesData.json()['volumeDataPoints']:
            date = salePoint['date']
            date = datetime.datetime.fromisoformat(date[:-1] + "+00:00")
            now = datetime.datetime.now(tz=datetime.timezone.utc)
            diff_days = abs(date - now).days
            if diff_days <= 30:
                totalamountSold += salePoint['value']
            
        if totalamountSold != 0:
            volume = round(float(totalamountSold) / float(30), 2)
        else:
            volume = 0

        if str(item) in values:
            projectedStatus = Valuation.ismarkedProjected(item)
            values[str(item)]['next_update'] = str(datetime.datetime.now() + timedelta(seconds=config['valuation']['update_values_interval']))
            values[str(item)]['offervalue'] = int(offervalue)
            values[str(item)]['requestvalue'] = int(requestvalue)
            values[str(item)]['rap'] = int(rap)
            values[str(item)]['projected'] = projectedStatus
        else:
            projectedStatus = Valuation.ismarkedProjected(item)
            values[str(item)] = {'volume': volume, 'projected': projectedStatus, 'next_update': str(datetime.datetime.now() + timedelta(seconds=config['valuation']['update_values_interval'])), 'rap': int(rap), 'offervalue': int(offervalue), "requestvalue": int(requestvalue)}

class Acier:
    def sendTrade(offer, request, userid, givingraw, gettingraw, fancy):
        if not token:
            updateToken()
            return Acier.sendTrade(offer, request, userid, givingraw, gettingraw, fancy)

        data = {
            "offers": [
            {
                "userId": userid,
                "userAssetIds": request,
                "robux": 0
            },
            {
                "userId": config['authentication']['userid'],
                "userAssetIds": offer,
                "robux": 0
            }
        ]}
        
        headers = {'X-CSRF-TOKEN': token[0], 'User-Agent': 'Roblox/WinInet', 'Referer': 'https://www.roblox.com/my/account', 'Origin': 'https://www.roblox.com'}

        if config['test_mode'] == False:
            if config['proxies']['enabled']:
                try:
                    if config['proxies']['rotating']['enabled'] == True:
                        attemptSend = requests.post('https://trades.roblox.com/v1/trades/send', json=data, cookies={'.ROBLOSECURITY': config['authentication']['cookie']}, headers=headers, proxies={"https": config['proxies']['rotating']['rotating_proxy']})
                    else:
                        attemptSend = requests.post('https://trades.roblox.com/v1/trades/send', json=data, cookies={'.ROBLOSECURITY': config['authentication']['cookie']}, headers=headers, proxies={"https": "http://" + next(ProxyPool)})
                except Exception as e:
                    if config['proxies']['retry_connection_errors']:
                        print(e)
                        return Acier.sendTrade(offer, request, userid, givingraw, gettingraw, fancy)
                    else:
                        print(e)
                        return
            else:
                attemptSend = requests.post('https://trades.roblox.com/v1/trades/send', json=data, cookies={'.ROBLOSECURITY': config['authentication']['cookie']}, headers=headers)
            if attemptSend.status_code == 200:
                print(fancy)
                #print(f'{datetime.datetime.now().time()}: Successfully sent trade to {userid} (trade id: {attemptSend.json()["id"]})')
                outboundsent.append("1")
                outboundsentcheck.append("1")
                if config['outbound']['notify']['send_notifications'] == True:
                    Webhooks.sendOutbound(userid, givingraw, gettingraw)
                if config['outbound']['dump_to_json']['dump'] == True:
                    tradeid = str(attemptSend.json()['id'])
                    with open(config['outbound']['dump_to_json']['file'], "r") as jsonFile:
                        ob = json.load(jsonFile)
                    ob[tradeid] = {'offer': givingraw, 'request': gettingraw, 'offer_uaids': offer, 'request_uaids': request}
                    with open(config['outbound']['dump_to_json']['file'], "w") as jsonFile:
                        json.dump(ob, jsonFile)
            elif "TooManyRequests" in attemptSend.text:
                if config['debug'] == True:
                    print(f"{datetime.datetime.now().time()}: Too many requests when attempting to send a trade to {userid} waiting {config['trade_ratelimit_retry']} seconds and retrying ...")
                time.sleep(config['trade_ratelimit_retry'])
                return Acier.sendTrade(offer, request, userid, givingraw, gettingraw, fancy)
            elif "privacy settings" in attemptSend.text:
                print(f'{datetime.datetime.now().time()}: Failed to send trade to {userid} as their privacy settings were too strict.')
            elif "userAssets are invalid" in attemptSend.text:
                print(f'Failed to send trade to {userid} as either the sender or receiver inventory has changed. Re-adding {userid} to the scan queue.')
                algorithmqueue.insert(0, str(userid))
            elif attemptSend.status_code == 403:
                updateToken()
                return Acier.sendTrade(offer, request, userid, givingraw, gettingraw, fancy)
            else:
                print(attemptSend.text)
        else:
            print(fancy)


    def getInventory(user):
        try:
            items = []
            global defaultCookie
            inventory = httpx.get(f'https://inventory.roblox.com/v1/users/{user}/assets/collectibles?sortOrder=Asc&limit=100', cookies=defaultCookie, timeout=30)
            if inventory.status_code == 200:
                if len(inventory.json()['data']) <  config['scraping']['maximum_items']:
                    for item in inventory.json()['data']:
                        if str(item['assetId']) not in requestblacklist:
                            valu = Cooldown.getsavedValue('request', item['assetId'])
                            if Valuation.getVolume(item['assetId']) >= config['valuation']['minimum_volume'] or Valuation.isValued(item['assetId']) == True:
                                items.append({'assetId': item['assetId'], 'uaid': str(item['userAssetId']), 'name': item['name'], 'rap': item['recentAveragePrice'], 'value': valu})
                    return items
            elif inventory.status_code == 429:
                print(f'Too many requests when attempting to scrape {user} inventory. Waiting and retrying...')
                time.sleep(2)
                return Acier.getInventory(user)
        except:
            return Acier.getInventory(user)

    def getselfInventory():
        global defaultCookie
        rawitems = []
        items = []

        getridof = False
        inventory = httpx.get(f'https://inventory.roblox.com/v1/users/{config["authentication"]["userid"]}/assets/collectibles?sortOrder=Asc&limit=100', cookies=defaultCookie)
        if inventory.status_code == 200:
            for item in inventory.json()['data']:
                if str(item['assetId']) in config['get_rid_of']['items']:
                    getridof = True
                if str(item['assetId']) not in offerblacklist:
                    items.append({'assetId': item['assetId'], 'uaid': str(item['userAssetId']), 'name': item['name'], 'rap': item['recentAveragePrice'], 'value': Cooldown.getsavedValue('offer', item['assetId'])})
                    rawitems.append(str(item['assetId']))
                if rawitems.count(str(item['assetId'])) >= config['do_not_trade_for']['dont_hoard_over']:
                    if config['debug'] == True:
                        print(f'Blacklisting {item["assetId"]} as you own {config["do_not_trade_for"]["dont_hoard_over"]} or more copies')
                    requestblacklist.append(str(item['assetId']))

            if getridof == True:
                itemnew = []
                for icheck in items:
                    if str(icheck['assetId']) in config['get_rid_of']['items']:
                        itemnew.append(icheck)
                return itemnew

            return items
        else:
            print(f'inventory status code is not 200 wtf?? {inventory.text}')
            return Acier.getselfInventory()

    def generateownedValues(items):
        pass

    def tocheckCombos():
        pass

class Updater:
    def sendQueue():
        while True:
            try:
                if queue:
                    trade = queue.pop(-1)
                    if config['queue']['double_check_queue']['double_check_owned'] == True:
                        if Checking.doublecheckOffer(trade['giving'], trade['getting'], trade['user']) == True:
                            Acier.sendTrade(trade['giving'], trade['getting'], trade['user'], trade['givingraw'], trade['gettingraw'], trade['fancymessage'])
                    else:
                        Acier.sendTrade(trade['giving'], trade['getting'], trade['user'], trade['givingraw'], trade['gettingraw'], trade['fancymessage'])
            except Exception as e:
               print(f'Ignoring exception in sendQueue {e}')

class Scraping: 
    # def isActive(user):
    #     try:
    #         userlastonline = httpx.get(f'https://api.roblox.com/users/{user}/onlinestatus/', timeout=30)
    #         lastonline = userlastonline.json()['LastOnline']
    #         parsed_time = dp.parse(lastonline)
    #         time_in_seconds = parsed_time.timestamp()
    #         final_time = time.time()-time_in_seconds

    #         if final_time/int(config['scraping']['owners']['maximum_seconds_inactive']) <= 1:
    #             return True
    #         else:
    #             return False
    #     except Exception as e:
    #         print(f'Ignoring exception in isActive: {e}')
    #         return False

    def getroliOwners(itemid):
        getOwners = httpx.get(f'https://www.rolimons.com/item/{itemid}', timeout=30).text.splitlines()
        for line in getOwners: 
            if 'bc_copies_data' in line:
                data = line.replace(";", "").replace(" ", "").replace("varbc_copies_data=", "")
        newdata = json.loads(data)
        for ownercheck in newdata['owner_ids']:
            if Cooldown.newcooldownOver(str(ownercheck)) == True:
                if str(ownercheck) != '1':
                    if Scraping.isActive(str(ownercheck)) == True:
                        Cooldown.writenewCooldown(str(ownercheck))
                        if config['debug'] == True:
                            print(f'{datetime.datetime.now().time()}: Searching for trade with {ownercheck} scraped from {itemid} owners')
                        algorithmqueue.append(ownercheck)

    def getName(item):
        global itemdetails
        return itemdetails.json()['items'][str(item)][0]

    def getuserName(userid):
        try:
            if str(userid) not in useridtoname:
                getName = httpx.get(f'https://users.roblox.com/v1/users/{userid}')
                if getName.status_code == 200:
                    useridtoname[str(userid)] = {'username': getName.json()['name']}
                    return getName.json()['name']
                elif getName.status_code == 429:
                    userpage = requests.get(f'https://www.roblox.com/users/{userid}/profile')

                    for line in userpage.text.splitlines():
                        if "Roblox.ProfileHeaderData" in line:
                            jsondata = json.loads(line.replace(";", "").split("=")[-1])
                            useridtoname[str(userid)] = {'username': jsondata['profileusername']}
                            return jsondata['profileusername']
            else:
                return useridtoname[str(userid)]['username']
        except Exception as e:
            print(f'Ignoring exception in getuserName: {e}')

    def scrapeRopro():
        while True:
            try:
                for user in httpx.get('https://ropro.io/api/getWishlistAll.php?page=1').json()['wishes']:
                    userid = user['user']
                    if Cooldown.newcooldownOver(str(userid)) == True:
                        Cooldown.writenewCooldown(str(userid))
                        if config['debug'] == True:
                            print(f"{datetime.datetime.now().time()}: Searching for trades with {user['user']} scraped from ropro trade ads.", flush=True)
                        algorithmqueue.append(str(userid))
            except Exception as e:
                print(f'Ignoring exception when scraping ropro: {e}')
            time.sleep(int(config['scraping']['scrape_cooldown']))

    def scrapeFlip():
        while True:
            try:
                getflipData = httpx.get(f'https://legacy.rbxflip-apis.com/games/versus/CF', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36', 'Connection': 'keep-alive'})
                for user in getflipData.json()['data']['games']:
                    if user['status'] == 'Completed':
                        winner = user['winner']['id']
                        loser = user['player']['id']
                        if Cooldown.newcooldownOver(str(winner)) == True and str(winner) not in blacklistusers:
                                Cooldown.writenewCooldown(str(winner))
                                if config['debug'] == True:
                                    print(f"{datetime.datetime.now().time()}: Searching for trades with {winner} scraped from rbxflip completed flips.")
                                algorithmqueue.append(str(winner))
                        if Cooldown.newcooldownOver(str(loser)) == True and str(winner) not in blacklistusers:
                                Cooldown.writenewCooldown(str(loser))
                                if config['debug'] == True:
                                    print(f"{datetime.datetime.now().time()}: Searching for trades with {loser} scraped from rbxflip completed flips.")
                                algorithmqueue.append(str(loser))
                        #    tocheckinvqueue.append(str(user['winner']['id']))
                time.sleep(int(config['scraping']['scrape_cooldown']))
            except Exception as e:
                print(f'Ignoring exception when scraping rbxflip: {e}')

    def scrapeRolimons():
        while True:
            try:
                getroliData = httpx.get(f'https://tradeads2.acier.repl.co/acierontop')
                for user in getroliData.json()['trade_ads']:
                    userid = user[2]
                    if Cooldown.newcooldownOver(str(userid)) == True and str(userid) not in blacklistusers:
                        Cooldown.writenewCooldown(str(userid))
                        if config['debug'] == True:
                            print(f"{datetime.datetime.now().time()}: Searching for trades with {userid} scraped from rolimons trade ads.")
                        algorithmqueue.append(str(userid))
            except Exception as e:
                print(f'Ignoring exception in scrapeRolimons: {e}')
            time.sleep(int(config['scraping']['scrape_cooldown']))

    def scrapeTxt():
        while True:
            try:
                cache = open(config['scraping']['scrape_from_file']['directory'], 'r')
                cacheusers = cache.readlines()
                for user in cacheusers:
                    userid = user.strip()
                    if Cooldown.newcooldownOver(str(userid)) == True and str(userid) not in blacklistusers:
                        Cooldown.writenewCooldown(str(userid))
                        if config['debug'] == True:
                            print(f"{datetime.datetime.now().time()}: Searching for trades with {userid} scraped from file.")
                        algorithmqueue.append(str(userid))
                time.sleep(int(config['scraping']['scrape_cooldown']))
            except:
                print(f'Unable to read {config["scraping"]["scrape_from_file"]["directory"]}')
    
    def scrapeHangout():
        while True:
            try:
                for user in httpx.get('https://atb-games-scraping.acier.repl.co/getusers').json():
                    if Cooldown.newcooldownOver(str(user)) == True and str(user) != '' and str(user) not in blacklistusers:
                        Cooldown.writenewCooldown(str(user))
                        if config['debug'] == True:
                            print(f"{datetime.datetime.now().time()}: Searching for trades with {user} scraped from trade hangout.")
                        algorithmqueue.append(str(user))           
            except Exception as e:
                print(f'Ignoring exception when scraping trade hangout: {e}')
            time.sleep(int(config['scraping']['scrape_cooldown']))
    
    def scrapeOwnership():
        while True:
            try:
                if config['scraping']['ownership_updates']['item_ids']:
                    for itemid in config['scraping']['ownership_updates']['item_ids']:
                        getOwnership = httpx.get(f'https://rblx.trade/api/v2/asset/{itemid}/ownership-history?limit=100', timeout=30)
                        if getOwnership.status_code == 200:
                            for userid in getOwnership.json()['data']:
                                oldowner = userid['previousUserId']
                                newowner = userid['userId']
                                if oldowner != None:
                                    if Cooldown.newcooldownOver(str(oldowner)) == True and str(oldowner) not in blacklistusers:
                                        Cooldown.writenewCooldown(str(oldowner))
                                        if config['debug'] == True:
                                            print(f"{datetime.datetime.now().time()}: Searching for trades with {oldowner} scraped from {itemid} ownership changes.")
                                        algorithmqueue.append(str(oldowner)) 
                                if newowner != None:
                                    if Cooldown.newcooldownOver(str(newowner)) == True and str(newowner) not in blacklistusers:
                                        Cooldown.writenewCooldown(str(newowner))
                                        if config['debug'] == True:
                                            print(f"{datetime.datetime.now().time()}: Searching for trades with {newowner} scraped from {itemid} ownership changes.")
                                        algorithmqueue.append(str(newowner)) 
            except Exception as e:
                print(f'Ignoring exception in scrapeOwnership: {e}')
            time.sleep(int(config['scraping']['scrape_cooldown']))

    def getDetails(tradeid):
        alreadyinboundchecked.append(str(tradeid))
        details = requests.get(f'https://trades.roblox.com/v1/trades/{tradeid}', cookies=defaultCookie)
        if details.status_code == 200:
            givingvalue = 0
            gettingvalue = 0
            givingraw = []
            gettingraw = []
            user = details.json()['offers'][1]['user']['id']
            for item in details.json()['offers'][0]['userAssets']: 
                if Valuation.ismarkedProjected(str(item['assetId'])) == True:
                    offervalue = Valuation.getroliValue(item['assetId']) * config['valuation']['projecteds']['owned_projecteds']['owned_projected_multiplier']
                else:
                    offervalue = Valuation.getroliValue(item['assetId'])
                givingvalue += offervalue
                givingraw.append(item['assetId'])
            for item2 in details.json()['offers'][1]['userAssets']:
                if Valuation.ismarkedProjected(str(item2['assetId'])) == True:
                    if config['inbound_sniper']['ignore_projecteds'] == False:
                        requestvalue = Valuation.getroliValue(item2['assetId']) * config['valuation']['projecteds']['owned_projecteds']['owned_projected_multiplier']
                    else:
                        requestvalue = 0
                else:
                    requestvalue = Valuation.getroliValue(item2['assetId'])
                gettingvalue += requestvalue
                gettingraw.append(item2['assetId'])
            fixgiving = float(givingvalue) * float(config['inbound_sniper']['minimum_request_multiplier'])
            if float(fixgiving) <= float(gettingvalue):
                if config['inbound_sniper']['notify']['send_notifications']:
                    fancygiving = []
                    fancygetting = []
                    for item in givingraw:
                        fancygiving.append(f'{Scraping.getName(item)} ({Valuation.getroliValue(item)}')
                    for item in gettingraw:
                        fancygetting.append(f'{Scraping.getName(item)} ({Valuation.getroliValue(item)}')

                    percentincrease = (gettingvalue - givingvalue) / givingvalue
                    wincalculation = round(float((percentincrease)) * 100, 2)
                    if not wincalculation < 0:
                        winbool = '+'
                    else:
                        winbool = ''
                    print(f'{datetime.datetime.now().time()}: Detected inbound win {tradeid} {fancygiving} for {fancygetting} ({winbool}{wincalculation}%)')
                    if config['inbound_sniper']['notify']['send_notifications'] == True:
                        Webhooks.sendInbound(user, givingraw, gettingraw, tradeid)
        elif details.status_code == 429:
            time.sleep(config['inbound_sniper']['scrape_interval'])
            return Scraping.getDetails(tradeid)
        else:
            print(f'Unknown status code in getDetails. {details.text}')

    def getInbounds():
        getinbounds = requests.get('https://trades.roblox.com/v1/trades/inbound?cursor=&limit=100&sortOrder=Desc', cookies=defaultCookie)
        if getinbounds.status_code == 200:
            for trade in getinbounds.json()['data']:
                if str(trade['id']) not in alreadyinboundchecked:
                    Scraping.getDetails(trade['id'])
        elif getinbounds.status_code == 429:
            print(f'Ratelimited when trying to grab inbound trades list. Waiting and retrying.')
            time.sleep(config['inbound_sniper']['scrape_interval'])
            return Scraping.getInbounds()
        else:
            print(f'Unknown status code in getInbounds. {getinbounds.text}')


class ThreadWorker:
    def inboundSniper():
        while True:
            try:
                Scraping.getInbounds()
                time.sleep(config['inbound_sniper']['scrape_interval'])
            except Exception as e:
                print(f'Ignoring exception in inboundSniper: {e}')
    def inventoryUpdater():
        global selfinventory
        while True:
            time.sleep(60)
            try:
                selfinventory = Acier.getselfInventory()
                print(f'{datetime.datetime.now().time()}: Successfully updated {len(selfinventory)} inventory items')
            except Exception as e:
                print(f'Ignoring exception in inventoryUpdater: {e}')
    def inventoryQueue():
        while True:
            try:
                if algorithmqueue:
                    if len(queue) <= config['queue']['maximum_queue']:
                        user = algorithmqueue.pop(0)
                        inventory = Acier.getInventory(user)
                        if inventory and selfinventory:
                            if config['debug'] == True:
                                print(f'{datetime.datetime.now().time()}: Successfully scraped {len(inventory)} items from {user}')
                            if config['trading']['experimental_algorithm']['use_over_legacy'] == True:
                                tradetype = 'experimental'
                                combination = Algo.ballgAgo(selfinventory, inventory)
                            else:
                                tradetype = 'legacy'
                                combination = Algo.acierhothotAlgo(selfinventory, inventory, config['trading']['legacy_algorithm']['minimum_request_multiplier'], config['trading']['legacy_algorithm']['maximum_request_multiplier'])
                                #combination = Algo.acierhothotAlgo(selfinventory, inventory, config['trading']['legacy_algorithm']['minimum_request_multiplier'], config['trading']['legacy_algorithm']['maximum_request_multiplier'])
                                if combination:
                                    combination = combination[0]
                            if combination:
                                print(f'{datetime.datetime.now().time()}: Found trade with {user}. Queue length is now {len(queue) + 1}')
                                fancyoffer = []
                                fancyrequest = []

                                givingval = 0
                                receval = 0
                                for item in combination['sending']:
                                    val = Valuation.getroliValue(item["assetId"])
                                    givingval += val
                                    fancyoffer.append(f'{item["name"]} ({val})')
                                for item in combination['recieving']:
                                    val = Valuation.getroliValue(item["assetId"])
                                    receval += val
                                    fancyrequest.append(f'{item["name"]} ({val})')
                                
                                wincalculation = round(((receval - givingval) / givingval) * 100, 2)
                                #wincalculation = round(float((combination["multiplier"]) - 1) * 100, 2)
                                if not wincalculation < 0:
                                    winbool = '+'
                                else:
                                    winbool = ''
                                if tradetype == 'experimental':
                                    fancymessage = f'{datetime.datetime.now().time()}: Successfully sent {fancyoffer} for {fancyrequest} \033[1m{combination["type"]}\033[0m to {user} (\033[1m{winbool}{wincalculation}\033[0;0m%)'
                                    fancybefore = f'{datetime.datetime.now().time()}: Attempting to send {fancyoffer} for {fancyrequest} \033[1m{combination["type"]}\033[0m to {user} (\033[1m{winbool}{wincalculation}\033[0;0m%)'
                                else:
                                    fancymessage = f'{datetime.datetime.now().time()}: Successfully sent {fancyoffer} for {fancyrequest} to {user} (\033[1m{winbool}{wincalculation}\033[0;0m%)'
                                    fancybefore = f'{datetime.datetime.now().time()}: Attempting to send {fancyoffer} for {fancyrequest} to {user} (\033[1m{winbool}{wincalculation}\033[0;0m%)'
                                
                                givingraw = []
                                gettingraw = []
                                for item in combination['sending']:
                                    givingraw.append(item['assetId'])
                                for item in combination['recieving']:
                                    gettingraw.append(item['assetId'])

                                givingrawuaid = []
                                gettingrawuaid = []
                                for item in combination['sending']:
                                    givingrawuaid.append(item['uaid'])
                                for item in combination['recieving']:
                                    gettingrawuaid.append(item['uaid'])

                                queue.append({'giving': givingrawuaid, 'getting': gettingrawuaid, 'user': user, 'givingraw': givingraw, 'gettingraw': gettingraw, 'fancymessage': fancymessage, 'fancybefore': fancybefore})
            except Exception as e:
              print(f'Ignoring exception in inventoryQueue: {e}')
    def shuffleuserQueue():
        while True:
            try:
                time.sleep(30)
                if algorithmqueue:
                    random.shuffle(algorithmqueue)
                print(f'{datetime.datetime.now().time()}: Successfully shuffled scraped queue of {len(queue)} and users queue of {len(algorithmqueue)} users')
            except Exception as e:
                print(f'Ignoring exception in shuffleuserQueue: {e}')
    def tradesperMinute():
        while True:
            time.sleep(60)
            print(f'{datetime.datetime.now().time()}: Sent {len(outboundsentcheck)} trades in 1 minute!')
            outboundsentcheck.clear()
    def databaseScrape():
        while True:
            try:
                cachedusers = httpx.get('https://acier-whitelist.acier.repl.co/cachedsorted', timeout=30)
                for user in cachedusers.json()['users']:
                    if Cooldown.newcooldownOver(str(user)) == True and str(user) not in blacklistusers:
                        Cooldown.writenewCooldown(str(user))
                        algorithmqueue.append(user)
            except Exception as e:
                print(f'Ignoring exception in databaseScrape: {e}')
            time.sleep(3600)
    def workThreads(task):
        if task ==  'completed':
            firstInventoryCheck()
            while True:
                try:
                    time.sleep(2.5)
                    secondInventoryCheck()
                    compareInventories()
                except Exception as e:
                    print(f'Ignoring exception in completed notifier: {e}')
        if task == 'tradesperMinute':
            ThreadWorker.tradesperMinute()
        if task == 'database':
            ThreadWorker.databaseScrape()
        if task == 'blacklist':
            while True:
                time.sleep(600)
                try:
                    Valuation.initializeBlacklist()
                except Exception as e:
                    print(f'Ignoring exception in initializeBlacklist: {e}')
        if task == 'inboundSniper':
            time.sleep(10)
            ThreadWorker.inboundSniper()
        if task == 'silentAuth':
            Auth.silentAuthenticate()
        if task == 'sendQueue':
            Updater.sendQueue()
        if task == 'inventoryUpdater':
            ThreadWorker.inventoryUpdater()
        if task == 'inventoryQueue':
            ThreadWorker.inventoryQueue()
        if task == 'ownership':
            Scraping.scrapeOwnership() 
        if task == 'scrapeRopro':
            Scraping.scrapeRopro()
        if task == 'scrapeFlip':
            Scraping.scrapeFlip()
        if task == 'scrapeRolimons':
            Scraping.scrapeRolimons()
        if task == 'scrapeTxt':
            Scraping.scrapeTxt()
        if task == 'scrapeHangout':
            Scraping.scrapeHangout()
        if task == 'shuffleuserQueue':
            ThreadWorker.shuffleuserQueue()
        # if task == 'owners':
        #     while True:
        #         currentowners = []
        #         for item in itemdetails.json()['items']:
        #             currentowners.append(item)
        #         if config['scraping']['owners']['shuffle_items'] == True:
        #             random.shuffle(currentowners)
        #         for itemc in currentowners:
        #             try:
        #                 Scraping.getroliOwners(itemc)
        #                 time.sleep(config['scraping']['scrape_cooldown'])
        #             except Exception as e:
        #                 print(f'Ignoring error {e} when scraping item owners for {item}')
        #                 time.sleep(config['scraping']['scrape_cooldown'])
        if task == 'consoleTitler':
            Auth.consoleTitler()
        if task == 'dumpvalues':
            while True:
                time.sleep(60)
                with open('config.json', 'r+', encoding='utf-8') as cfgfile:
                    try:
                        config = json.load(cfgfile)
                    except:
                        print(f'{datetime.datetime.now().time()}: Your config file is in invalid format. Please troubleshoot it using jsonformatter.curiousconcept.com')
                try:
                    newvalues = values.copy()
                    with open('values.json', "w") as jsonFile:
                        json.dump(newvalues, jsonFile)
                except Exception as e:
                    print(f'Ignoring exception when dumping values: {e}')
                
                if config['save_cooldown'] == True:
                    try:
                        newcooldown = cooldown.copy()
                        with open('cooldown.json', "w") as jsonFile:
                            json.dump(newcooldown, jsonFile)
                    except Exception as e:
                        print(f'Ignoring exception when dumping cooldown: {e}')
                
                try:
                    with open('cached_inbounds.json', "w") as jsonFile:
                        json.dump(alreadyinboundchecked, jsonFile)
                except Exception as e:
                    print(f'Ignoring exception when dumping inbound: {e}')
                

def getactualRap(item):
        global itemdetails
        return itemdetails.json()['items'][str(item)][2]

class Webhooks:
    def sendCompleted(give, get):
        givingFormatted = ''
        gettingFormatted = ''
        givingValue = 0
        gettingValue = 0
        givingrap = 0
        gettingrap = 0

        for item in give:
            givingFormatted += f'``{Valuation.getroliValue(item)}`` [{Scraping.getName(item)}](https://rolimons.com/item/{item}) '
            if Valuation.ismarkedProjected(item) == True:
                givingFormatted += '⚠️'
            if Valuation.isRare(item) == True:
                givingFormatted += '💎'

            givingFormatted += '\n'

            givingValue += Valuation.getroliValue(item)
            givingrap += getactualRap(item)
        for item in get:
            gettingFormatted += f'``{Valuation.getroliValue(item)}`` [{Scraping.getName(item)}](https://rolimons.com/item/{item}) '
            if Valuation.ismarkedProjected(item) == True:
                gettingFormatted += '⚠️'
            if Valuation.isRare(item) == True:
                gettingFormatted += '💎'
            gettingFormatted += '\n'
            gettingValue += Valuation.getroliValue(item)
            gettingrap += getactualRap(item)

        winpercentage = round(((gettingValue - givingValue) / givingValue) * 100, 2)
        winrap = round(((gettingrap - givingrap) / givingrap) * 100, 2)
        embed = dhooks.Embed(
            description=f':euro: {gettingValue - givingValue} ({winpercentage}%)\n:dollar: {gettingrap - givingrap} ({winrap}%)',
            color=0x7cf04e,
            timestamp='now'
        )
        grin = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/160/twitter/53/money-with-wings_1f4b8.png'
        #headshot = f'https://www.roblox.com/headshot-thumbnail/image?userId={user}&width=150&height=150&format=png'

        embed.set_author(name=f'new completed trade detected !!', icon_url=grin)


        #embed.add_field(name='Profit', value=f'{gettingValue - givingValue} ({winpercentage}%)')
        embed.add_field(name=f':outbox_tray: offer - ``{givingValue}``', value=f'{givingFormatted}')
        embed.add_field(name=f':inbox_tray: request - ``{gettingValue}``', value=f'{gettingFormatted}')

        embed.set_footer(text=f'acier trade bot | acier.gg')
        #embed.set_thumbnail(headshot)
        
        completedhook.send(config['completed_notifier']['mention'])
        completedhook.send(embed=embed)


    def sendOutbound(user, give, get):
        givingFormatted = ''
        gettingFormatted = ''
        givingValue = 0
        gettingValue = 0
        givingrap = 0
        gettingrap = 0

        for item in give:
            givingFormatted += f'``{Valuation.getroliValue(item)}`` [{Scraping.getName(item)}](https://rolimons.com/item/{item}) '
            if Valuation.ismarkedProjected(item) == True:
                givingFormatted += '⚠️'
            if Valuation.isRare(item) == True:
                givingFormatted += '💎'

            givingFormatted += '\n'

            givingValue += Valuation.getroliValue(item)
            givingrap += getactualRap(item)
        for item in get:
            gettingFormatted += f'``{Valuation.getroliValue(item)}`` [{Scraping.getName(item)}](https://rolimons.com/item/{item}) '
            if Valuation.ismarkedProjected(item) == True:
                gettingFormatted += '⚠️'
            if Valuation.isRare(item) == True:
                gettingFormatted += '💎'
            gettingFormatted += '\n'
            gettingValue += Valuation.getroliValue(item)
            gettingrap += getactualRap(item)

        winpercentage = round(((gettingValue - givingValue) / givingValue) * 100, 2)
        winrap = round(((gettingrap - givingrap) / givingrap) * 100, 2)
        embed = dhooks.Embed(
            description=f':euro: {gettingValue - givingValue} ({winpercentage}%)\n:dollar: {gettingrap - givingrap} ({winrap}%)',
            color=0xffd966,
            timestamp='now'
        )
        grin = 'https://images.emojiterra.com/twitter/512px/1f601.png'
        headshot = f'https://www.roblox.com/headshot-thumbnail/image?userId={user}&width=150&height=150&format=png'
        chicken = f'https://static.wikia.nocookie.net/roblox/images/4/40/Sparkle_Time_Chicken.png/revision/latest?cb=20170212065201'

        embed.set_author(name=f'successfully sent trade to {Scraping.getuserName(user)} ({user})', icon_url=grin)
    

        #embed.add_field(name='Profit', value=f'{gettingValue - givingValue} ({winpercentage}%)')
        embed.add_field(name=f':outbox_tray: offer - ``{givingValue}``', value=f'{givingFormatted}')
        embed.add_field(name=f':inbox_tray: request - ``{gettingValue}``', value=f'{gettingFormatted}')

        embed.set_footer(text=f'acier.gg | {len(queue) + 1} trades in queue', icon_url=chicken)
        embed.set_thumbnail(headshot)

        outboundhook.send(embed=embed)
    
    def sendInbound(user, give, get, trade):
        givingFormatted = ''
        gettingFormatted = ''
        givingValue = 0
        gettingValue = 0
        givingrap = 0
        gettingrap = 0

        for item in give:
            givingFormatted += f'``{Valuation.getroliValue(item)}`` [{Scraping.getName(item)}](https://rolimons.com/item/{item}) '
            if Valuation.ismarkedProjected(item) == True:
                givingFormatted += '⚠️'
            if Valuation.isRare(item) == True:
                givingFormatted += '💎'

            givingFormatted += '\n'
            givingValue += Valuation.getroliValue(item)
            givingrap += getactualRap(item)
        for item in get:
            gettingFormatted += f'``{Valuation.getroliValue(item)}`` [{Scraping.getName(item)}](https://rolimons.com/item/{item}) '
            if Valuation.ismarkedProjected(item) == True:
                gettingFormatted += '⚠️'
            if Valuation.isRare(item) == True:
                gettingFormatted += '💎'
            gettingFormatted += '\n'
            gettingValue += Valuation.getroliValue(item)
            gettingrap += getactualRap(item)

        winpercentage = round(((gettingValue - givingValue) / givingValue) * 100, 2)

        winrap = round(((gettingrap - givingrap) / givingrap) * 100, 2)
        inboundhook.send(config['inbound_sniper']['notify']['mention'])
        embed = dhooks.Embed(
            description=f':euro: {gettingValue - givingValue} ({winpercentage}%)\n:dollar: {gettingrap - givingrap} ({winrap}%)\n:yen: id: {trade}',
            color=0xffd966,
            timestamp='now'
        )
        headshot = f'https://www.roblox.com/headshot-thumbnail/image?userId={user}&width=150&height=150&format=png'
        chicken = f'https://static.wikia.nocookie.net/roblox/images/4/40/Sparkle_Time_Chicken.png/revision/latest?cb=20170212065201'
        grin = 'https://images.emojiterra.com/twitter/512px/1f601.png'

        embed.set_author(name=f'received inbound win from {Scraping.getuserName(user)} ({user})', icon_url=grin)

        embed.add_field(name=f':outbox_tray: offer - ``{givingValue}``', value=f'{givingFormatted}')
        embed.add_field(name=f':inbox_tray: request - ``{gettingValue}``', value=f'{gettingFormatted}')

        embed.set_thumbnail(headshot)

        inboundhook.send(embed=embed)

class Checking:
    def doublecheckOffer(offeruaids, requestuaids, user):
        myinventory = selfinventory
        userinventory = Acier.getInventory(user)
        if myinventory and userinventory:
            validofferitems = 0
            validrequestitems = 0
            for item in myinventory:
                if str(item['uaid']) in offeruaids:
                    validofferitems += 1
            
            for item in userinventory:
                if str(item['uaid']) in requestuaids:
                    validrequestitems += 1
            
            if len(offeruaids) == validofferitems and len(requestuaids) == validrequestitems:
                return True
            else:
                print(f'{datetime.datetime.now().time()}: Removed trade with {user} from the queue as an item offered in the trade is no longer owned. Re-entering {user} into the scraped queue.')
                algorithmqueue.append(str(user))
                return False
        else:
            print(f'{datetime.datetime.now().time()}: Removed trade with {user} from the queue as an item offered in the trade is no longer owned. Re-entering {user} into the scraped queue (null inventory).')

class Auth:
    def consoleTitler():
        try:
            while True:
                ctypes.windll.kernel32.SetConsoleTitleW(f"acier trade bot | sent: {len(outboundsent)} | queue: {len(queue)} | user queue: {len(algorithmqueue)}")
                time.sleep(1)
        except:
            pass

    def silentAuthenticate():
        global itemdetails
        while True:
            time.sleep(600)
            try:
                itemdetails = httpx.get("https://www.rolimons.com/itemapi/itemdetails", timeout=30)
            except Exception as e:
                print(f'{datetime.datetime.now().time()}: Failed to update item details ...')
            try:
                linkeduser = requests.get('https://acier-whitelist.acier.repl.co/getlinkeduser', timeout=30, data={'username': config['authentication']['whitelist_username'], 'password': config['authentication']['whitelist_password']})
                if linkeduser.json()['success'] == True:
                    if not str(linkeduser.json()['linked']) == Auth.md5(str(config['authentication']['userid'])):
                        print(f'Whitelist check failed. userid mismatch.')
                        current_system_pid = os.getpid()
                        ThisSystem = psutil.Process(current_system_pid)
                        ThisSystem.terminate()
            except Exception as e:
                print(f'Whitelist check failed. Send this to acier: {e}')
                current_system_pid = os.getpid()
                ThisSystem = psutil.Process(current_system_pid)
                ThisSystem.terminate()


    def md5(str):
        return hashlib.md5(str.encode()).hexdigest()

    def Authenticate(token):
        for i in range(1 + 1):
            attemptHash = Auth.md5(f"acierballg{config['authentication']['userid']}" + str(int(time.time() / 60 ) - i))
            if(attemptHash == token): 
                return True
        return False

if config['outbound']['notify']['send_notifications']:
    outboundhook = dhooks.Webhook(config['outbound']['notify']['discord_webhook_url'])

if config['completed_notifier']['notify']:
    completedhook = dhooks.Webhook(config['completed_notifier']['discord_webhook_url'])


if config['inbound_sniper']['notify']['send_notifications']:
    inboundhook = dhooks.Webhook(config['inbound_sniper']['notify']['discord_webhook_url'])

#Webhooks.sendOutbound(3583776911, [115363212], [138932314, 48545806])

ctypes.windll.kernel32.SetConsoleTitleW("acier trade bot | sent: 0 | queue: 0 | user queue: 0")
formattedinventory = []
unformattedinventory = []
getlinkedData = httpx.get('https://users.roblox.com/v1/users/authenticated', cookies=defaultCookie, timeout=30)
if getlinkedData.status_code == 200 and str(getlinkedData.json()['id']) == str(config['authentication']['userid']):
    getserverResponse = httpx.post('https://acier-whitelist.acier.repl.co/authenticate', timeout=30, data={'username': config['authentication']['whitelist_username'], 'password': config['authentication']['whitelist_password'], 'hwid': ''})
    if "token" in getserverResponse.text:
        if Auth.Authenticate(getserverResponse.json()['token']):
            inventory = Acier.getselfInventory()
            for item in inventory:
                value = Cooldown.getsavedValue('offer', item["assetId"])

                if str(item['assetId']) == '241671883':
                    formattedinventory.append(f"SPARKLE TIME CHICKEN ({value})")
                else:
                    formattedinventory.append(f"{item['name']} ({value})")
                unformattedinventory.append(item['assetId'])
            
            if "241671883" in unformattedinventory or 241671883 in unformattedinventory:
                stc = True
                print("""
        ░▒███████
        ░██▓▒░░▒▓██
        ██▓▒░  ░▒▓██   ██████
        ██▓▒░    ░▓███▓  ░▒▓██
        ██▓▒░   ░▓██▓     ░▒▓██
        ██▓▒░               ░▒▓██
        ██▓▒░              ░▒▓██
        ██▓▒░            ░▒▓██
        ██▓▒░          ░▒▓██
            ██▓▒░        ░▒▓██
            ██▓▒░     ░▒▓██
            ██▓▒░  ░▒▓██
            █▓▒░░▒▓██
                ░▒▓██
            ░▒▓██
            ░▒▓██""")
            else:
                stc = False
            print(f'{datetime.datetime.now().time()}: Successfully authenticated {getlinkedData.json()["name"]} ({getlinkedData.json()["id"]})')
            try:
                version = httpx.get('https://acier-whitelist.acier.repl.co/version', timeout=30)
                if version.json()['version'] > VERSION:
                    print(f'{datetime.datetime.now().time()}: You\'re using an outdated version of acier trade bot. Please download v{version.json()["version"]} @ acier.gg/downloads for a better user experience.')
            except:
                pass
            Valuation.initializeBlacklist()
            selfinventory = Acier.getselfInventory()
            print(f'{datetime.datetime.now().time()}: Tradable inventory: {formattedinventory}')
            threads = ['tradesperMinute', 'inventoryUpdater','silentAuth', 'blacklist', 'consoleTitler', 'dumpvalues']
            if stc == False:
                if config['threads']['combination_threads'] <= 3:
                    for _ in range(config['threads']['combination_threads']):
                        threads.append('inventoryQueue')
                else:
                    print(f'{datetime.datetime.now().time()}: Set your combination threads to 3 because you don\'t own a sparkle time chicken ...')
                    for _ in range(3):
                        threads.append('inventoryQueue')
            else:
                for _ in range(config['threads']['combination_threads']):
                    threads.append('inventoryQueue')

            for _ in range(config['threads']['trade_send_threads']):
                threads.append('sendQueue')

            if config['completed_notifier']['notify'] == True:
                threads.append('completed')
            if config['scraping']['ropro_trade_ads'] == True:
                threads.append('scrapeRopro')
            if config['scraping']['rolimons_trade_ads'] == True:
                threads.append('scrapeRolimons')
            if config['scraping']['rbxflip'] == True:
                threads.append('scrapeFlip')
            if config['scraping']['trade_hangout'] == True:
                threads.append('scrapeHangout')
            if config['scraping']['scrape_from_file']['enabled'] == True:
                threads.append('scrapeTxt')
            if config['scraping']['ownership_updates']['enabled'] == True:
                threads.append('ownership')
            if config['inbound_sniper']['enabled'] == True:
                threads.append('inboundSniper')
            if config['scraping']['shuffle_queues'] == True:
                threads.append('shuffleuserQueue')

            #f config['scraping']['database_scraping'] == True:
            threads.append('database')

            for task in threads:
                threading.Thread(target=ThreadWorker.workThreads, args=[task]).start()

            #Cooldown.writenewValue('4390891467', 69, 420)
            #print(Cooldown.getsavedValue(241671883))
        else:
            print(f'{datetime.datetime.now().time()}: your roblox account is not whitelisted ...')
            time.sleep(5)
    else:
        print(f'{datetime.datetime.now().time()}: your whitelist username and/or password are invalid ...')
        time.sleep(5)
else:
    print(f'{datetime.datetime.now().time()}: Failed to authenticate with roblox ...')
    time.sleep(5)