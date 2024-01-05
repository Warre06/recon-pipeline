#!/usr/bin/env python3

import sys

# Definieren van de gebruikte kleuren zodat ik niet altijd de ANSI color code als argument moet meegeven
R = '\033[31m'  # rood
G = '\033[32m'  # groen
C = '\033[36m'  # cyaan
W = '\033[0m'   # wit
Y = '\033[33m'  # geel

# Functie om data te exporteren naar een text bestand - output(list) & data als argumenten
def export(output, data):
    # Eerst checken of het output formaat klopt natuurlijk
    if output['format'] != 'txt':
        print(f'{R}[-] {C}Ongeldig File Format, Geldige Formats : {W}txt')
        sys.exit()

    # Naam van bestand uit output dictionary halen
    fname = output['file']
    # Data schrijven naar het bestand mbv txt_export() , zie laatste functie
    with open(fname, 'w') as outfile:
        txt_export(data, outfile)

# Deze functie zal het gemakkelijker maken om data te lezen en schrijven van complexere datastructures zoals lists & dictionaries
def txt_unpack(outfile, val):
    def write_item(item):
        # Schrijft de items van de list naar het bestand
        if isinstance(item, list):
            outfile.write(f'{item[0]}\t{item[1]}\t\t{item[2]}\n')
        else:
            outfile.write(f'{item}\n')
    # Check het type van de waarde en schrijf juist naar het bestand dmv write_item()
    if isinstance(val, list):
        for item in val:
            write_item(item)
    
    # Check het type van de waarde en schrijf juist naar het bestand dmv write_item()
    elif isinstance(val, dict):
        for sub_key, sub_val in val.items():
            # Indien al geexport, overslaan
            if sub_key == 'exported':
                continue
            # Bij nested data structures gaat dit statement recursief de text unpacken
            if isinstance(sub_val, list):
                txt_unpack(outfile, sub_val)
            else:
                outfile.write(f'{sub_key}: {sub_val}\n')

# Functie om data te exporteren naar een text bestand
def txt_export(data, outfile):
    for key, val in data.items():
        #Eerst checken ofdat de module data al niet geexporteerd is om duplicaten te vermijden
        if key.startswith('module'):
            if not val['exported']:
                txt_unpack(outfile, val)
                val['exported'] = True
        #Schrijven van de section headers voor de types
        elif key.startswith('Type'):
            outfile.write(f'\n{data[key]}\n')
            outfile.write(f'{"=" * len(data[key])}\n\n')
        else:
            # Eventueel andere key-value paren ook naar het bestand schrijven
            outfile.write(f'{key}: {val}\n')
