import cv2
import numpy as np
import collections as collections
import math
import rospy 
from std_msgs.msg import Int32MultiArray 
from std_msgs.msg import MultiArrayDimension


# encuentra el camino más corto entre dos puntos de una matriz de nxn

class Template(object):
	def __init__(self, args):
		self.args = args
		super(Template, self).__init__()

		# sub
		self.sub = rospy.Subscriber('duckiebot/Grid',Int32MultiArray , self.callback)
		self.suv = rospy.Subscriber('duckiebot/posicioninicial',Int32MultiArray , self.callback2)

		# pub
		self.pub = rospy.Publisher('duckiebot/Step',Int32MultiArray , queue_size = 1 )

		# variables internas
		self.posi = [None,None,None]

	# obtiene la posición inicial	
	def callback2(self, msg):
		layout = msg.layout.dim
		data   = msg.data
		width  = layout[1].size
		height = layout[0].size
		
		self.posi = np.array(data)
	

	# calcula la ruta más corta entre dos ptos pertenecientes a la matriz	
	def callback(self, msg):
		
		# obtiene la matriz en forma de lista
		layout = msg.layout.dim
		data   = msg.data
		width  = layout[1].size
		height = layout[0].size
		
		# convierte la lista en una matriz
		grid = np.array(data).reshape(width,height)


		wall = 0                    #Valor de las paredes
		
		srow, scol, so = self.posi  #Fila, Columna y Orientacion inicial (1=Norte, 2=Este, 3=Sur, 4=Oeste)
		
		grow, gcol, gv = [0, 0, 99]  #Fila, Columna y Verificador final

		grid[grow, gcol] = gv        # coloca el destino en la amtriz

		width, height = grid.shape
		
		# calcula el camino más corto
		def bfs(grid, start):
		    queue = collections.deque([[start]])
		    seen = set([start])
		    while queue:
			path = queue.popleft()
			x, y = path[-1]
			if grid[y][x] == gv:
			    return path
			for x2, y2 in ((x+1,y), (x-1,y), (x,y+1), (x,y-1)):
			    if 0 <= x2 < width and 0 <= y2 < height and grid[y2][x2] != wall and (x2, y2) not in seen:
				queue.append(path + [(x2, y2)])
				seen.add((x2, y2))

		# lista de pasos 		
		steps = bfs(grid, (scol, srow))
	
		instructions = []
		for i in range(len(steps)-1):
		    xi = steps[i][0]
		    yi = steps[i][1]
		    xf = steps[i+1][0]
		    yf = steps[i+1][1]
		    if xi < xf: instructions.append(2)
		    if xi > xf: instructions.append(4)
		    if yi < yf: instructions.append(3)
		    if yi > yf: instructions.append(1)
		    
		# movimientos
		Instructions = [so]+instructions
		
		motion = []
		
		#rellenar la lista de pasos 
		for i in range(len(Instructions)-1):
		    ini = Instructions[i]
		    fin = Instructions[i+1]
		    if abs(ini - fin) == 3:
			motion.append(((ini - fin)//3)*90)       # 1 = adelante
			motion.append(1)                         # 90 = girar derecha
		    if ini != fin and abs(ini - fin) != 3:   # -90 = girar izq
			motion.append((fin - ini)*90)
			motion.append(1)
		    if ini == fin: motion.append(1)
		

		# publicar la lista de pasos
		h = 1
		w = len(motion)
		    
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
		mat.data = motion   
	    
		self.pub.publish(mat)

# nodo 
def main():
	rospy.init_node('steps') 
	obj = Template('args') 
	rospy.spin() 

if __name__ =='__main__':
	main()

