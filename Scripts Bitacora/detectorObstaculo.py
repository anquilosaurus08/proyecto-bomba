#!/usr/bin/env python

import rospy 
from std_msgs.msg import String, Int32, Bool 
from geometry_msgs.msg import Twist 
from sensor_msgs.msg import Image 
from geometry_msgs.msg import Point
import cv2 
from cv_bridge import CvBridge 
import numpy as np 


class Template(object):
	def __init__(self, args):
		super(Template, self).__init__()
		self.args = args
		self.sub  = rospy.Subscriber('duckiebot/camera_node/image/raw', Image, self.procesar_img)
		self.pub = rospy.Publisher('duckiebot/camera_node/pov', Image, queue_size=1 )
		self.pubObs = rospy.Publisher('duckiebot/obs', Bool, queue_size = 1)
		self.min_area=2000


	def procesar_img(self, img):
		bridge = CvBridge()
		Image = bridge.imgmsg_to_cv2(img, "bgr8")
		image = Image[105:240 , 0:320] #crop de la imagen 
		
		# cambiar espacio de color
		
		image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

		# filtrar rango util
		limL = np.array([100, 75,  60])
		limU = np.array([255, 255, 255])
	
		# aplicar mascara
		mask = cv2.inRange(image_hsv, limL, limU)


		# aplicar transformaciones morfologicas
		kernel = np.ones((5,5), np.uint8)
		img_out= cv2.erode(mask, kernel, iterations= 5)
		img_out= cv2.dilate(mask, kernel, iterations= 5)
		
		image_out = cv2.bitwise_and(image, image, mask= mask)	

		# definir bloop
		_, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		
		
		for cnt in contours:
			x,y,w,h=cv2.boundingRect(cnt)
			if w*h > self.min_area:
				x2 = x+w
				y2 = y+h
				cv2.rectangle(image,(x,y),(x2,y2),(255,0,0),2)
				X = (x+x2)/2
				print(y2)
				if X in range(100,220) and y2 in range(80,300): # si el obstaculo está en el centro (ejex)
					print('True')                               # y en la parte inferior (eje y)
					self.pubObs.publish(True)
				else:
					print('False')
					self.pubObs.publish(False)
			

		# publicar imagen final
		image_out3 = cv2.cvtColor(image_out, cv2.COLOR_HSV2BGR)
		msg = bridge.cv2_to_imgmsg(image_out3, "bgr8")
		self.pub.publish(msg)
		
		
		
# nodo
def main():
	rospy.init_node('obstaculo') 
	obj = Template('args') 
	rospy.spin() 


if __name__ =='__main__':
	main()
