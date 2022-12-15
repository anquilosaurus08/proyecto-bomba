import cv2
import numpy as np
import collections as collections
import math
import rospy 
from std_msgs.msg import Int32MultiArray
from std_msgs.msg import MultiArrayDimension
from time import sleep 
import copy


# envia y calcula la posición inicial, actualiza la matriz cuando ve un obstáculo y la envia

class Template(object):
	def __init__(self, args):
		self.args = args
		super(Template, self).__init__()
		#sub
		self.sub = rospy.Subscriber('duckiebot/Grid2',Int32MultiArray , self.callback)
		self.suv = rospy.Subscriber('duckiebot/cambio', Int32MultiArray, self.callback2)

		#pub
		self.pub = rospy.Publisher('duckiebot/Grid',Int32MultiArray, queue_size = 2)
		self.puc = rospy.Publisher('duckiebot/posicioninicial',Int32MultiArray, queue_size = 2)

		#variables
		self.map = np.array(None)
		self.posi = [None,None,None] 
		self.estacion = []
	
	# obtiene los movimientos realizados por el duckiebot y calcula una nueva posición inicial y matriz
	def callback2(self,msg): 
		sleep(5) #evitar desfases

		# saca la información del msg (lista de pasos)
		layout = msg.layout.dim
		data   = msg.data
		width  = layout[1].size
		height = layout[0].size

		# pasa la lista a array de numpy
		cambio = np.array(data).reshape(width,height)

		# calcula la posción final 
		def pfinal(pinicial,pasos):
		    def orientacion(oi,odt):
			if odt == 90: oi=(oi-1)%4 + 1            # gira derecha
			if odt == -90: oi = (oi+2)%4 +1			 # gira izquierda
			if abs(odt) == 180: oi = (oi +1)%4 +1    # gira 180 grados
			return oi 

		    pfi = pinicial

		    for i in pasos:	
			if i == 1:
			    if pfi[2] == 1: pfi[0] -=1   #norte
			    if pfi[2] ==2: pfi[1] +=1    #este
			    if pfi[2] ==3: pfi[0] +=1    #sur
			    if pfi[2] == 4: pfi[1] -=1   #oeste

			else:    
			    pfi[2] = orientacion(pfi[2],i) # cambia la orientación

		    return pfi

		# nueva posición    
		pnueva = pfinal(self.posi, cambio) 
	
		# cambia la posición cuando es distinta de incial 
		if pnueva != self.posi:
			self.posi = pnueva

		# localización del obstáculo
		obstaculo = copy.copy(pnueva)

		if obstaculo[2] == 1: obstaculo[0] -=1   #norte
		if obstaculo[2] == 2: obstaculo[1] +=1   #este
		if obstaculo[2] == 3: obstaculo[0] +=1   #sur
		if obstaculo[2] == 4: obstaculo[1] -=1   #oeste
		
		# coloca un 0 donde se encuentra el obstáculo
		filaobs, columobs, _ = obstaculo
		self.map[filaobs][columobs] = 0
		

		#Nueva matriz	
		h = self.map.shape[0]
		w = self.map.shape[1]
		out = np.zeros((self.map.shape), dtype=int)

        # pasar la matriz de un array de numpy a una lista [[1,1],[2,2]] -> [1,1,2,2]
		out2 = []
		for i in range(w):
			for j in range(h):
				out2.append(int(self.map[i,j]))
				out[i,j] = int(self.map[i,j])
			
		
		# enviar la lista con la nueva matriz
		mat = Int32MultiArray()
		mat.layout.dim.append(MultiArrayDimension())
		mat.layout.dim.append(MultiArrayDimension())
		mat.layout.dim[1].label = "width"
		mat.layout.dim[0].label = 'height'
		mat.layout.dim[0].size = h
		mat.layout.dim[1].size = w
		mat.layout.dim[0].stride = w*h
		mat.layout.dim[1].stride = w
		mat.layout.data_offset = 0
		mat.data = out2
		print(mat, "mat")
		
		# enviar la lista con la nueva posición incial
		Mat = Int32MultiArray()
		Mat.layout.dim.append(MultiArrayDimension())
		Mat.layout.dim.append(MultiArrayDimension())
		Mat.layout.dim[1].label = "width"
		Mat.layout.dim[0].label = 'height'
		Mat.layout.dim[0].size = 1
		Mat.layout.dim[1].size = 2
		Mat.layout.dim[0].stride = 2
		Mat.layout.dim[1].stride = 2
		Mat.layout.data_offset = 0
		Mat.data = self.posi
		print(Mat, "Mat")
		
		self.pub.publish(mat)
		self.puc.publish(Mat)
		
		
	#Envia posición de la estación de bomberos
	def callback(self, msg):
		# obtiene la información del msg (posición inicial)
		layout = msg.layout.dim
		data   = msg.data
		width  = layout[1].size
		height = layout[0].size
		
		# define la ubicación de la estación de bomberos
		if self.posi == [None,None,None]:
			self.posi = [4,4,1]
			self.estacion = copy.copy(self.posi)
		self.posi = [4,4,1]
		
		# pasa la lista a array de numpy
		self.map = np.array(data).reshape(width,height)
		
		# pasar la matriz a una lista [[1,1],[2,2]] -> [1,1,2,2]
		h = self.map.shape[0]
		w = self.map.shape[1]
		out = np.zeros((self.map.shape), dtype=int)

		#rellena la lista
		out2 = []
		for i in range(w):
			for j in range(h):
				out2.append(int(self.map[i,j]))
				out[i,j] = int(self.map[i,j])
			
		
		
		# publicar la lista con la matriz
		mat = Int32MultiArray()
		mat.layout.dim.append(MultiArrayDimension())
		mat.layout.dim.append(MultiArrayDimension())
		mat.layout.dim[1].label = "width"
		mat.layout.dim[0].label = 'height'
		mat.layout.dim[0].size = h
		mat.layout.dim[1].size = w
		mat.layout.dim[0].stride = w*h
		mat.layout.dim[1].stride = w
		mat.layout.data_offset = 0
		mat.data = out2
	
		# publicar la lista de con la posición inicial
		Mat = Int32MultiArray()
		Mat.layout.dim.append(MultiArrayDimension())
		Mat.layout.dim.append(MultiArrayDimension())
		Mat.layout.dim[1].label = "width"
		Mat.layout.dim[0].label = 'height'
		Mat.layout.dim[0].size = 1
		Mat.layout.dim[1].size = 2
		Mat.layout.dim[0].stride = 2
		Mat.layout.dim[1].stride = 2
		Mat.layout.data_offset = 0
		Mat.data = self.posi
	
		
		self.pub.publish(mat)
		self.puc.publish(Mat)

		

def main():
	rospy.init_node('grid2') 
	obj = Template('args') 
	rospy.spin() 


if __name__ =='__main__':
	main()

