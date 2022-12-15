import cv2 
import numpy as np
import collections as collections
import math
import rospy 
from std_msgs.msg import Int32MultiArray 
from std_msgs.msg import MultiArrayDimension, String, Int32, Bool
from duckietown_msgs.msg import Twist2DStamped
from time import sleep
import sys

# ejecuta los movimientos de la lista de pasos, se corrige con el seguidor de lineas, se detiene al ver un obstaculo
# y envia la lista de pasos que realizó

class Template(object):
	def __init__(self, args):
		self.args = args
		super(Template, self).__init__()

		# sub
		self.sub = rospy.Subscriber('duckiebot/Step',Int32MultiArray , self.callback)
		self.suv = rospy.Subscriber('duckiebot/moveInt', Int32, self.callback2)
		self.suw = rospy.Subscriber('duckiebot/obs', Bool, self.callback3)

		# pub
		self.pub = rospy.Publisher('duckiebot/wheels_driver_node/car_cmd',Twist2DStamped, queue_size = 1 )
		self.pud = rospy.Publisher('duckiebot/cambio', Int32MultiArray, queue_size = 1)

		# variables internas
		self.move = Twist2DStamped()
		self.obs = Bool()
		self.matar = True
		self.zero = Twist2DStamped()
		self.zero.omega = 0
		self.zero.v = 0
		self.corr = 0
		self.lista = []
    
	# recibe un msg si le dice si hay o no un obstáculo
	def callback3(self,msg):
		self.obs.data = msg.data
		if self.obs.data == True:
			self.move.v = 0
			self.pub.publish(self.move)

	# recibe donde está la concentración de blanco
	def callback2(self, msg):
		self.corr = msg.data
		
	# realiza la secuencia de pasos
	def callback(self, msg):
		#obtiene una lista con la secuencia de pasos
		layout = msg.layout.dim
		data   = msg.data
		width  = layout[0].size
		height = layout[1].size
		
		# convierte la lista en un array
		Grid = np.array(data).reshape(width,height)
		
		# saca la lista 
		grid = Grid[0]
				
        # manda las instrucciones a las ruedas

		# Ejecuta la lista de pasos si no ve ningún obstáculo o si lo ve pero va a girar
		if (self.matar == True) or (self.matar != True and grid.tolist()[0] != 1) :
	        
			contador = 0
			grid = grid.tolist()

			#procesa la lista de pasos
			while len(grid) != 0:
				i = grid.pop(0)
				
				if self.obs.data and i == 1: grid = []    # vacia la lista de pasos al ver una obstaculo
				else:                                     # ejecuta la lista
					if i == 1: #avanza
						
						t = 0.3
						fwd = False
						
						#correciones
						while fwd == False and self.obs.data != True:
							# está centrado -> avanza
							if abs(self.corr) <= 4:   
								self.move.omega = 0
								self.move.v = 20
								self.pub.publish(self.move)
								self.lista.append(1)
								fwd = True
							
                            # está corrido a la levemente a los costados
							elif abs(self.corr) >  3 and abs(self.corr) < 13:
								self.move.omega = 2*(self.corr/16) + 7*(self.corr/abs(self.corr))
								self.move.v = 0
								self.pub.publish(self.move)
								sleep(t)
								self.pub.publish(self.zero)
								sleep(t) 

                            # está muy corrido a los costados
							elif abs(self.corr) >= 13:
								self.move.omega = 9*(self.corr/abs(self.corr))
								self.move.v = 0 
								self.pub.publish(self.move)
								sleep(t)
								self.pub.publish(self.zero)
								sleep(t)

							# no detecta lineas
							else: 
								self.move.omega = 0
								self.move.v = 0
								self.pub.publish(self.move)
								sleep(t)
								
                        
						sleep(1/3+0.430)
						self.move.v = 0 #se detiene una vez que termina de avanzar
						self.pub.publish(self.zero)
						sleep(1)

					#girando
					if i != 1 :
						cw = abs(i)/i      #direccion de giro
						mag = abs(i/90)    #n° de giros 90-> 1  180->2

						if mag >= 0:       #gira a la derecha
							self.move.v = 0
							self.move.omega = 11.5*cw
							self.pub.publish(self.move)
							self.lista.append(i)
							sleep(0.12+0.5*mag)
							self.move.omega = 0
							self.pub.publish(self.zero)
							sleep(1)		

						if mag < 0:        #gira a la izquierda
							self.move.v = 0
							self.move.omega = 9*cw
							self.pub.publish(self.move)
							self.lista.append(i)
							sleep(0.08+0.5*mag)
							self.move.omega = 0
							self.pub.publish(self.zero)
							sleep(1)		
							
		    # los sleeps son para asegurarnos que se publique bien y no desfasen			
					
			self.move.v = 0
			self.move.omega = 0
			self.pub.publish(self.move)
				 
			# terminada la lista de pasos se detiene
			self.matar = False
		
		# cuando ve un obstaculo envia una lista de pasos que realizó hasta el momento
		if self.matar != True:
			
			mat = Int32MultiArray()
			mat.layout.dim.append(MultiArrayDimension())
			mat.layout.dim.append(MultiArrayDimension())
			mat.layout.dim[1].label = "width"
			mat.layout.dim[0].label = 'height'
			mat.layout.dim[0].size = 1
			mat.layout.dim[1].size = len(self.lista)
			mat.layout.dim[0].stride = len(self.lista)
			mat.layout.dim[1].stride = len(self.lista)
			mat.layout.data_offset = 0
			mat.data = self.lista  
			self.pud.publish(mat) #lista de pasos reales
			self.lista = []
			sleep(2)
			self.matar = True #vuelve a funcionar
			
		
		
			
		

def main():
	rospy.init_node('pathfollowing') 
	obj = Template('args') 
	rospy.spin() 


if __name__ =='__main__':
	main()

