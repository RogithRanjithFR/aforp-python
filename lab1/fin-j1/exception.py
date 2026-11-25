import logging
from pathlib import Path




def read_folder():
	logging.basicConfig(filename="events.log",
	level=logging.DEBUG,
	format="%(asctime)s - %(levelname)s - %(message)s"
	)

	try:
	 logging.info("Je suis dans le bloc try")
#	 fichier = open("no.txt", "r")
	 #nombre = int("salut")
	 folder = Path("data")
	 if not folder.is_dir():
		 logging.error("Le dossier est introuvable")
	 else:
	 	for file in folder.rglob("*.txt"):
			 taille = file.stat().st_size
			 with open(file, "r", encoding="utf-8") as f:
				 content = f.read()
			 logging.info( 
				"Fichier lu: %s, taille: %s octets",
				file.name,
				taille 
			 )
			 print ("Fichier :", file.name)
			 print ("Taille :", taille)
			 print ("Contenu :", content)
	#except FileNotFoundError: # si le try ne fonctionne pas ca affiche que le fichier n'existe pas
	except ValueError:
		#print ("Le fichier n'existe pas")
		logging.error("Le dossier est introuvable")
	finally: # ca permet de continuer meme si le try ne passe
		print ("Suite")

read_folder()



# DEBUG, INFO, WARNING, ERROR, CRITICAL
# logging.debug, logging.info, logging.warning, logging.error, logging.critical

# faire difference entre glob et rglob 
# rglob permet d acceder aux fichiers des sous-dossiers


