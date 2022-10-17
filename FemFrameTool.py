import numpy as np
from numpy import ndarray


# Reading vert, elem_vert from .net format for grid
def read_net(path_mesh) -> tuple[ndarray, list[tuple[int, int, int]]]:
	file_mesh = open(path_mesh, 'r').readlines()
	n_nodes = int(file_mesh[0].split()[0])
	n_triangle = int(file_mesh[0].split()[1])
	vert = np.zeros((n_nodes, 2))

	for i in range(n_nodes):
		vert[i] = list(map(float, file_mesh[i + 1].split()[:2]))
	elem_vert: list[tuple[int, int, int]] = list()

	for i in range(n_triangle):
		elem_vert.append((
			int(file_mesh[i + 1 + n_nodes].split()[0]) - 1, int(file_mesh[i + 1 + n_nodes].split()[1]) - 1,
			int(file_mesh[i + 1 + n_nodes].split()[2]) - 1))
	return vert, elem_vert


# Reading field from .fun format
def read_fun(path_file):
	file_field = open(path_file, 'r').readlines()
	# field = [float(file_field[i].split()[0]) for i in range(len(file_field))]
	field = [float(1) for i in range(len(file_field))]
	return np.array(field)


# Saving grid with data field in .vtk format from .net
def save_vtk(path_save, grid, data):
	file = open(path_save, 'w')
	file.writelines('# vtk DataFile Version 3.0')
	file.write('\n')
	file.write('Grid2D')
	file.write('\n')
	file.write('ASCII')
	file.write('\n')
	file.write('DATASET UNSTRUCTURED_GRID')
	file.write('\n')
	file.write('POINTS ' + str(grid.Nvert) + ' double')
	file.write('\n')
	for i in range(grid.Nvert):
		file.write(str(grid.vert[i][0]) + ' ' + str(grid.vert[i][1]) + ' ' + '0')
		file.write('\n')
	k = 0
	for i in range(grid.Nelem):
		k = k + grid.elem_nvert[i] + 1
	file.write('CELLS ' + str(grid.Nelem) + ' ' + str(k))
	file.write('\n')
	for i in range(grid.Nelem):
		s = str(grid.elem_nvert[i])
		for j in range(grid.elem_nvert[i]):
			s = s + ' ' + str(grid.elem_vert[i][j])
		file.write(s)
		file.write('\n')
	file.write('CELL_TYPES ' + str(grid.Nelem))
	file.write('\n')
	for i in range(grid.Nelem):
		file.write('7')
		file.write('\n')
	file.write('POINT_DATA ' + str(grid.Nvert))
	file.write('\n')
	file.write('SCALARS data double 1')
	file.write('\n')
	file.write('LOOKUP_TABLE default')
	file.write('\n')
	for i in range(grid.Nvert):
		file.write(str(data[i]))
		file.write('\n')
	file.close()


if __name__ == '__main__':
	raise SystemExit('FemFrameTool.py это не основное приложение!')
else:
	print('FemFrameTool.py используется как библиотека!')
