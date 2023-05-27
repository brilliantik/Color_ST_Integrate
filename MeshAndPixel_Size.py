import numpy as np
import math

import pandas as pd

well_all = []
well_inj = []
well_prod = []
well_nowork = []
lx = -999999999.0
ly = -999999999.0
x_max = -999999999.0
x_min = -999999999.0
y_max = -999999999.0
y_min = -999999999.0
xy_bound_info = []
xy_center_bound_edges = []
l_mean = -999999999.0


class Well:
	def __init__(self, st):
		self.name = st[0]
		self.mode = st[1]
		self.r = float(st[2])
		self.x = float(st[3])
		self.y = float(st[4])
		self.Node = int(st[5])
		self.press = float(st[6])
		self.rate = float(st[7])
		self.index = None
		if self.rate < 0:
			self.type = 'producer'
		elif self.rate > 0:
			self.type = 'injection'
		elif self.rate == 0:
			self.type = 'no_working'


class Coord:
	def __init__(self, st):
		self.x = float(st[0])
		self.y = float(st[1])


def read_result_wll(path):
	file = open(path + '\\result.wll', 'r')
	file_info = file.readlines()
	file.close()
	file_info.pop(0)
	well_size = file_info.__len__()

	xy_well_info = np.zeros(well_size, dtype = Well)

	for i in range(well_size):
		well = Well(file_info[i].split())
		well.index = i
		xy_well_info[i] = well

	global well_inj, well_prod, well_nowork, well_all

	for i in range(well_size):
		if xy_well_info[i].type == 'injection':
			well_inj.append(xy_well_info[i])
		elif xy_well_info[i].type == 'producer':
			well_prod.append(xy_well_info[i])
		elif xy_well_info[i].type == 'no_working':
			well_nowork.append(xy_well_info[i])
		well_all.append(xy_well_info[i])


def read_con(path):
	global lx, ly, x_max, x_min, y_max, y_min

	xy_bound_file = open(path + '\\finemesh.con', 'r').readlines()
	index_size = 0

	for i in range(len(xy_bound_file)):
		if xy_bound_file[i].rstrip() == '$4 Что считать нулём':
			index_size = i
			break

	bound_point_size = index_size - 2

	# xy_bound = []
	# for i in range(bound_point_size):
	# 	xy_bound.append(xy_bound_file[i + 2].split())

	xy_bound = np.zeros(bound_point_size, dtype = list)
	for i in range(bound_point_size):
		xy_bound[i] = xy_bound_file[i + 2].split()

	global xy_bound_info

	xy_bound_info = [Coord(xy_bound[i]) for i in range(bound_point_size)]

	x_bound_array = [xy_bound_info[i].x for i in range(bound_point_size)]
	y_bound_array = [xy_bound_info[i].y for i in range(bound_point_size)]

	x_max = max(x_bound_array)
	x_min = min(x_bound_array)
	y_max = max(y_bound_array)
	y_min = min(y_bound_array)

	lx = x_max - x_min
	ly = y_max - y_min


def init_center_bound_edges():
	global xy_center_bound_edges

	for i in range(xy_bound_info.__len__() - 1):
		x = (xy_bound_info[i].x + xy_bound_info[i + 1].x)/2
		y = (xy_bound_info[i].y + xy_bound_info[i + 1].y)/2
		xy_center_bound_edges.append(Coord((x, y)))


def init_l():
	n_well_all = well_all.__len__()
	n_well_inj = well_inj.__len__()
	n_well_prod = well_prod.__len__()
	n_con = xy_center_bound_edges.__len__()

	m_well_inj_l = np.zeros(n_well_inj)
	for i in range(n_well_inj):
		m_well_inj_l[i] = min([math.hypot(well_inj[i].x - well_prod[j].x, well_inj[i].y - well_prod[j].y) for j in range(n_well_prod)])

	m_well_prod_l = np.zeros(n_well_prod)
	for i in range(n_well_prod):
		m_well_prod_l[i] = min([math.hypot(well_prod[i].x - well_inj[j].x, well_prod[i].y - well_inj[j].y) for j in range(n_well_inj)])

	m_con_l = np.zeros(n_con)
	for i in range(n_con):
		m_con_l[i] = min([math.hypot(xy_center_bound_edges[i].x - well_all[j].x, xy_center_bound_edges[i].y - well_all[j].y) for j in range(n_well_all)])

	av_well_l = (m_well_inj_l.mean() + m_well_prod_l.mean()) / 2
	m_con_l_new = [i for i in m_con_l if i < av_well_l]

	global l_mean

	l_mean = np.array(list(m_well_inj_l) + list(m_well_prod_l) + list(m_con_l_new)).mean()


def init_nelem_npixel():
	n_pixeil_on_l = 300
	n_x_pixel = int(lx/l_mean * n_pixeil_on_l)
	n_y_pixel = int(ly/l_mean * n_pixeil_on_l)

	fem_elem_between_nearest_well = 20

	n = int(2 * fem_elem_between_nearest_well * fem_elem_between_nearest_well * (lx/l_mean) * (ly/l_mean))
	print('Кол-во пикселей по большей оси:', max(n_x_pixel, n_y_pixel))
	print('Размерность сетки в КЭ:', n)


def give_nelem_and_npixel(path):
	read_result_wll(path)
	read_con(path)
	init_center_bound_edges()
	init_l()
	init_nelem_npixel()
	pass


if __name__ == '__main__':
	print('MeshAndPixel_Size.py Используется как исполняемый файл!')
else:
	print('MeshAndPixel_Size.py Используется как библиотека!')
