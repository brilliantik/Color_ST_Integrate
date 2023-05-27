import numpy as np
import sys
import pandas as pd
import scipy.interpolate
from scipy.interpolate import Rbf, interp1d, LinearNDInterpolator, NearestNDInterpolator, griddata
import matplotlib.pyplot as plt

well_prod = []
sl_info = []


class SL:
	def __init__(self, st):
		self.ln = int(st[0])

		self.WellFrom = int(st[1])
		self.WellTo = int(st[2])

		if self.WellFrom != -1:
			self.WellFrom = self.WellFrom - 1
		if self.WellTo != -1:
			self.WellTo = self.WellTo - 1

		self.Np = int(st[3])
		self.index = int(st[4])
		self.xy = None
		self.color = None
		self.FT = None

		self.L = None
		self.p = None
		self.interior_indexes_nodes = None
		self.w = None
		self.s = None
		self.u = None
		self.k = None
		self.h = None
		self.interior_indexes_half_nodes = None


class Well:
	def __init__(self, st):
		self.index = int(st[0])
		self.name = st[1]
		self.type = st[2]
		self.x = float(st[3])
		self.y = float(st[4])
		self.r = float(st[5])
		self.press = float(st[6])
		self.q = float(st[7])


class RP:
	def __init__(self, st):
		self.relative_path = st
		self.__kmu = None
		self.__f1_interpolation = None
		self.__f2_interpolation = None
		self.__k1 = None
		self.__k2 = None
		self.__n1 = None
		self.__n2 = None
		self.__Swr = None
		self.__Sor = None
		self.initialize()

	def initialize(self):
		file = open(self.relative_path + '\\relpermFVM.rp', 'r')
		file_info = file.readlines()
		file.close()

		self.__kmu = float(file_info[0].split()[0])
		file_info.pop(0)

		# дописать через if для степенных функций пока только для табличных офп
		if int(file_info[0].split()[0]) == 1:
			self.__k1 = float(file_info[0].split()[1])
			self.__k2 = float(file_info[0].split()[2])
			self.__n1 = float(file_info[0].split()[3])
			self.__n2 = float(file_info[0].split()[4])
			self.__Swr = float(file_info[0].split()[5])
			self.__Sor = float(file_info[0].split()[6])
			self.__f1_interpolation = lambda ss: np.power((ss - self.__Swr) / (1.0 - self.__Sor - self.__Swr), self.__n1) * self.__k1
			self.__f2_interpolation = lambda ss: np.power((1.0 - (ss - self.__Swr) / (1.0 - self.__Sor - self.__Swr)), self.__n2) * self.__k2
		elif int(file_info[0].split()[0]) == 0:
			file_info.pop(0) #удаление строки со степенными зависимостями
			n_nodes = int(file_info[0].split()[0])
			file_info.pop(0)

			s = np.zeros(n_nodes, dtype = float)
			f1n = np.zeros(n_nodes, dtype = float)
			f2n = np.zeros(n_nodes, dtype = float)

			for i in range(n_nodes):
				splt = file_info[i].split()
				s[i] = splt[0]
				f1n[i] = splt[1]
				f2n[i] = splt[2]

			# self.__f1_interpolation = Rbf(s, f1n, function = 'linear', mode = "1-D")
			# self.__f2_interpolation = Rbf(s, f2n, function = 'linear', mode = "1-D")
			self.__f1_interpolation = interp1d(s, f1n)
			self.__f2_interpolation = interp1d(s, f2n)

	def f1(self, s):
		return self.__f1_interpolation(s)

	def f2(self, s):
		return self.__f2_interpolation(s)

	def kmu(self):
		return self.__kmu

	def f(self, s):
		# print('f1', self.f1(s))
		# print('f2', self.f2(s))
		# print('f', (self.f1(s)) / (self.f1(s) + self.kmu() * self.f2(s)))
		return (self.f1(s)) / (self.f1(s) + self.kmu() * self.f2(s))

	def __power_f1(self):
		pass

	def __power_f2(self):
		pass

	def test_table_rp(self):
		n = 1000
		s = np.linspace(0, 1, 1000)
		file = open(self.relative_path + 'table_rp_my.txt', 'w')
		for i in range(n):
			file.write(str(s[i]) + '\t' + str(self.f1(s[i])) + '\t' + str(self.f2(s[i])) + '\t' + str(self.f(s[i])) + '\n')
		file.close()


class M_S_FIELD:
	def __init__(self, st):
		self.relative_path = st
		self.__m_interpolation = None
		self.__s_interpolation = None
		self.initialize()

	def initialize(self):
		file = open(self.relative_path + '\\default.net', 'r')
		file_info = file.readlines()
		file.close()

		n_nodes = int(file_info[0].split()[0])
		file_info.pop(0)

		x_nodes = np.zeros(n_nodes, dtype = float)
		y_nodes = np.zeros(n_nodes, dtype = float)
		for i in range(n_nodes):
			f = file_info[i].split()
			x_nodes[i] = f[0]
			y_nodes[i] = f[1]

		file_m = open(self.relative_path + '\\m.fun', 'r')
		file_info_m = file_m.readlines()
		file_m.close()

		file_s = open(self.relative_path + '\\s.fun', 'r')
		file_info_s = file_s.readlines()
		file_s.close()

		mn = np.zeros(n_nodes, dtype = float)
		sn = np.zeros(n_nodes, dtype = float)

		for i in range(n_nodes):
			mn[i] = file_info_m[i].split()[0]
			sn[i] = file_info_s[i].split()[0]

		# self.__m_interpolation = Rbf(x_nodes, y_nodes, mn, function = 'linear', smooth = 0.0)
		# self.__s_interpolation = Rbf(x_nodes, y_nodes, sn, function = 'linear', smooth = 0.0)
		self.__m_interpolation = LinearNDInterpolator((x_nodes, y_nodes), mn)
		self.__s_interpolation = LinearNDInterpolator((x_nodes, y_nodes), sn)

	def m(self, x, y):
		return self.__m_interpolation(x, y)

	def s(self, x, y):
		return self.__s_interpolation(x, y)

	def test_field(self):
		n = 1000
		x = np.linspace(0, 1, n)
		y = 2.0 * x
		m = self.__m_interpolation(x, y)
		s = self.__s_interpolation(x, y)
		file = open(self.relative_path + 'test_txt_epure.txt', 'w')
		for i in range(n):
			file.write(str(x[i]) + '\t' + str(m[i]) + '\t' + str(s[i]) + '\n')
		file.close()


def read_file_prod_wells(relative_path):
	file = open(relative_path + '\\Color_ST_analiz//well_prod_info.txt', 'r')
	file_info = file.readlines()
	file.close()
	file_info.pop(0)

	n_prod_well = file_info.__len__()
	w = np.zeros(n_prod_well, dtype = Well)

	for i in range(n_prod_well):
		w[i] = Well(file_info[i].split('\t'))

	global well_prod
	well_prod = w


def read_file_SLs(relative_path):
	file = open(relative_path + '\\Result\\SL_ST_PROD\\SLsReg_auto.txt', 'r')
	file_info = file.readlines()
	file.close()

	n_sl = int(file_info[0].split()[0])
	file_info.pop(0)

	sl_info_ = np.zeros(n_sl, dtype = SL)
	num = int(0)
	for i in range(n_sl):
		file_arr = file_info[i + num].split()
		sl = SL(file_arr)
		sl.xy = [
			(float(file_info[1 + num + i + j].split()[0]), float(file_info[1 + num + i + j].split()[1])) for j in range(sl.Np)]
		num += sl.Np

		sl.FT = [sl.WellFrom, sl.WellTo]

		file_dat = open(relative_path + '\\Result\\SL_ST_PROD\\SLR_auto_' + str(sl.ln) + '.dat')
		file_info_dat = file_dat.readlines()
		file_dat.close()

		file_info_dat.pop(0)
		n_nodes = int(file_info_dat[0].split()[0]) + 1
		n_half_nodes = n_nodes + 1

		file_info_dat.pop(0)

		file_info_l_p_i = file_info_dat[:n_nodes]
		file_info_w_s_u_k_h_i = file_info_dat[n_nodes:]

		l_p_i = pd.DataFrame(np.array([file_info_l_p_i[j].split() for j in range(n_nodes)]))
		w_s_u_k_h_i = pd.DataFrame(np.array([file_info_w_s_u_k_h_i[j].split() for j in range(n_half_nodes)]))

		sl.L = l_p_i[0].values.astype('float64')
		sl.p = l_p_i[1].values.astype('float64')
		sl.interior_indexes_nodes = l_p_i[2].values.astype('int64')

		sl.w = w_s_u_k_h_i[0].values.astype('float64')
		sl.s = w_s_u_k_h_i[1].values.astype('float64')
		sl.u = w_s_u_k_h_i[2].values.astype('float64')
		sl.k = w_s_u_k_h_i[3].values.astype('float64')
		sl.h = w_s_u_k_h_i[4].values.astype('float64')
		sl.interior_indexes_half_nodes = w_s_u_k_h_i[5].values.astype('str')

		sl_info_[i] = sl

	global sl_info
	sl_info = sl_info_


def create_map(relative_path):
	t_all = []
	x_all = []
	y_all = []

	rel_perm = RP(relative_path)
	ms_field = M_S_FIELD(relative_path)
	rel_perm.test_table_rp()
	ms_field.test_field()

	for i in range(sl_info.__len__()):
		sl = sl_info[i]
		d = [sl.L[i + 1] - sl.L[i] for i in range(sl.Np - 1)]
		d = np.flip(d)
		u = sl.u
		u = np.delete(u, -1)
		u = np.delete(u, 0)
		u = np.flip(u)
		# x = [(sl.xy[j][0] + sl.xy[j + 1][0]) / 2.0 for j in range(sl.Np - 1)]
		# y = [(sl.xy[j][1] + sl.xy[j + 1][1]) / 2.0 for j in range(sl.Np - 1)]
		x = [sl.xy[j + 1][0] for j in range(sl.Np - 1)]
		y = [sl.xy[j + 1][1] for j in range(sl.Np - 1)]
		x = np.flip(x)
		y = np.flip(y)
		n = u.__len__()

		t = np.zeros(n, dtype = float)

		m = ms_field.m(x, y)
		s = ms_field.s(x, y)

		# проверка на отрицательные значения и значения меньшк единицы
		# for j in range(n):
		# 	if m[j] > 1.0:
		# 		m[j] = 1.0 - np.finfo(float).eps
		# 	elif m[j] < 0.0:
		# 		m[j] = np.finfo(float).eps
		# 	if s[j] > 1.0:
		# 		s[j] = 1.0 - np.finfo(float).eps
		# 	elif s[j] < 0.0:
		# 		s[j] = np.finfo(float).eps

		summ = 0.0
		for j in range(n):
			summ += (m[j] * (1.0 - s[j]) * d[j]) / (u[j] * (1.0 - rel_perm.f(s[j])))
			t[j] = summ
		t_all.append(t)
		x_all.append(x)
		y_all.append(y)
	t_all = np.concatenate(t_all)
	x_all = np.concatenate(x_all)
	y_all = np.concatenate(y_all)

	interpolate_2d(x_all, y_all, t_all, relative_path)
	pass


def interpolate_2d(x, y, v, relative_path):
	file = open(relative_path + '\\default.net', 'r')
	file_info = file.readlines()
	file.close()

	n_nodes = int(file_info[0].split()[0])
	file_info.pop(0)

	x_nodes = np.zeros(n_nodes, dtype = float)
	y_nodes = np.zeros(n_nodes, dtype = float)
	for i in range(n_nodes):
		f = file_info[i].split()
		x_nodes[i] = f[0]
		y_nodes[i] = f[1]

	# f = Rbf(x, y, v, function = 'linear')
	f = LinearNDInterpolator((x, y), v)
	strs = ''
	v_new = f(x_nodes, y_nodes)

	for i in range(n_nodes):
		strs += str(v_new[i]) + '\t' + str(i + 1) + '\n'

	file_save = open(relative_path + '\\t.fun', 'w')
	file_save.write(strs)
	file_save.close()


def create_t_map(relative_path):
	read_file_prod_wells(relative_path)
	read_file_SLs(relative_path)
	create_map(relative_path)
	pass


if __name__ == '__main__':
	create_t_map(sys.argv[1])
	print('TMap.py Используется как исполняемый файл!')
else:
	print('TMap.py Используется как библиотека!')
