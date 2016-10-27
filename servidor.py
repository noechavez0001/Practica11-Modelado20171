#! /usr/bin/env python

import sys
from PyQt4 import QtCore, QtGui, uic
import random
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

#(0 es arriba, 1 es derecha, 2 es abajo, 3 es izquierda)

class snake():
	def __init__(self, color, iden, cuerpo):
		self.color = color
		self.iden = iden
		self.direccion = 1 #random.randint(0,3)
		self.cuerpo = cuerpo

	def snake_format(self):
		d = self.color
		i = self.iden
		dat = {"id": i, "color": d}
		return dat

	def snake_format2(self):
		c = self.cuerpo
		d = self.color
		i = self.iden
		dat = {"id": i, "camino":c, "color": d}
		return dat		

class servidorInterfaz(QtGui.QDialog):
	def __init__(self):
		QtGui.QDialog.__init__(self)
		self.timer = QtCore.QTimer()
		self.num_serp = 0
		self.serpientes = []
		self.direccion = 1
		self.snake = []
		self.proxy = 0
		self.timer.timeout.connect(lambda: self.updateTable())
		self.timer.start(250)
		# configuracion del TableWidget.
		self.ui = uic.loadUi("servidor.ui")
		self.ui.tableWidget.horizontalHeader().hide()
		self.ui.tableWidget.verticalHeader().hide()
		self.ui.tableWidget.setRowCount(20)
		self.ui.tableWidget.setColumnCount(20)
		self.ui.tableWidget.keyPressEvent = self.keyPressEventTable
		self.ui.spin_filas.valueChanged.connect(lambda: self.resizeTable())
		self.ui.spin_colum.valueChanged.connect(lambda: self.resizeTable())
		self.ui.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
		self.ui.tableWidget.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
		self.ui.spin_espera.valueChanged.connect(lambda: self.esperaAct())
		self.ui.iniciar_juego.setCheckable(True)
		self.ui.terminar_juego.setVisible(False)
		self.ui.iniciar_juego.clicked.connect(lambda: self.ini_juego())
		self.ui.terminar_juego.clicked.connect(lambda: self.ter_juego())
		# cofiguracion del servidor
		self.ui.ini_serv.clicked.connect(lambda: self.config_serv())
		# registro de funciones
		self.ui.show()

	
	#configura el servidor
	def config_serv(self):
		self.ui.ini_serv.setVisible(False)
		print "hola"
		puerto = self.ui.spin_puerto.value()
		my_ip = self.ui.edit_url.text()
		if (puerto == 0):
			puerto = 8000
		self.proxy = SimpleXMLRPCServer((str(my_ip), puerto), allow_none = True)
		self.proxy.timeout= self.ui.spin_timeout.value()
		self.timer_serv = QtCore.QTimer()
		self.timer_serv.timeout.connect(lambda: self.espera_coneccion())
		self.proxy.register_function(self.ping, 'ping')
		self.proxy.register_function(self.yo_juego, 'yo_juego')
		self.proxy.register_function(self.cambia_direccion, 'cambia_direccion')
		self.proxy.register_function(self.estado_del_juego, 'estado_del_juego')

		self.timer_serv.start(100)

	def espera_coneccion(self):
		self.proxy.handle_request()


	#cambia el tamano de las filas y renglones para ajustarlos al tamano
	def resizeTable(self):
		self.ui.tableWidget.setRowCount(self.ui.spin_filas.value())
		self.ui.tableWidget.setColumnCount(self.ui.spin_colum.value())

	#modifica el tiempo que tarda en actualizarce el juego en ms
	def esperaAct(self):
		self.timer.start(self.ui.spin_espera.value())

	def updateTable(self):
		if (self.ui.iniciar_juego.isChecked()):
			#aqui va la actualizacion de la tabla
			for sn in self.serpientes:
				if (sn.direccion==0):
					x = sn.cuerpo[0]
					a = sn.cuerpo[-1]
					c = (x[0] - 1)% self.ui.spin_filas.value()
					sn.cuerpo.insert(0,[c,x[1]])
					self.ui.tableWidget.setItem(c,x[1], QtGui.QTableWidgetItem("", 0))
					self.ui.tableWidget.item(a[0],a[1]).setBackground(QtGui.QColor(250,250,250))
					self.ui.tableWidget.item(c,x[1]).setBackground(QtGui.QColor(sn.color['r'],sn.color['g'],sn.color['b']))
					del sn.cuerpo[-1]
				elif (sn.direccion==2):
					x = sn.cuerpo[0]
					a = sn.cuerpo[-1]
					c = (x[0] + 1)% self.ui.spin_filas.value()
					sn.cuerpo.insert(0,[c,x[1]])
					self.ui.tableWidget.setItem(c,x[1], QtGui.QTableWidgetItem("", 0))
					self.ui.tableWidget.item(a[0],a[1]).setBackground(QtGui.QColor(250,250,250))
					self.ui.tableWidget.item(c,x[1]).setBackground(QtGui.QColor(sn.color['r'],sn.color['g'],sn.color['b']))
					del sn.cuerpo[-1]
				elif (sn.direccion==1):
					x = sn.cuerpo[0]
					a = sn.cuerpo[-1]
					c = (x[1] + 1)% self.ui.spin_colum.value()
					sn.cuerpo.insert(0,[x[0], c])
					self.ui.tableWidget.setItem(x[0], c, QtGui.QTableWidgetItem("", 0))
					self.ui.tableWidget.item(a[0],a[1]).setBackground(QtGui.QColor(250,250,250))
					self.ui.tableWidget.item(x[0], c).setBackground(QtGui.QColor(sn.color['r'],sn.color['g'],sn.color['b']))
					del sn.cuerpo[-1]
				elif (sn.direccion==3):
					x = sn.cuerpo[0]
					a = sn.cuerpo[-1]
					c = (x[1] - 1)% self.ui.spin_colum.value()
					sn.cuerpo.insert(0,[x[0],c])
					self.ui.tableWidget.setItem(x[0], c, QtGui.QTableWidgetItem("", 0))
					self.ui.tableWidget.item(a[0],a[1]).setBackground(QtGui.QColor(250,250,250))
					self.ui.tableWidget.item(x[0], c).setBackground(QtGui.QColor(sn.color['r'],sn.color['g'],sn.color['b']))
					del sn.cuerpo[-1]
					
				#self.serp_viva(sn)

	def quitar_serp(self,snake):
		self.serpientes.remove(snake)


	def serp_viva(self, snake):
		rest = self.serpientes
		cab = snake.cuerpo[0]
		c = snake.cuerpo[1:]
		if (cab in c ):
		# 	self.del_serpiente(sn)
		# 	self.quitar_serp(sn)
			print "muerta"
		rest.remove(snake)
		for s in rest:
			if snake.cuerpo[0] in s.cuerpo:
				# self.del_serpiente(sn)
				# self.quitar_serp(sn)
				print "muerta"
		print "viva"

	def del_serpiente(self,snake):
		for x in snake.cuerpo:
			self.ui.tableWidget.item(x[0],x[1]).setBackground(QtGui.QColor(250,250,250))

	def ini_juego(self):
		#aqui va la inicializacion de snake
		if (self.ui.iniciar_juego.isChecked()):
			self.ui.iniciar_juego.setText("Pausar Juego")
			self.ui.terminar_juego.setVisible(True)
			#self.yo_juego()
		else:
			self.ui.iniciar_juego.setText("Iniciar Juego")


	def ter_juego(self):
		#aqui va el reinicio de la tabla del juego
		if (self.ui.iniciar_juego.isChecked()):
			self.ui.ini_serv.setVisible(True)
			self.num_serp = 0
			self.serpientes = []
			self.ui.tableWidget.clear()
			self.ui.terminar_juego.setVisible(False)
			self.ui.iniciar_juego.setCheckable(False)
			self.ui.iniciar_juego.setCheckable(True)
			self.ui.iniciar_juego.setText("Iniciar Juego")
		self.ui.terminar_juego.setVisible(False)



	#enventos de presionar una tecla
	def keyPressEventTable(self, event):
		key = event.key()
		if key == QtCore.Qt.Key_Left:
			if (self.direccion != 1):
				self.direccion = 3
			print('Left Arrow Pressed')
		elif key == QtCore.Qt.Key_Up:
			if (self.direccion != 2):
				self.direccion = 0
			print('Up Arrow Pressed')
		elif key == QtCore.Qt.Key_Right:
			if (self.direccion != 3):
				self.direccion = 1
			print('Right Arrow Pressed')
		elif key == QtCore.Qt.Key_Down:
			if (self.direccion != 0):
				self.direccion = 2
			print('Down Arrow Pressed')


	def yo_juego(self):
		# agregar la posicion aleatoria de la serpiente (cuerpo)
		r = random.randint(0, 255)
		g = random.randint(0, 255)
		b = random.randint(0, 255)
		dic = {"r":r, "g":g, "b": b}
		col = self.ui.spin_colum.value()
		fil = self.ui.spin_filas.value()
		x = random.randint(0, col)
		y = random.randint(0, fil)
		cuer = []
		cuer.append([x,y])
		for z in xrange(1,6):
			x = x+1
			cuer.append([(x%col),(y%fil)])
		#cuer = [[0,5],[0,4],[0,3],[0,2],[0,1],[0,0]]
		a = self.num_serp
		self.num_serp = a +1
		new_s = snake(dic, a, cuer)
		self.serpientes.append(new_s)
		print new_s.snake_format()
		for x in cuer:
			self.ui.tableWidget.setItem(x[0], x[1], QtGui.QTableWidgetItem("", 0))
			self.ui.tableWidget.item(x[0],x[1]).setBackground(QtGui.QColor(dic["r"],dic["g"],dic["b"]))
		return new_s.snake_format()


	def ping(self):
		print "Pong!"
		return "Pong!"


	def cambia_direccion(self, iden, dire):
		for s in self.serpientes:
			if (s.iden == iden):
				if (s.direccion%2 != dire%2 ):
					s.direccion = dire

	def estado_del_juego(self):
		espera = self.ui.spin_espera.value()
		tamY = self.ui.spin_filas.value()
		tamX = self.ui.spin_colum.value()
		viboras = []
		for s in self.serpientes:
			viboras.append(s.snake_format2())
		est ={"espera":espera, "tamY":tamY, "tamX":tamX, "viboras":viboras}
		return est

app = QtGui.QApplication(sys.argv)
window = servidorInterfaz()
sys.exit(app.exec_())
