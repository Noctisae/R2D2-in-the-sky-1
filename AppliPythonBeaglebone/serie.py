#/usr/bin/env python
# -*-coding:Utf-8 -*
import Adafruit_BBIO.UART as UART
import serial
import curses

import threading

import os
import sys

import constants

###   Préparation du programme

class Serie(Thread):
	"""
	Classe regroupant l'application générale du robot
		Contient:
			Une connexion série UART
			L'algorythmique de surveillance et la transmission des commandes aux moteurs
	"""
	self.MODE = 0

	def __init__(self, queue_input, queue_output, sel_uart =1):
		if(sel_uart not in [1,2,4,5]):
				return "Erreur : la liaison série spécifiée n'est pas valide"
		threading.Thread.__init__(self)
		self.input = queue_input
		self.output = queue_output
		self.stoprequest = threading.Event()
		### Liaison série
		#On choisir la liaison série 1 par défaut, la liaison série spécifiée sinon
		UART.setup("UART"+str(sel_uart))

		#Ouverture de la liaison série
		self.ser = serial.Serial(port = "/dev/ttyO"+str(sel_uart), baudrate=38400,bytesize=8, stopbits=1,timeout=None)
		self.ser.close()

	def run(self):
		while not self.stoprequest.isSet():
			try:
				infos = self.input.get(True, 0.05)
				resultM = 0
				if(MODE != infos[0]):
					resultM = ordre_moteurs(constants.SET_MODE)
				MODE = infos[0]
				resultG = ordre_moteurs(constants.SET_SPEED_1,infos[1])
				resultD = ordre_moteurs(constants.SET_SPEED_2,infos[2])
				resultA = ordre_moteurs(constants.SET_ACCELERATION,infos[3])
				self.output.put((resultM, resultG, resultD, resultA))
			except Queue.Empty:
				continue

	#Fonction chargée d'effectuer l'envoi sur la liaison série des commandes moteurs
	def ordre_moteurs(self,commande,parameter):
		#On vérifie que la commande et son paramètre correspondent à des valeurs autorisées
		AUTORISATION = True
		if(commande in constants.LIST_SET):
			AUTORISATION = verif_commande_SETSPEED(parameter)
		elif(commande == constants.SET_ACCELERATION):
			AUTORISATION = verif_commande_SETACCELERATION(parameter)
		elif(commande == constants.SET_MODE):
			AUTORISATION = verif_commande_SETMODE(parameter)

		if(AUTORISATION):
			self.ser.open()
			if self.ser.isOpen():
				self.ser.write(constants.CMD+commande+parameter)
				#Si la commande est une commande GET, on lit la réponse et on la retourne
				if (commande in constants.LIST_GET):
						return self.ser.read()
			else:
				#Si la liaison série n'est pas ouverte, on renvoie l'erreur 1000
				return 1000
			self.ser.close()
		return 0
	
	def get_serial(self):
		return self.ser.name


	def verif_commande_SETSPEED(self,parameter):
		if(self.MODE % 2):
			return (parameter >= 0) & (parameter <= 255)
		else :
			return (parameter >= -128) & (parameter <= 127)

	def verif_commande_SETACCELERATION(self,parameter):
		return (parameter >= 1) & (parameter <= 10)

	def verif_commande_SETMODE(self,parameter):
		return (parameter >= 0) & (parameter <= 3)