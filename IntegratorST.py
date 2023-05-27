import numpy as np
from PIL import Image

from grid import *
from GeneralClassAndFunction import Config
from GeneralClassAndFunction import read_xml_config
from CalcParam import calc_all_params, calc_t_param
import time


grid = None
fieldd = None
pic = None
clr = []
cfg: Config


class Color:
	def __init__(self, st):
		c = st[0].rstrip().replace('(', '').replace(')', '').replace(' ', '').split(',')
		r = int(c[0])
		g = int(c[1])
		b = int(c[2])
		self.color = (r, g, b)
		d = st[1].rstrip().replace('(', '').replace(')', '').replace(' ', '').split(',')
		f = int(d[0])
		t = int(d[1])
		self.ft = (f, t)


def read_pic(path):
	global pic
	pic = Image.open(path)


def read_ppwcac_info(path):
	global clr

	ppwcfc_file = open(path, 'r').readlines()
	ncolor = int(ppwcfc_file[1].split()[1])
	clr = np.zeros(ncolor, dtype = Color)
	for i in range(ncolor):
		clr[i] = Color(ppwcfc_file[i + 3].split('\t'))


def read_mesh(path):
	global grid
	grid = gu_build_from_net(path)


def init_color_to_vert():
	assigment_color_to_vert(grid, pic, cfg)


def output_file_param(data, path):
	file = open(path, 'w')
	file.write(
		'###' + '\t' + 'st_number' + '\t' + 'Well_From' + '\t' + 'Well_To' + '\t' + 'Color_R' + '\t' + 'Color_G' + '\t'
		+ 'Color_B' + '\t' + 'value' + '\n')
	file.write('##Size' + '\t' + str(len(data)) + '\n')
	for i in range(len(data)):
		file.write(
			'{:<}'.format(str(i)) + '\t' + '{:<}'.format(str(clr[i].ft[0])) + '\t' + '{:<}'.format((str(clr[i].ft[1])))
			+ '\t' + '{:<}'.format(str(clr[i].color[0])) + '\t' + '{:<}'.format(str(clr[i].color[1])) + '\t'
			+ '{:<}'.format(str(clr[i].color[2])) + '\t' + '{:<}'.format(str(data[i])) + '\n')
	file.close()


def output_file_params(data, path):
	n_data = len(data)
	file = open(path, 'w')
	strs = '###' + 'st_number' + '\t' + 'Well_From' + '\t' + 'Well_To' + '\t' + 'Color_R' + '\t' + 'Color_G' + '\t' \
			 + 'Color_B'
	for i in range(n_data):
		strs = strs + '\t' + data[i][0]
	strs = strs + '\n'
	len_data_i = len(data[0][1])
	strs = strs + '##Size' + '\t' + str(len_data_i) + '\n'
	for i in range(len_data_i):
		strs = strs + '{:<}'.format(str(i)) + '\t' + '{:<}'.format(str(clr[i].ft[0])) + '\t' + '{:<}'.format((str(clr[i].ft[1]))) \
					+ '\t' + '{:<}'.format(str(clr[i].color[0])) + '\t' + '{:<}'.format(str(clr[i].color[1])) + '\t' \
					+ '{:<}'.format(str(clr[i].color[2]))
		for j in range(n_data):
			strs = strs + '\t' + '{:<}'.format(str(data[j][1][i]))
		strs = strs + '\n'
	file.write(strs)
	file.close()


def integrate_st(config):
	global cfg
	start_time = time.time()
	cfg = config
	read_pic(cfg.path_save_picture_ST)
	read_ppwcac_info(cfg.path_save_color_and_conn_info)
	read_mesh(cfg.path_default_net)
	init_color_to_vert()
	output_infos = calc_all_params(cfg.path_relative_folder, grid, clr, cfg)
	output_file_params(output_infos, cfg.path_save_st_Well_From_To_colorRGB_value)
	output_infos_t = calc_t_param(cfg.path_relative_folder, grid, clr, cfg)
	output_file_params(output_infos_t, cfg.path_folder_save + 't_table.txt')
	print('integrate_st() function time : ', time.time() - start_time)


if __name__ == '__main__':
	# raise SystemExit("IntegratorST.py это не основное приложение!")
	print('IntegratorST.py Используется как исполняемый файл!')
	integrate_st(read_xml_config())
else:
	print('IntegratorST.py Используется как библиотека!')
