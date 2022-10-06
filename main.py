import xml.etree.ElementTree as ET
from PIL import Image
from grid import *
from FemFrameTool import read_fun
from IntegratorST import integral_jacob, integrate_by_st
from ImageCreate import create_image
import sys


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


class Config:
	def __init__(self, pixel, path_file_names, path_file_names_for_save, path_folder):
		self.pixel_size = pixel
		self.path_default_wells_dat = path_file_names[0]
		self.path_result_wll = path_file_names[1]
		self.path_default_con = path_file_names[2]
		self.path_SLsReg_auto_txt = path_file_names[3]
		self.path_default_net = path_file_names[4]
		self.path_result_fun = path_file_names[5]
		self.path_save_picture_SL = path_file_names_for_save[0]
		self.path_save_picture_ST = path_file_names_for_save[1]
		self.path_save_color_and_conn_info = path_file_names_for_save[2]
		self.path_save_st_Well_From_To_colorRGB_value = path_file_names_for_save[3]
		self.path_folder_save = path_folder


grid = None
field = None
jac = None
pic = None
clr = []
cfg: Config


def read_xml_config():
	global cfg
	path_xml_file = sys.argv[1]
	tree = ET.parse(path_xml_file)
	root = tree.getroot()
	pixel_size = int(root.find('pixel_size').text)
	relative_path = root.find('relative_path').text
	relative_path_for_save = root.find('relative_path_for_save').text
	folder_name = root.find('folder_name_for_save').text
	path_save = relative_path_for_save + folder_name + '\\'
	path_file_names = [relative_path + file_name.text for file_name in root.find('file_names').findall('file_name')]
	path_file_names_for_save = [
		path_save + file_names_for_save.text for file_names_for_save in
		root.find('file_names_for_save').findall('file_name_save')]
	cfg = Config(pixel_size, path_file_names, path_file_names_for_save, path_save)


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


def read_field(path):
	global field
	field = read_fun(path)


def init_j():
	global jac

	jac = integral_jacob(grid, field)


def init_color_to_vert():
	assigment_color_to_vert(grid, pic, cfg)


def output_file(data, path):
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


def main():
	read_xml_config()
	create_image(cfg)
	read_pic(cfg.path_save_picture_ST)
	read_ppwcac_info(cfg.path_save_color_and_conn_info)
	read_mesh(cfg.path_default_net)
	read_field(cfg.path_result_fun)
	init_j()
	init_color_to_vert()
	output_info = integrate_by_st(grid, clr, jac)
	output_file(output_info, cfg.path_save_st_Well_From_To_colorRGB_value)


if __name__ == '__main__':
	main()
else:
	raise SystemExit('Это не библиотека!')
