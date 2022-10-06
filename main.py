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
