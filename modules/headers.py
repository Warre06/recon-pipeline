#!/usr/bin/env python3

import requests
from modules.export import export
from modules.write_log import log_writer

#Uitschakelen van SSL waarschuwingen
requests.packages.urllib3.disable_warnings()

# Definieren van de gebruikte kleuren zodat ik niet altijd de ANSI color code als argument moet meegeven
R = '\033[31m'  # roord
G = '\033[32m'  # groen
C = '\033[36m'  # cyaan
W = '\033[0m'   # wit
Y = '\033[33m'  # geel

#Effectieve functie om de headers op te vragen, 
def headers(target, output, data):
	result = {}
	print(f'\n{Y}[!] Headers :{W}\n')
	try:
		# GET request sturen naar target URL zonder SSL Verificatie
		rqst = requests.get(target, verify=False, timeout=10)
		# Loopen door hears en printen
		for key, val in rqst.headers.items():
			print(f'{C}{key} : {W}{val}')
			# De results dictionary bijwerken met de gevonden headers
			if output != 'None':
				result.update({key: val})
	except Exception as exc:
		# Indien exception optreed, printen
		print(f'\n{R}[-] {C}Exception : {W}{exc}\n')
		if output != 'None':
			result.update({'Exception': str(exc)})
		log_writer(f'[headers] Exception = {exc}')
	#Indien exception optrad gaan we het resultaat als niet-exported loggen in results
	result.update({'exported': False})

	if output != 'None':
		#Filename prepareren om op te kunnen slaan
		fname = f'{output["directory"]}/headers.{output["format"]}'
		output['file'] = fname
		data['module-headers'] = result
		#Data exporteren
		export(output, data)
	# Status Loggen naar terminal
	log_writer('[headers] Completed')
