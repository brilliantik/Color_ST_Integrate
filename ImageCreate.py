# import sys
import os
import numpy as np
from PIL import Image, ImageDraw

path_well_size = ''
path_well_info = ''
path_bound = ''
path_sl_info = ''
path_save = ''
path_save_SL = ''
path_save_ST = ''
path_folder = ''
pixel_max = int(-999999)
well_size = int(-999999)
xy_well_info = []
x_0 = float(-999999.0)
y_0 = float(-999999.0)
norm_xy = float(-999999.0)
lx_norm = float(-999999.0)
ly_norm = float(-999999.0)
xy_bound_array = []
xy_well_ellipse_array = []
n_sl = int(-999999)
sl_info = []
ft = []
fft = []
clr = ''
img = Image.new('RGB', (1, 1))
idraw = ImageDraw.Draw(img)


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


class Coord:
	def __init__(self, st):
		self.x = float(st[0])
		self.y = float(st[1])


class SL:
	def __init__(self, st):
		# self.WellFrom = int(st[1])
		# self.WellTo = int(st[2])
		if int(st[1]) > int(st[2]):
			self.WellFrom = int(st[2])
			self.WellTo = int(st[1])
		elif int(st[1]) < int(st[2]):
			self.WellFrom = int(st[1])
			self.WellTo = int(st[2])
		self.Np = int(st[3])
		self.index = int(st[4])
		self.xy = None
		self.color = None
		self.FT = None


class Config:
	def __init__(self, pixel, path_file_names, path_file_names_for_save, path_folder_save, path_relative_folder, kku):
		self.pixel_size = pixel
		self.path_default_wells_dat = path_file_names[0]
		self.path_result_wll = path_file_names[1]
		self.path_default_con = path_file_names[2]
		self.path_SLsReg_auto_txt = path_file_names[3]
		self.path_default_net = path_file_names[4]
		self.path_result_fun = path_file_names[5]
		self.path_resvelo_vel = path_file_names[6]
		self.path_save_picture_SL = path_file_names_for_save[0]
		self.path_save_picture_ST = path_file_names_for_save[1]
		self.path_save_color_and_conn_info = path_file_names_for_save[2]
		self.path_save_st_Well_From_To_colorRGB_value = path_file_names_for_save[3]
		self.path_folder_save = path_folder_save
		self.path_relative_folder = path_relative_folder
		self.ku = kku


def normal_line(x1, y1, x2, y2):
	p = 2
	xc = (x2 + x1) / 2
	yc = (y2 + y1) / 2
	dx = x2 - x1
	dy = y2 - y1

	n1x = dy
	n1y = -dx
	n2x = -dy
	n2y = dx
	ll = np.sqrt(dx * dx + dy * dy)

	xx1 = xc + p * n1x / ll
	yy1 = yc + p * n1y / ll

	xx2 = xc + p * n2x / ll
	yy2 = yc + p * n2y / ll
	p_plus = [xx1, yy1]
	p_minus = [xx2, yy2]
	return [p_plus, p_minus]


def init_pixel_size():
	global pixel_max

	pixel_max = int(1000)


def init_path_from_cfg(cfg: Config):
	global path_well_size, path_well_info, path_bound, path_sl_info
	global path_folder, path_save, path_save_SL, path_save_ST

	# path_cfg = sys.argv[1]
	# paths = open(path_cfg, 'r').readlines()

	# path_well_size = paths[0].rstrip()
	# path_well_info = paths[1].rstrip()
	# path_bound = paths[2].rstrip()
	# path_sl_info = paths[3].rstrip()
	# path_save = paths[4].rstrip()
	path_well_size = cfg.path_default_wells_dat
	path_well_info = cfg.path_result_wll
	path_bound = cfg.path_default_con
	path_sl_info = cfg.path_SLsReg_auto_txt
	path_save = cfg.path_save_color_and_conn_info
	path_save_SL = cfg.path_save_picture_SL
	path_save_ST = cfg.path_save_picture_ST
	path_folder = cfg.path_folder_save


def init_well_info():
	global well_size, xy_well_info

	well_size_file = open(path_well_size, 'r').readlines()
	well_size = int(well_size_file[0].split()[0])

	xy_well_file = open(path_well_info, 'r').readlines()
	xy_well_info = np.zeros(well_size, dtype = Well)

	for i in range(well_size):
		well = Well(xy_well_file[i + 1].split())
		well.index = i
		xy_well_info[i] = well


def init_bound_info():
	global x_0, y_0, norm_xy, lx_norm, ly_norm, xy_bound_array

	xy_bound_file = open(path_bound, 'r').readlines()
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

	xy_bound_info = [Coord(xy_bound[i]) for i in range(bound_point_size)]

	x_bound_array = [xy_bound_info[i].x for i in range(bound_point_size)]
	y_bound_array = [xy_bound_info[i].y for i in range(bound_point_size)]

	x_max = max(x_bound_array)
	x_min = min(x_bound_array)
	y_max = max(y_bound_array)
	y_min = min(y_bound_array)

	lx = x_max - x_min
	ly = y_max - y_min

	x_0 = x_min
	y_0 = y_min

	# kof = int(lx / ly)

	norm_xy = max(lx, ly)

	x_bound_array = (np.array(x_bound_array) - x_0) * (pixel_max - 1) / norm_xy
	y_bound_array = (np.array(y_bound_array) - y_0) * (pixel_max - 1) / norm_xy

	xy_bound_array = [(int(x_bound_array[i]), int(y_bound_array[i])) for i in range(bound_point_size)]

	lx_norm = lx / norm_xy
	ly_norm = ly / norm_xy


def init_well_ellipse_info():
	global xy_well_ellipse_array

	xy_well_ellipse_array = [
		((xy_well_info[i].x - xy_well_info[i].r - x_0) * (pixel_max - 1) / norm_xy,
			(xy_well_info[i].y - xy_well_info[i].r - y_0) * (pixel_max - 1) / norm_xy,
			(xy_well_info[i].x + xy_well_info[i].r - x_0) * (pixel_max - 1) / norm_xy,
			(xy_well_info[i].y + xy_well_info[i].r - y_0) * (pixel_max - 1) / norm_xy) for i in range(well_size)]


def init_sl_info():
	global n_sl, sl_info, ft, fft

	sl_file = open(path_sl_info, 'r').readlines()
	n_sl = int(sl_file[0].split()[0])

	sl_info = np.zeros(n_sl, dtype = SL)
	num = int(0)

	for i in range(n_sl):
		sl_file_input = sl_file[1 + num + i].split()
		sl = SL(sl_file_input)
		sl.xy = [
			((float(sl_file[2 + num + i + j].split()[0]) - x_0) * (pixel_max - 1) / norm_xy,
				(float(sl_file[2 + num + i + j].split()[1]) - y_0) * (pixel_max - 1) / norm_xy) for j in range(sl.Np)]
		num += sl.Np
		fft.append((sl.WellFrom, sl.WellTo))
		sl.FT = [sl.WellFrom, sl.WellTo]
		sl_info[i] = sl

	ft = list(set(fft))

	init_nonrepeating_color()

	for i in range(n_sl):
		for j in range(len(ft)):
			if fft[i] == ft[j]:
				idraw.line(sl_info[i].xy, fill = clr[j])
				sl_info[i].color = clr[j]


def init_nonrepeating_color():
	global clr
	color256 = []
	clr = set(color256)
	# # Генерирование списка неповторяющихся цветов clr
	while len(clr) != len(ft):
		color = list(np.random.choice(range(255), size = 3))
		color256.append((color[0], color[1], color[2]))
		clr = list(set(color256))


# Можно исправить будет цветастая картинка, но не факт что хватит цветов


def create_rectangle():
	global img, idraw
	dobavok = 1
	img = Image.new('RGB', (int(lx_norm * pixel_max) + dobavok, int(ly_norm * pixel_max) + dobavok), 'white')
	idraw = ImageDraw.Draw(img)
	idraw.line(xy_bound_array, fill = 'black', width = 1)


def create_well(color):
	for i in range(well_size):
		idraw.ellipse(xy_well_ellipse_array[i], color, color)


def create_sl():
	global idraw
	for i in range(n_sl):
		for j in range(len(ft)):
			idraw.line(sl_info[i].xy, fill = sl_info[i].color)


def create_st():
	global idraw
	sl_color = (0, 0, 1)
	for i in range(n_sl):
		for j in range(len(ft)):
			idraw.line(sl_info[i].xy, fill = sl_color)

	create_well(sl_color)

	for i in range(n_sl):
		for j in range(int(sl_info[i].Np / 2) - 1, int(sl_info[i].Np / 2)):
			x1 = sl_info[i].xy[j][0]
			y1 = sl_info[i].xy[j][1]
			x2 = sl_info[i].xy[j + 1][0]
			y2 = sl_info[i].xy[j + 1][1]
			xp = normal_line(x1, y1, x2, y2)
			if list(img.getpixel((xp[0][0], xp[0][1]))) == [0, 0, 0]:
				continue
			elif list(img.getpixel((xp[0][0], xp[0][1]))) == [255, 255, 255]:
				ImageDraw.floodfill(img, (xp[0][0], xp[0][1]), sl_info[i].color, border = None, thresh = 0.5)
			elif list(img.getpixel((xp[0][0], xp[0][1]))) != list(sl_info[i].color):
				ImageDraw.floodfill(img, (xp[0][0], xp[0][1]), (0, 0, 0), border = None, thresh = 0.5)
			if list(img.getpixel((xp[1][0], xp[1][1]))) == [0, 0, 0]:
				continue
			elif list(img.getpixel((xp[1][0], xp[1][1]))) == [255, 255, 255]:
				ImageDraw.floodfill(img, (xp[1][0], xp[1][1]), sl_info[i].color, border = None, thresh = 0.5)
			elif list(img.getpixel((xp[1][0], xp[1][1]))) != list(sl_info[i].color):
				ImageDraw.floodfill(img, (xp[1][0], xp[1][1]), (0, 0, 0), border = None, thresh = 0.5)

	create_sl()
	create_well((0, 0, 0))


# font = ImageFont.truetype("Fonts/times.ttf", int(pixel_max / 20))
# for i in range(well_size):
# 	idraw.text(xy_point[i], xy_well_info[i].name, font = font, fill = 'white')  # названия скважин


def path_pic_well_conn_and_color_info(path):
	file = open(path, 'w')
	file.write('###' + '\t' + 'Wells connection(color) info' + '\t' + '###' + '\n')
	file.write('Size' + '\t' + str(len(clr) + 2) + '\n')
	file.write('#Color            #Connection' + '\n')
	file.write('{:<15}'.format('(0, 0, 0)') + '\t' + '{:<15}'.format('(-999999999, -999999999)') + '\n')
	file.write('{:<15}'.format('(255, 255, 255)') + '\t' + '{:<15}'.format('(+999999999, +999999999)') + '\n')
	for i in range(len(clr)):
		file.write('{:<15}'.format(str(clr[i])) + '\t' + '{:<15}'.format(str(ft[i])))
		file.write('\n')


def get_params(config):
	init_pixel_size()
	init_path_from_cfg(config)
	init_bound_info()
	return [pixel_max, x_0, y_0, norm_xy]


def create_image(config):
	global img, idraw
	init_pixel_size()
	init_path_from_cfg(config)
	init_well_info()
	init_bound_info()
	init_well_ellipse_info()
	init_sl_info()
	create_rectangle()
	# init_nonrepeating_color()
	create_sl()
	create_well((0, 0, 0))
	img.show()
	if not os.path.isdir(path_folder):
		os.mkdir(path_folder)
	img.save(path_save_SL)
	create_st()
	img.show()
	img.save(path_save_ST)
	path_pic_well_conn_and_color_info(path_save)


if __name__ == '__main__':
	raise SystemExit("ImageCreate.py это не основное приложение!")
else:
	print('ImageCreate.py Используется как библиотека!')
