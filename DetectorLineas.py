
# -*- coding: utf-8 -*-
"""
@author: AranaCorp
"""
import rospy #importar ros para python
from std_msgs.msg import String, Int32 # importar mensajes de ROS tipo String y tipo Int32
from geometry_msgs.msg import Twist # importar mensajes de ROS tipo geometry / Twist
from sensor_msgs.msg import Image # importar mensajes de ROS tipo Image
from geometry_msgs.msg import Point
import cv2
from cv_bridge import CvBridge # importar convertidor de formato de imagenes
import numpy as np 
  
class Template(object):
	def __init__(self, args):
		super(Template, self).__init__()
		self.args = args
		self.sub  = rospy.Subscriber('duckiebot/camera_node/image/raw', Image, self.procesar_img)
		self.pub = rospy.Publisher('duckiebot/camera_node/line', Image, queue_size=1 )
		self.pab = rospy.Publisher('duckiebot/move', String, queue_size = 1)
		self.move = 'none'

	def procesar_img(self, img):
		d = 40
		
		bridge = CvBridge()
		
		image = bridge.imgmsg_to_cv2(img, 'bgr8') #320x240

		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		
		blur = cv2.GaussianBlur(gray,(5,5),0)
		
		omeroSinson, threshA = cv2.threshold(blur, 180, 255, cv2.THRESH_BINARY_INV)
		
		thresh = abs(255-threshA)
		_, contours, _ = cv2.findContours(thresh.copy(), 1, cv2.CHAIN_APPROX_NONE)
		
		if len(contours) == 0:
			self.move = 'nada'
			print('sicosis')
		
		if len(contours) >0:
			c = max(contours, key=cv2.contourArea)
			M = cv2.moments(c)
			
			cx= int(M['m10']/M['m00'])
			cy= int(M['m01']/M['m00'])
			
			cv2.line(image,(cx,0),(cx,720),(255,0,0),1)
			cv2.line(image,(0,cy),(1280,cy),(255,0,0),1)
			
			cv2.drawContours(image, contours, -1, (0,255,0), 1)
			
			print(cx == None)
			if cx <= 160-d:
				self.move = 'left'
				
			elif cx >160-d and cx <160+d:
				self.move = 'fwd'
				
			elif cx >= 160+d:
				self.move = 'right'
			else:
			        print('error')
			
			print(self.move)

	        msg = bridge.cv2_to_imgmsg(image, "bgr8")
	        #cv2.imwrite('linesDetected.jpg', img) 
		self.pub.publish(msg)
		self.pab.publish(self.move)

def main():
	rospy.init_node('cv2') #creacion y registro del nodo!

	obj = Template('args') # Crea un objeto del tipo Template, cuya definicion se encuentra arriba

	#objeto.publicar() #llama al metodo publicar del objeto obj de tipo Template

	rospy.spin() #funcion de ROS que evita que el programa termine -  se debe usar en  Subscribers


if __name__ =='__main__':
	main()
	 #if = theta and theta <= np.pi/18) or 	DI(np.pi/2-np.pi/180*10 <= theta and theta <= np.pi/2+np.pi/180*10): 
