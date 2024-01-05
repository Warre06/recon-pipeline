# Automated Recon Pipeline - Eindopdracht Ethical Hacking

Dit is mijn eindopdracht voor het vak Ethical Hacking, in het logboek zult u zien dat ik voorbije 3 maanden intensief bezig ben geweest met een pipeline op basis van luigi tasks maar na schrijven van al deze tasks lukte het me niet om ze te koppelen tot een pipeline, iets wat duidelijk vaker voorkomt heb ik gelezen. Daarom heb ik gekozen voor asyncio om toch een zo snel mogelijke pipeline te creeeren, deels met code die ik heb kunnen recupereren van mijn luigi project agz ik hier al heel veel code van had. 

## Features

Mijn recon-pipeline geeft gedetailleerde informatie zoals:

* Header Information

* Whois

* SSL Certificate Information

* Port Scan
    * Fast Port Scan
    * Top 1000 ports

* Export
    * Formats
        * txt

## Installation & Configuration
### Linux

```bash
git clone https://github.com/Warre06/recon-pipeline.git
cd recon-pipeline
pip3 install -r requirements.txt
```
## Usage

```bash
usage: recon_pipeline.py [-h] [--headers] [--sslinfo] [--whois] [--ps] [--full] [-pt PT] [-T T] [-r] [-s] [-sp SP] [-e E] [-o O] url

Automated Reconnaisance Pipeline - Eindopdracht Ethical Hacking | v1.0.0

positional arguments:
  url         Target URL

options:
  -h, --help  show this help message and exit
  --headers   Header Information
  --sslinfo   SSL Certificate Information
  --whois     Whois Lookup
  --ps        Fast Port Scan
  --full      Full Recon Scan

Extra Opties:
  -pt PT      Aantal threads voor port scan [ Default : 50 ]
  -T T        Request Timeout [ Default : 30.0 ]
  -r          Allow Redirect [ Default : False ]
  -s          Toggle SSL Verification [ Default : True ]
  -sp SP      Specify SSL Port [ Default : 443 ]
  -e E        File Extensions [ Example : txt, xml, php ]
  -o O        Export Format [ Default : txt ]
```