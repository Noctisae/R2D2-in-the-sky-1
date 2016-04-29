#/usr/bin/env python
# -*-coding:Utf-8 -*
import socket
import threading
import Queue
from time import sleep
class Reception_Serveur(threading.Thread):
	"""
	Classe englobant le socket serveur permettant la transmission d'infos du robot au smartphone, et inversement
		Contient:
			Socket serveur réceptionnant les informations du smartphone
			Socket client transmettant les informations vers le smartphone

		Prend en entrée:
			queue_input : Une queue d'items input, les informations que le controleur envoie à la classe Serveur : le retour des commandes de la liaison série
			queue_output : Une queue d'items output, les informations que le serveur transmet au controleur : les commandes demandées par smartphone
			
	"""
	def __init__(self,serveur, queue_output):
		threading.Thread.__init__(self)
		self.output = queue_output
		self.serveur = serveur
		#variable écoutant l'arrêt du thread par le controleur
		self.stoprequest = threading.Event()
		
		### Socket serveur
		self.socket_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		#Adresse et Port à définir suivant les possibilités de l'application Android, ici port 12800
		self.socket_serveur.bind(('', 12800))

		#Une connexion maximale possible au socket, comme ca pas de problème avec plusieurs applications, un seul téléphone peut communiquer avec l'appli
		self.socket_serveur.listen(1)

		#On accepte la connexion
		#Attention, la méthode accept bloque le programme tant qu'aucun client ne s'est présenté
		self.connexion_avec_client, self.infos_connexion = self.socket_serveur.accept()
		print(self.infos_connexion)
		self.serveur.infos_connexion = self.infos_connexion
		

	def run(self):
		sleep(1)
		self.socket_serveur.settimeout(0.05)
		attente = False
		compteur_attente = 0
		#Tant que le controleur ne demande pas au thread de s'arreter
		while not self.stoprequest.isSet():
			print("Le compteur_attente vaut : "+str(compteur_attente))
			if(compteur_attente > 10000):
				attente = True
				self.connexion_avec_client.close()
			if(attente):
				self.connexion_avec_client, self.infos_connexion = self.socket_serveur.accept()
				self.serveur.infos_connexion = self.infos_connexion
				print(self.infos_connexion)
				attente = False
			try:
				#On attend les informations du smartphone
				#La connexion Android envoie deux caractères au début de la connexion
				#Il faut donc les réceptionner afin qu'ils ne perturbent pas le reste des messages
				print("Dans la classe Reception serveur : J'attends les informations du smartphone")
				chaine = ""
				continuer = True
				enregistrer = False
				while continuer:
					msg = self.connexion_avec_client.recv(1)
					if(msg == "{"):
						enregistrer = True
					elif(msg == "}"):
						continuer = False
					if(enregistrer):
						chaine += msg
				print("Dans la classe Reception serveur : "+chaine)
				self.output.appendleft((chaine))
				compteur_attente = 0
			except socket.timeout:
				compteur_attente += 1
				continue

	def stop(self):
		self.stoprequest.set()