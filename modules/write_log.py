import logging
import settings


def log_writer(message):
    # Configuratie van het logging systeem
    logging.basicConfig(
        filename=settings.log_file_path, # Bestand waar logs in worden opgeslagen
        encoding='utf-8',
        level=logging.INFO, # Logniveau instellen, kan heel uitgebreid zijn of beperkt
        format='[%(asctime)s] : %(message)s', # Logformaat met tijd
        datefmt='%m/%d/%Y %I:%M:%S %p' # Datum & Tijd toevoegen
    )
    logging.info(message)
