import requests
import json
import datetime
import time

def get_share_list():
	share = requests.get('https://api-invest.tinkoff.ru/openapi/sandbox/market/stocks/', 
		headers={'Content-Type':'application/json', 'Authorization': 'Bearer {}'.format(token_dev)})
	return str(share.json())



def get_orderbook(status, token, figi, depth):
	if( status == 'y'): sandbox = 'sandbox/'
	else: sandbox = ''

	book = requests.get('https://api-invest.tinkoff.ru/openapi/' + sandbox + 'market/orderbook/', 
		headers={'Content-Type':'application/json', 'Authorization': 'Bearer {}'.format(token)},
	  params={'figi':figi, 'depth':depth})
	return book.json()
	

def get_candles(status, token, figi, tfrom, tto, interval):
	if( status == 'y'): sandbox = 'sandbox/'
	else: sandbox = ''

	candles = requests.get('https://api-invest.tinkoff.ru/openapi/' + sandbox + 'market/candles', 
		headers={'Content-Type':'application/json', 'Authorization': 'Bearer {}'.format(token)},
	  params={'figi':figi, 'from':tfrom, 'to':tto, 'interval':interval})
	return candles.json()





token_prod = '' # тут боевой токен
token_dev = '' # тут токен для тестового режима
cara_figi = 'BBG001J2QYS9'

#req = get_orderbook('y', token_dev, cara_figi, 10)
#print(req['payload']['lastPrice'])

def date_time():
	now = datetime.datetime.now()
	date_format = now.strftime('%Y-%m-%dT%H:%M:%S+03:00')
	old_date = now - datetime.timedelta(hours=1)
	old_date_format = old_date.strftime('%Y-%m-%dT%H:%M:%S+03:00')
	return date_format, old_date_format

def reqest_price():
	dat = date_time()
	req = get_candles('n', token_prod, cara_figi, dat[1], dat[0], '5min') # 'n' при вызове функции - бовой запрос, 'y' - будет режим песочницы
	return req

def examination_price():
	try:
		time.sleep(1)
		req = reqest_price()
		time.sleep(1)
		req_orderbook = get_orderbook('n', token_prod, cara_figi, 1)

		if (req['payload']['candles'] == []):
			print('пустой массив')
			print(req_orderbook)
		price_open = req['payload']['candles'][-1]['c']
		price_close = req_orderbook['payload']['asks'][0]['price']
		difference = 100 - ( 100 / price_open * price_close)
		dat = date_time()
		if ( difference >= 0.5):
			file = open('traid_test_cara.txt', 'a')
			file.write('buy cara [' + dat[0] + '] price: ' + str(price_close) + '\n')
			while True:
				time.sleep(2)
				new_req_orderbook = get_orderbook('n', token_prod, cara_figi, 1)
				new_price_close = new_req_orderbook['payload']['bids'][0]['price']
				new_difference = 100 - ( 100 / new_price_close * price_close)
				dat = date_time()
				if ( new_difference >= 0.5):
					profit = new_price_close - price_close
					file = open('traid_test_cara.txt', 'a')
					file.write('sell cara [' + dat[0] + '] price: ' + str(new_price_close) + ' profit: '+ str(round(profit, 2)) +'\n\n')
					file = open('traid_test_cara_log.txt', 'a')
					file.write('cara [' + dat[0] + '] new_difference: ' + str(round(new_difference, 2)) + '\n')
					break
				elif ( new_difference <= -0.5):
					no_profit = new_price_close - price_close
					file = open('traid_test_cara.txt', 'a')
					file.write('fail sell cara [' + dat[0] + '] price: ' + str(new_price_close) + ' profit: '+ str(round(no_profit, 2)) +'\n\n')
					file = open('traid_test_cara_log.txt', 'a')
					file.write('cara [' + dat[0] + '] new_difference: ' + str(round(new_difference, 2)) + '\n')
					break
		else:
			file = open('traid_test_cara_log.txt', 'a')
			file.write('cara [' + dat[0] + '] difference: ' + str(round(difference, 2)) + ' price open: ' + str(price_open) + ' close: ' + str(price_close) + '\n')
	except Exception as err:
		dat = date_time()
		file = open('traid_test_cara_log.txt', 'a')
		file.write('\nERROR [' + err + ']\n\n')
		return err


while True:
	e =	examination_price()
	if ( e != None):
		print('ERROR '+ e)
		break
	else:
		print('pass')


# req = get_orderbook('n', token_prod, cara_figi, 1)
# #print(req['payload']['asks']['price'])
# print(req['payload']['asks'][0]['price'])

#print(req['payload']['candles'][-1]['o'])






#file = open('cara_candle.txt', 'w')
#file.write(str(req))
#file.write(req.get('lastPrice'))



# 12.19 -> 11.91
# 100 - (100/цена открытия*цена закрытия)= >0.5 bay
# 100 - (100/цена закрытия текущая * цена покупки)= >1 sell

# 'o': 12, цена открытия
# 'c': 11.73, цена закрытия
# 'h': 12.01, максимальная цена
# 'l': 11.72, минимальная цена
# 'v': 21009, объем