import numpy as np


def integral_jacob(grid):
	j = np.zeros(grid.Nelem)
	for i in range(grid.Nelem):
		x1 = grid.vert[grid.elem_vert[i][0]][0]
		y1 = grid.vert[grid.elem_vert[i][0]][1]
		x2 = grid.vert[grid.elem_vert[i][1]][0]
		y2 = grid.vert[grid.elem_vert[i][1]][1]
		x3 = grid.vert[grid.elem_vert[i][2]][0]
		y3 = grid.vert[grid.elem_vert[i][2]][1]
		j[i] = ((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) / 2
	return j


def integrate_by_st_vert(grid, color, jacob, field):
	integral_color = np.zeros(len(color))

	for i in range(grid.Nelem):
		for j in range(grid.elem_nvert[i]):
			for k in range(len(color)):
				if grid.vert_color[grid.elem_vert[i][j]] == list(color[k].color):
					f = (field[grid.elem_vert[i][0]] + field[grid.elem_vert[i][1]] + field[grid.elem_vert[i][2]]) / 3
					integral_color[k] = integral_color[k] + (jacob[i] * f) / 3

	return integral_color


def integrate_by_st_vem(grid, color, jacob, field, field_u, ku):
	integral_color = np.zeros(len(color))
	for i in range(grid.Nelem):
		if field_u[i] - ku * np.median(field_u) > 0:
			for j in range(grid.elem_nvert[i]):
				for k in range(len(color)):
					if grid.vert_color[grid.elem_vert[i][j]] == list(color[k].color):
						f = (field[grid.elem_vert[i][0]] + field[grid.elem_vert[i][1]] + field[grid.elem_vert[i][2]]) / 3
						integral_color[k] = integral_color[k] + (jacob[i] * f) / 3
		else:
			continue

	return integral_color


if __name__ == '__main__':
	raise SystemExit("IntegratorST.py это не основное приложение!")
else:
	print('IntegratorST.py Используется как библиотека!')
