#!/usr/bin/env python3

from os import getenv, path, makedirs
from json import loads
from shutil import copytree
# Locatie van home directory, zo kunnen we ons bij volgende directories hierop baseren.
home = getenv('HOME')

# Best Practices voor locaties van bestanden voor een CLI tool
usr_data = f'{home}/.local/share/recon-pipeline/dumps/'
conf_path = f'{home}/.config/recon-pipeline'
path_to_script = path.dirname(path.realpath(__file__))
src_conf_path = f'{path_to_script}/conf/'
conf_file_path = f'{conf_path}/config.json'
log_file_path = f'{home}/.local/share/recon-pipeline/run.log'

# Controleren of configuratiemap bestaat, anders kopieren van conf/conf.json naar conf_path
if not path.exists(conf_path):
	copytree(src_conf_path, conf_path, dirs_exist_ok=True)

# Controleren of gegevensmap bestaat, anders aanmaken
if not path.exists(usr_data):
	makedirs(usr_data, exist_ok=True)
	
# Uitlezen van de configuratie instellingen uit het configuratiebestand
with open(conf_file_path, 'r') as config_file:
	config_read = config_file.read()
	config_json = loads(config_read)
	timeout = config_json['common']['timeout']

	ssl_port = config_json['ssl_cert']['ssl_port']

	port_scan_th = config_json['port_scan']['threads']

	export_fmt = config_json['export']['format']
