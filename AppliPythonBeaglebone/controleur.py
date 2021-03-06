# coding: utf8
import os
import sys
sys.path.append("/root/R2D2/classes/")
import threading

"""
	On importe les classes personnalisées python
"""
import surveillance_serveur
import surveillance_serie
import traitement
import video
import LED
#import template
#import template_surveillance


class Controleur(object):
### Programme principal

	def __init__(self):
		#On prépare un fichier temporaire tant que le script est lancé
		#pid = str(os.getpid())
		#pidfile = "/tmp/controleur.pid"

		#try:
		#	#On teste si le fichier existe déja
		#	if os.path.isfile(pidfile):
		#		os.link(pidfile,"daemon_python")
		#	else:
		#		file(pidfile, 'w').write(pid)
		#		os.link(pidfile,"daemon_python")
		#except IOError as e:
		#	message = "I/O error("+str(e.errno)+"): "+str(e.strerror)
		#	print(message)
		#On effectue le vrai travail ici
		#On instancie les classes principales
		self.stop_event = threading.Event()
		self.surveillance_serveur = surveillance_serveur.Surveillance_serveur(self,self.stop_event)
		self.surveillance_serie   = surveillance_serie.Surveillance_serie(self,self.stop_event)
		self.traitement        = traitement.Traitement(self,self.stop_event)
		self.video        		  = video.Video(self.stop_event)
		self.led 				  = LED.LED(self.stop_event)

		#On met les threads en mode daemon, quand le controleur est tué, on tue tous les threads
		self.surveillance_serveur.daemon = True
		self.surveillance_serie.daemon   = True
		self.traitement.daemon        = True
		self.video.daemon        		 = True
		self.led.daemon        			 = True
		####################################
		#	Partie Template
		####################################
		#self.template			  = template.Template(self)
		#self.template_surveillance	= template_surveillance.Template_surveillance(self)

		#self.template.daemon			  = True
		#self.template_surveillance.daemon	= True

	def fonctionnement(self):
		try:
			#on démarre les threads
			self.surveillance_serveur.start()
			self.surveillance_serie.start()
			self.traitement.start()
			self.video.start()
			self.led.start()
			
			#Tant que l'arrêt du programme n'a pas été détecté (ctrl+c au clavier ou évènement système important)
			#On boucle indéfiniment juste pour rester vivant
			while not self.stop_event.isSet():
				continue

			####################################
			#	Partie Template
			####################################
			#La partie surveillance doit être lancée avant la partie traitement
			#self.template_surveillance.start()
			#self.template.start()	

				
		#On récupère toutes exceptions génantes (Ctrl-C de l'utilisateur, arrêt brutal du système)
		except KeyboardInterrupt as key:
			print("User-generated interrupt, exiting....")
			try:
				self.stop_event.set()
				self.surveillance_serveur.stop()
				self.surveillance_serie.stop()
				self.traitement.stop()
				self.video.stop()
				self.led.stop()
				
				####################################
				#	Partie Template
				####################################
				#self.template_surveillance.stop()
				#self.template.stop()	
				
				
			except OSError as e:  ## si l'opération échoue, on affiche l'erreur rencontrée (voir au niveau des permissions)
				print ("Error: %s - %s." % (e.filename,e.strerror))

		except SystemExit as exit_sys:
			print("An exception forcing the interpreter to stop has been detected, shutting down....")
			try:
				self.surveillance_serveur.stop()
				self.surveillance_serie.stop()
				self.traitement.stop()
				self.video.stop()
				self.led.stop()
				####################################
				#	Partie Template
				####################################
				#self.template_surveillance.stop()
				#self.template.stop()	
				

			except OSError as e:  ## si l'opération échoue, on affiche l'erreur rencontrée (voir au niveau des permissions)
				print ("Error: %s - %s." % (e.filename,e.strerror))
		#Quand on a fini toute l'application (si celle-ci a une fin), on efface le fichier disant que l'application est lancée (et on restaure le terminal initial)
		finally:
			try:
				#os.remove("daemon_python")
				self.surveillance_serveur.stop()
				self.surveillance_serie.stop()
				self.traitement.stop()
				self.video.stop()
				self.led.stop()
				####################################
				#	Partie Template
				####################################
				#self.template_surveillance.stop()
				#self.template.stop()	
			
			except OSError as e:  ## si l'opération échoue, on affiche l'erreur rencontrée (voir au niveau des permissions)
				print ("Error: %s - %s." % (e.filename,e.strerror))


	#Fonction chargée de mettre à jour le serveur de la classe traitement si la classe de surveillance serveur a été obligé de redémarrer le thread
	def mise_a_jour_serveur(self,serveur):
		self.traitement.serveur=serveur
	#Fonction chargée de mettre à jour la liaison série de la classe traitement si la classe de surveillance série a été obligé de redémarrer le thread
	def mise_a_jour_serie(self,serie):
		self.traitement.serie=serie

	#def mise_a_jour_template_partage(self,template_partage):
	#	self.template.template_partage=template_partage


c=Controleur()
c.fonctionnement()