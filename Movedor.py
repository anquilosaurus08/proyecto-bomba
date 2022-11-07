import rospy #importar ros para python
from std_msgs.msg import String, Int32 # importar mensajes de ROS tipo String y tipo Int32
from sensor_msgs.msg import Joy # importar mensajes de ROS tipo String y tipo Int32
from geometry_msgs.msg import Twist # importar mensajes de ROS tipo geometry / Twist
from duckietown_msgs.msg import Twist2DStamped
from geometry_msgs.msg import Point


class Template(object):
	def __init__(self, args):
		super(Template, self).__init__()
		self.args = args
		self.sub  = rospy.Subscriber('duckiebot/move', String, self.callback)
		self.pub = rospy.Publisher('duckiebot/wheels_driver_node/car_cmd',Twist2DStamped, queue_size = 1 )
		self.move = Twist2DStamped()

	#def publicar(self):
	

	def callback(self,msg):
		datos = msg
		Datos = str(datos)
		if Datos == 'data: "fwd"':
			self.move.omega = 0
			self.move.v = 1
		elif Datos == 'data: "left"':
			self.move.omega = -8
			self.move.v = 0.3
			
		elif Datos == 'data: "right"':
			self.move.omega = 8
			self.move.v = 0.3
		else: 
			self.move.omega = 0
			self.move.v = 0
			print('x_X')
		
		print(self.move)
		self.pub.publish(self.move)


	

	
def main():
	rospy.init_node('move') #creacion y registro del nodo!

	obj = Template('args') # Crea un objeto del tipo Template, cuya definicion se encuentra arriba

#objeto.publicar() #RD:IRDAllama al metodo publicar del objeto obj de tipo Template

	rospy.spin() #funcion de ROS que evita que el programa termine -  se debe usar en  Subscribers


if __name__ =='__main__':
	main()

