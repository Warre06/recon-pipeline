#!/usr/bin/env python3

import os
import sys

R = '\033[31m'  # rood
G = '\033[32m'  # groen
C = '\033[36m'  # cyaan
W = '\033[0m'   # wit

from modules.write_log import log_writer
log_writer('Importeren configuratie...')
import settings as config

# De nodige variabele op basis van de configuratie (settings.py)
home = config.home
usr_data = config.usr_data
conf_path = config.conf_path
path_to_script = config.path_to_script
src_conf_path = config.src_conf_path

log_writer(
	f'PATHS = HOME:{home}, SCRIPT_LOC:{path_to_script},\
	CONFIG:{config.conf_file_path}, LOG:{config.log_file_path}'
)

import argparse

VERSION = '1.0.0'
log_writer(f'AUTO RECONNAISSANCE PIPELINE v{VERSION}')

# Parsen van alle nodige CLI argumenten voor een 
parser = argparse.ArgumentParser(description=f'Automated Reconnaisance Pipeline - Eindopdracht Ethical Hacking | v{VERSION}')
parser.add_argument('url', help='Target URL')
parser.add_argument('--headers', help='Header Information', action='store_true')
parser.add_argument('--sslinfo', help='SSL Certificate Information', action='store_true')
parser.add_argument('--whois', help='Whois Lookup', action='store_true')
parser.add_argument('--ps', help='Fast Port Scan', action='store_true')
parser.add_argument('--full', help='Full Recon Scan', action='store_true')

ext_help = parser.add_argument_group('Extra Opties')
ext_help.add_argument('-pt', type=int, help='Aantal threads voor port scan [ Default : 50 ]')
ext_help.add_argument('-T', type=float, help='Request Timeout [ Default : 30.0 ]')
ext_help.add_argument('-r', action='store_true', help='Allow Redirect [ Default : False ]')
ext_help.add_argument('-s', action='store_false', help='Toggle SSL Verification [ Default : True ]')
ext_help.add_argument('-sp', type=int, help='Specify SSL Port [ Default : 443 ]')
ext_help.add_argument('-e', help='File Extensions [ Example : txt, xml, php ]')
ext_help.add_argument('-o', help='Export Format [ Default : txt ]')
ext_help.set_defaults(
	pt=config.port_scan_th,
	T=config.timeout,
	sp=config.ssl_port,
	o=config.export_fmt
)

try:
	args = parser.parse_args()
except SystemExit:
	log_writer('[recon-pipeline] Help menu accessed')
	log_writer(f'{"-" * 30}')
	sys.exit()

# Toewijzen van de meegegeven argumenten aan variabele om mee te kunnen werken, dit houdt het overzichtelijker
target = args.url
headinfo = args.headers
sslinfo = args.sslinfo
whois = args.whois
pscan = args.ps
full = args.full
pscan_threads = args.pt
tout = args.T
sslv = args.s
sslp = args.sp
filext = args.e
output = args.o

import socket
import datetime
import ipaddress
import tldextract
from json import loads

type_ip = False
data = {}

# Ik vond een banner wel leuk, dus dit wordt weergegeven bij het runnen van het script
def banner():

	art = r'''
 _____ _____ 
|  _  |  _  |
|     |   __|
|__|__|__|'''
	print(f'{G}{art}{W}\n')
	print(f'{G}[>]{C} Auteur   :{W} Warre Gehre')
	print(f'{G}[>]{C} Version      :{W} {VERSION}\n')


try:
	banner()
    # Checkt of target geldige URL is, vaak gemaakte fout ! 
	if not target.startswith(('http', 'https')):
		print(f'{R}[-] {C}Protocol Mist, Vergeet niet {W}http:// {C}or{W} https:// \n')
		log_writer(f'Protocol missing in {target}, exiting')
		sys.exit(1)

	if target.endswith('/'):
		target = target[:-1]

	print(f'{G}[+] {C}Target : {W}{target}')
	ext = tldextract.extract(target)
	domain = ext.registered_domain
	if not domain:
		domain = ext.domain
	domain_suffix = ext.suffix

	if ext.subdomain:
		hostname = f'{ext.subdomain}.{ext.domain}.{ext.suffix}'
	else:
		hostname = domain

	try:
		ipaddress.ip_address(hostname)
		type_ip = True
		ip = hostname
	except Exception:
		try:
			ip = socket.gethostbyname(hostname)
			print(f'\n{G}[+] {C}IP Address : {W}{str(ip)}')
		except Exception as e:
			print(f'\n{R}[-] {C}Unable to Get IP : {W}{str(e)}')
			sys.exit(1)

	start_time = datetime.datetime.now()

	if output != 'None':
		fpath = usr_data
		dt_now = str(datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S'))
		fname = f'{fpath}fr_{hostname}_{dt_now}.{output}'
		respath = f'{fpath}fr_{hostname}_{dt_now}'
		if not os.path.exists(respath):
			os.makedirs(respath)
		out_settings = {
			'format': output,
			'directory': respath,
			'file': fname
		}
		log_writer(f'OUTPUT = FORMAT: {output}, DIR: {respath}, FILENAME: {fname}')

	if full:
		log_writer('Starting full recon...')

		
		from modules.sslinfo import cert
		from modules.portscan import scan
		from modules.headers import headers
		from modules.whois import whois_lookup

		headers(target, out_settings, data)
		cert(hostname, sslp, out_settings, data)
		whois_lookup(domain, domain_suffix, path_to_script, out_settings, data)
		scan(ip, out_settings, data, pscan_threads)
		
	if headinfo:
		from modules.headers import headers
		log_writer('Starting header enum...')
		headers(target, out_settings, data)

	if sslinfo:
		from modules.sslinfo import cert
		log_writer('Starting SSL enum...')
		cert(hostname, sslp, out_settings, data)

	if whois:
		from modules.whois import whois_lookup
		log_writer('Starting whois enum...')
		whois_lookup(domain, domain_suffix, path_to_script, out_settings, data)


	if pscan:
		from modules.portscan import scan
		log_writer('Starting port scan...')
		scan(ip, out_settings, data, pscan_threads)


	if not any([full, headinfo, sslinfo, whois, pscan]):
		print(f'\n{R}[-] Error : {C}Minstens 1 Argument Nodig met URL{W}')
		log_writer('At least One Argument is Required with URL, exiting')
		output = 'None'
		sys.exit(1)

	end_time = datetime.datetime.now() - start_time
	print(f'\n{G}[+] {C}Duur van scan {W}{str(end_time)}\n')
	log_writer(f'Completed in {end_time}')
	print(f'{G}[+] {C}Exported : {W}{respath}')
	log_writer(f'Exported to {respath}')
	log_writer(f'{"-" * 30}')
	sys.exit()
except KeyboardInterrupt:
	print(f'{R}[-] {C}Keyboard Interrupt.{W}\n')
	log_writer('Keyboard interrupt, exiting')
	log_writer(f'{"-" * 30}')
	sys.exit(130)
