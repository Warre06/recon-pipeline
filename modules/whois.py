#!/usr/bin/env python3

import asyncio
from json import load
from modules.export import export
from modules.write_log import log_writer
# Definieren van de gebruikte kleuren zodat ik niet altijd de ANSI color code als argument moet meegeven
R = '\033[31m'  # rood
G = '\033[32m'  # groen
C = '\033[36m'  # cyaan
W = '\033[0m'   # wit
Y = '\033[33m'  # geel

# Async functie om WHOIS-informatie op te halen bij een WHOIS-server
async def get_whois(domain, server):
	whois_result = {}
	reader, writer = await asyncio.open_connection(server, 43)
	writer.write((domain + '\r\n').encode())
	# Tussentijdse variabele om snel te controleren of er whois gegevens zijn voor een domein of niet, zie lijn 30
	raw_resp = b''
	while True:
		chunk = await reader.read(4096)
		if not chunk:
			break
		raw_resp += chunk

	writer.close()
	await writer.wait_closed()
	raw_result = raw_resp.decode()
	# Checkt of er een match is in de whois gegevens, zo niet wordt whois_result=None
	if 'No match for' in raw_result:
		whois_result = None

	res_parts = raw_result.split('>>>', 1)
	whois_result['whois'] = res_parts[0]
	return whois_result

# Functie voor whois lookup van een domein
def whois_lookup(domain, tld, script_path, output, data):
	result = {}
	# Locatie van onze WHOIS servers waar we informatie gaan van opvragen
	db_path = f'{script_path}/whois_servers.json'
	with open(db_path, 'r') as db_file:
		db_json = load(db_file)
	print(f'\n{Y}[!] Whois Lookup : {W}\n')

	try:
		whois_sv = db_json[tld]
		whois_info = asyncio.run(get_whois(domain, whois_sv))
		print(whois_info['whois'])
		result.update(whois_info)
	except KeyError:
		print(f'{R}[-] Error : {C}Dit domein suffix wordt niet ondersteund.{W}')
		result.update({'Error': 'Dit domein suffix wordt niet ondersteund.'})
		log_writer('[whois] Exception = Dit domein suffix wordt niet ondersteund.')
	except Exception as exc:
		print(f'{R}[-] Error : {C}{exc}{W}')
		result.update({'Error': str(exc)})
		log_writer(f'[whois] Exception = {exc}')

	result.update({'exported': False})
	# Resultaat wegschrijven
	if output != 'None':
		fname = f'{output["directory"]}/whois.{output["format"]}'
		output['file'] = fname
		data['module-whois'] = result
		export(output, data)
	# Status loggen 
	log_writer('[whois] Completed')