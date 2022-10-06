import xml.etree.ElementTree as ET
from PIL import Image
from grid import *
from FemFrameTool import read_fun
from IntegratorST import integral_jacob, integrate_by_st
from ImageCreate import create_image

grid = None
field = None
jac = None
pic = None
clr = []


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
	def __init__(self, pixel, path_file_names, path_file_names_for_save):
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


def read_xml_config():
	path_xml_file = 'info.xml'
	tree = ET.parse(path_xml_file)
	root = tree.getroot()
	pixel_size = int(root.find('pixel_size').text)
	relative_path = root.find('relative_path').text
	relative_path_for_save = root.find('relative_path_for_save').text
	folder_name = root.find('folder_name_for_save').text
	path_save = relative_path_for_save + folder_name + '\\'
	path_file_names = [relative_path + file_name.text for file_name in root.find('file_names').findall('file_name')]
	path_file_names_for_save = [path_save + file_names_for_save.text for file_names_for_save in root.find('file_names_for_save').findall('file_name_save')]
	return Config(pixel_size, path_file_names, path_file_names_for_save)


def read_pic():
	global pic

	path_pic = r'C:\Stud\ST_LT\Color_ST_Integrate\Result\Pic_ST.png'
	pic = Image.open(path_pic)


def read_ppwcac_info():
	global clr

	path_ppwcfc_file = r'C:\Stud\ST_LT\Color_ST_Integrate\Result\ppwcac_info.txt'
	ppwcfc_file = open(path_ppwcfc_file, 'r').readlines()
	ncolor = int(ppwcfc_file[3].split()[1])
	clr = np.zeros(ncolor, dtype = Color)
	for i in range(ncolor):
		clr[i] = Color(ppwcfc_file[i + 5].split('\t'))


def read_mesh():
	global grid

	path_mesh = r'C:\Stud\ST_LT\SL_ST_EXAMPLE\Ex2\default.net'
	grid = gu_build_from_net(path_mesh)


def read_field():
	global field

	path_field = r'C:\Stud\ST_LT\SL_ST_EXAMPLE\Ex2\result.fun'
	field = read_fun(path_field)


def init_j():
	global jac

	jac = integral_jacob(grid, field)


def init_color_to_vert():
	assigment_color_to_vert(grid, pic)


def output_file(data):
	file = open(r'C:\Stud\ST_LT\Color_ST_Integrate\Result\st_ft_color_value.txt', 'w')
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
	cfg = read_xml_config()
	create_image()
	read_pic()
	read_ppwcac_info()
	read_mesh()
	read_field()
	init_j()
	init_color_to_vert()
	output_info = integrate_by_st(grid, clr, jac)
	output_file(output_info)


if __name__ == '__main__':
	main()
else:
	raise SystemExit('Это не библиотека!')
