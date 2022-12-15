
# -*- coding: utf-8 -*-
"""
@author: AranaCorp
"""
import rospy 
from std_msgs.msg import String, Int32 
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image 
from geometry_msgs.msg import Point
import cv2
from cv_bridge import CvBridge # importar convertidor de formato de imagenes
import numpy as np 
  
#El detector de lineas detecta las concentraciones de blanco y a partir esto entrega la posición en x mapeada
#de [0,320] --> [-16,16]


class Template(object):
	def __init__(self, args):
		super(Template, self).__init__()
		self.args = args

		#sub
		self.sub  = rospy.Subscriber('duckiebot/camera_node/image/raw', Image, self.procesar_img)

		#pub
		self.pub = rospy.Publisher('duckiebot/camera_node/line', Image, queue_size=1 )
		self.pab = rospy.Publisher('duckiebot/moveInt', Int32, queue_size = 1)

		#variables
		self.move = 'none'

	def procesar_img(self, img):
		bridge = CvBridge()
		image = bridge.imgmsg_to_cv2(img, 'bgr8') #320x240

		#Imagen en escala de gris
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		
		#Filtro 
		blur = cv2.GaussianBlur(gray,(5,5),0)
		
		omeroSinson, threshA = cv2.threshold(blur, 180, 255, cv2.THRESH_BINARY_INV)
		
		#Bloops
		thresh = abs(255-threshA)
		_, contours, _ = cv2.findContours(thresh.copy(), 1, cv2.CHAIN_APPROX_NONE)
		
		
		if len(contours) == 0:     #Si no detecta lineas
			self.move = 0
			print('sicosis')
		
		if len(contours) >0:        #Al detectar concentraciones de blanco
			c = max(contours, key=cv2.contourArea)
			M = cv2.moments(c)
			
			#Rectas de concentaciones de blanco en cada eje
			cx= int(M['m10']/M['m00']) 
			cy= int(M['m01']/M['m00'])
			
			cv2.line(image,(cx,0),(cx,720),(255,0,0),1)
			cv2.line(image,(0,cy),(1280,cy),(255,0,0),1)

			#Dibuja contornos
			cv2.drawContours(image, contours, -1, (0,255,0), 1) 

			#Posición en x mapeada			
			self.move = (cx - 160)/10

	        msg = bridge.cv2_to_imgmsg(image, "bgr8")

		self.pub.publish(msg)
		self.pab.publish(self.move)

#nodo
def main():
	rospy.init_node('cv2') 
	obj = Template('args') 
	rospy.spin() 


if __name__ =='__main__':
	main()
	 