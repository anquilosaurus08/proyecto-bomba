import cv2
import numpy as np
import random
import math 
import time #permite usa la funcion sleep
import rospy 
from sensor_msgs.msg import Image 
from std_msgs.msg import Int32MultiArray 
from std_msgs.msg import MultiArrayDimension

# toma una imagen y la convierte en una matriz cuadrada

class Template(object):
	def __init__(self, args):
		super(Template, self).__init__()
		
		# sub
		self.sub = rospy.Subscriber('duckiebot/camera_node/image/raw', Image, self.publicar )

		# pub
		self.pub = rospy.Publisher('duckiebot/Grid2',Int32MultiArray , queue_size = 10 )


		
	def publicar(self, msg):
		
		# stipple search
		def stipple(mask, iters):
		    # resolución
		    height, width = mask.shape[:2];
		    # chequeos aleatorios
		    counts = [];
		    for a in range(iters):
				# obtención de posiciones aleatorias
				copy = np.copy(mask);
				x = random.randint(0, width-1);
				y = random.randint(0, height-1);

				# rellena
				cv2.floodFill(copy, None, (x, y), 100);

				# count
				count = np.count_nonzero(copy == 100);
				counts.append(count);
			print(counts, "counts")
		    return counts;
		    
		loop = True
		while loop == True:

			# cargar imagen
			gray = cv2.imread("tiles2.jpg", cv2.IMREAD_GRAYSCALE);

			# mask
			mask = cv2.inRange(gray, 100, 255);
			height, width = mask.shape[:2];

			# checks
			sizes = stipple(mask, 10);

			# saca el tamaño más común o el más pequeño
			size = max(set(sizes), key=sizes.count);

			# tamaño de uno de los lados de la matriz
			side = math.sqrt(size);

			# dimensiones de la matriz
			grid_width = int(round(width / side));
			grid_height = int(round(height / side));

			# recalculate size to nearest rounded whole number
			side = int(width / grid_width);

			# construccion de la matriz
			grid = [];
			start_index = int(side / 2.0);
			for y in range(start_index, height, side):
			    row = [];
			    for x in range(start_index, width, side):
				row.append(mask[y,x] == 255);
			    grid.append(row[:]);

			# matriz como un array de numpy 	
			Grid = np.array(grid)

			# pasar el array de numpy a una lista [[1,1],[2,2]] -> [1,1,2,2]
			h = Grid.shape[0]     #saca dimensiones
			w = Grid.shape[1]
			out = np.zeros((Grid.shape), dtype=int)

			out2 = []         
			for i in range(w):      #rellena la lista
				for j in range(h):
					out2.append(int(Grid[i,j]))
					out[i,j] = int(Grid[i,j])

			# evitar errores de aleatoriedad al generar la matriz
			if out.shape != (1,1): loop = False
			else: loop = True

			# enviar un lista
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
			
			
		self.pub.publish(mat)		
		time.sleep(999999999)  # funciona una vez

# nodo
def main():
	rospy.init_node('grid') 
	obj = Template('args') 
	rospy.spin() 


if __name__ =='__main__':
	main()
