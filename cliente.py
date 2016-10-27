#! /usr/bin/env python

import sys
from PyQt4 import QtCore, QtGui, uic
import xmlrpclib
import time 

class ImageDialog(QtGui.QDialog):
	def __init__(self):
		QtGui.QDialog.__init__(self)
		#configuracion 
		self.proxy= 0
		self.serpiente = None
		self.estado = None
		self.direccion = 1
		self.col = 0
		self.row = 0
		self.viboras= []
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(lambda: self.updateTable())
		# Set up the user interface from Designer.
		self.ui = uic.loadUi("cliente.ui")
		self.ui.tableWidget.horizontalHeader().hide()
		self.ui.tableWidget.verticalHeader().hide()
		self.ui.tableWidget.keyPressEvent = self.keyPressEventTable
		self.ui.tableWidget.setRowCount(5)
		self.ui.tableWidget.setColumnCount(5)
		self.ui.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
		self.ui.tableWidget.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
		self.ui.edit_id.setReadOnly(True)
		self.ui.edit_color.setReadOnly(True)
		#configuracion de botones
		self.ui.ping.clicked.connect(lambda: self.ping_cliente())
		self.ui.participar.clicked.connect(lambda: self.participar_juego())
		self.ui.show()

	#funcion del boton ping
	def ping_cliente(self):
		url = self.ui.edit_url.text()
		puerto = self.ui.spin_puerto.value()
		direccion = 'http://'+str(url)+':'+str(puerto)+'/' 
		self.proxy = xmlrpclib.ServerProxy(direccion)
		self.ui.ping.setText('Pinging...')
		try:
			self.ui.ping.setText(self.proxy.ping())
		except Exception, e:
			self.ui.ping.setText('No pong :(')

	def participar_juego(self):
		url = self.ui.edit_url.text()
		puerto = self.ui.spin_puerto.value()
		direccion = 'http://'+str(url)+':'+str(puerto)+'/' 
		self.proxy = xmlrpclib.ServerProxy(direccion)
		color = '{250,250,250}'
		idn = '0'
		try:
			self.serpiente = self.proxy.yo_juego()
			self.estado = self.proxy.estado_del_juego()
		except Exception, e:
			print 'no hay conexion'
		self.col = self.estado['tamX']
		self.row = self.estado['tamY']
		self.ui.tableWidget.setRowCount(self.row)
		self.ui.tableWidget.setColumnCount(self.col)
		self.ui.edit_id.setText(str(self.serpiente['id']))
		self.ui.edit_color.setText(str(self.serpiente['color']))
		self.ui.participar.setVisible(False)
		self.timer.start(self.estado['espera'])
		self.viboras = self.estado['viboras']

	#enventos de presionar una tecla
	def keyPressEventTable(self, event):
		key = event.key()
		if key == QtCore.Qt.Key_Left:
			if (self.direccion != 1):
				self.direccion = 3
				self.proxy.cambia_direccion(self.serpiente['id'],self.direccion)
			print('Left Arrow Pressed')
		elif key == QtCore.Qt.Key_Up:
			if (self.direccion != 2):
				self.direccion = 0
				self.proxy.cambia_direccion(self.serpiente['id'],self.direccion)
			print('Up Arrow Pressed')
		elif key == QtCore.Qt.Key_Right:
			if (self.direccion != 3):
				self.direccion = 1
				self.proxy.cambia_direccion(self.serpiente['id'],self.direccion)
			print('Right Arrow Pressed')
		elif key == QtCore.Qt.Key_Down:
			if (self.direccion != 0):
				self.direccion = 2
				self.proxy.cambia_direccion(self.serpiente['id'],self.direccion)
			print('Down Arrow Pressed')


 	def updateTable(self):
		self.ui.tableWidget.clear()
 		self.estado = self.proxy.estado_del_juego()
 		if (self.estado['tamY']!= self.row or self.estado['tamX']!= self.col):
 			self.row = self.estado['tamY']
 			self.col = self.estado['tamX']
	 		self.ui.tableWidget.setRowCount(self.row)
			self.ui.tableWidget.setColumnCount(self.col)
 		self.viboras = self.estado['viboras']
 		for s in self.viboras:
 			cuerpo = s['camino']
 			color = s['color']
 			for c in cuerpo:
 				self.ui.tableWidget.setItem(c[0],c[1], QtGui.QTableWidgetItem("", 0))
				self.ui.tableWidget.item(c[0],c[1]).setBackground(QtGui.QColor(color['r'],color['g'],color['b']))


app = QtGui.QApplication(sys.argv)
window = ImageDialog()
sys.exit(app.exec_())