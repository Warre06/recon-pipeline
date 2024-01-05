#!/usr/bin/env python3

import ssl
import socket
from modules.export import export
from modules.write_log import log_writer
from cryptography import x509
from cryptography.hazmat.backends import default_backend

# Definieren van de gebruikte kleuren zodat ik niet altijd de ANSI color code als argument moet meegeven
R = '\033[31m'  # rood
G = '\033[32m'  # groen
C = '\033[36m'  # cyaan
W = '\033[0m'   # wit
Y = '\033[33m'  # geel

# Functie voor het verkrijgen van SSL-certificaatinformatie van een het target
def cert(hostname, sslp, output, data):
	result = {}
	presence = False
	print(f'\n{Y}[!] SSL Certificate Information : {W}\n')
	# Controleren of SSL aanwezig is op opgegeven poort van doel
	port_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	port_test.settimeout(5)
	try:
		port_test.connect((hostname, sslp))
		port_test.close()
		presence = True
	except Exception:
		port_test.close()
		print(f'{R}[-] {C}SSL Is Niet Aanwezig Op Opgegeven URL ...Skipping...{W}')
		result.update({'Error': 'SSL Niet Aanwezig'})
		log_writer('[sslinfo] SSL Is Niet Aanwezig Op Opgegeven URL ...Skipping...')
	# Hulpfunctie voor het uitpakken van geneste tuples in de dictionaries van het certificaat
	def unpack(nested_tuple, pair):
		for item in nested_tuple:
			if isinstance(item, tuple):
				if len(item) == 2:
					pair[item[0]] = item[1]
				else:
					unpack(item, pair)
			else:
				pair[nested_tuple.index(item)] = item
	# Functie voor verwerken van SSL-info
	def process_cert(info):
		pair = {}
		for key, val in info.items():
			if isinstance(val, tuple):
				print(f'{G}[+] {C}{key}{W}')
				unpack(val, pair)
				for sub_key, sub_val in pair.items():
					print(f'\t{G}└╴{C}{sub_key}: {W}{sub_val}')
					result.update({f'{key}-{sub_key}': sub_val})
				pair.clear()
			elif isinstance(val, dict):
				print(f'{G}[+] {C}{key}{W}')
				for sub_key, sub_val in val.items():
					print(f'\t{G}└╴{C}{sub_key}: {W}{sub_val}')
					result.update({f'{key}-{sub_key}': sub_val})
			elif isinstance(val, list):
				print(f'{G}[+] {C}{key}{W}')
				for sub_val in val:
					print(f'\t{G}└╴{C}{val.index(sub_val)}: {W}{sub_val}')
					result.update({f'{key}-{val.index(sub_val)}': sub_val})
			else:
				print(f'{G}[+] {C}{key} : {W}{val}')
				result.update({key: val})
	# Als SSL aanwezig is, SSL-verbinding maken en certificaatgegevens verwerken
	if presence:
		ctx = ssl.create_default_context()
		ctx.check_hostname = False
		ctx.verify_mode = ssl.CERT_NONE
		sock = socket.socket()
		sock.settimeout(5)
		ssl_conn = ctx.wrap_socket(sock, server_hostname=hostname)
		ssl_conn.connect((hostname, sslp))
		x509_cert = ssl_conn.getpeercert(binary_form=True)
		decoded_cert = x509.load_der_x509_certificate(x509_cert, default_backend())

		# Tijdelijke dictionaries om verwerkte resultaten op te vangen, later gaan deze gebruikt worden om de resultaten weg te schrijven
		subject_dict = {}
		issuer_dict = {}
        # Functie voor het omzetten van het X.509-attribuut van het certificaat naar een dictionary die we kunnen gebruiken om weg te schrijven naar file.
		def name_to_dict(attribute):
			attr_name = attribute.oid._name
			attr_value = attribute.value
			return attr_name, attr_value
		# Functie voor verwerken van subject-attributen van het certificaat
		for attribute in decoded_cert.subject:
			name, value = name_to_dict(attribute)
			subject_dict[name] = value
		# Functie voor verwerken van issuer-attributen van certificaat
		for attribute in decoded_cert.issuer:
			name, value = name_to_dict(attribute)
			issuer_dict[name] = value
		# Maakt een dictionary die alle informatie van het certificaat bevat die wij bij bovenstaande functies hebben omgezet tot bruikbaar formaat.
		cert_dict = {
			'protocol': ssl_conn.version(),
			'cipher': ssl_conn.cipher(),
			'subject': subject_dict,
			'issuer': issuer_dict,
			'version': decoded_cert.version,
			'serialNumber': decoded_cert.serial_number,
			'notBefore': decoded_cert.not_valid_before.strftime("%b %d %H:%M:%S %Y GMT"),
			'notAfter': decoded_cert.not_valid_after.strftime("%b %d %H:%M:%S %Y GMT"),
		}
		
		# verwerken van de verschillende extensies van het certificaat
		extensions = decoded_cert.extensions
		for ext in extensions:
			if ext.oid != x509.ExtensionOID.SUBJECT_ALTERNATIVE_NAME:
				continue
			san_entries = ext.value
			subject_alt_names = []
			for entry in san_entries:
				if isinstance(entry, x509.DNSName):
					subject_alt_names.append(entry.value)
			cert_dict['subjectAltName'] = subject_alt_names
		# Verwerken van certificaat informatie dmv process_cert() functie die we vanboven hebben gedeclareerd
		process_cert(cert_dict)
	result.update({'exported': False})
	# Het resultaat wegschrijven naar het juiste bestand.
	if output:
		fname = f'{output["directory"]}/ssl.{output["format"]}'
		output['file'] = fname
		data['module-SSL Certificate Information'] = result
		export(output, data)
	# Loggen naar terminal voor meer interactie
	log_writer('[sslinfo] Completed')
