from FemFrameTool import read_fun, read_vel
from RPData import RPData
# from IntegratorST import integrate_by_st_vert, integrate_by_st_vem
import numpy as np
import pandas as pd


def calc_area_field(relative_path):
	area = read_fun(relative_path + 'field_1.fun')
	return area


def calc_height_field(relative_path):
	height = read_fun(relative_path + 'h.fun')
	return height


def calc_volume_field(relative_path):
	volume = calc_height_field(relative_path)
	return volume


def calc_sandiness_field(relative_path):
	sandiness = read_fun(relative_path + 'e.fun')
	return sandiness


def calc_perm_field(relative_path):
	perm = read_fun(relative_path + 'perm.fun')
	return perm


def calc_collector_field(relative_path):
	e = calc_sandiness_field(relative_path)
	h = calc_height_field(relative_path)
	collector = e * h
	return collector


def calc_poro_field(relative_path):
	poro = read_fun(relative_path + 'm.fun')
	return poro


def calc_poro_volume_field(relative_path):
	e = calc_sandiness_field(relative_path)
	h = calc_height_field(relative_path)
	m = calc_poro_field(relative_path)
	poro_volume = e * m * h
	return poro_volume


def calc_init_water_saturation_field(relative_path):
	s0 = read_fun(relative_path + 's0.fun')
	return s0


def calc_init_store_oil_field(relative_path):
	e = calc_sandiness_field(relative_path)
	h = calc_height_field(relative_path)
	m = calc_poro_field(relative_path)
	s0 = calc_init_water_saturation_field(relative_path)
	stock_oil = e * h * m * (1 - s0)
	return stock_oil


def calc_current_water_saturation_field(relative_path):
	s = read_fun(relative_path + 's.fun')
	return s


def calc_current_store_oil_field(relative_path):
	e = calc_sandiness_field(relative_path)
	h = calc_height_field(relative_path)
	m = calc_poro_field(relative_path)
	s = calc_current_water_saturation_field(relative_path)
	stock_oil = e * h * m * (1 - s)
	return stock_oil


def calc_velocity_field(relative_path):
	velocity = read_vel(relative_path + 'resvelo.vel')
	return velocity


def calc_press_field(relative_path):
	press = read_fun(relative_path + 'result.fun')
	return press


def calc_ph_field(relative_path):
	p = calc_press_field(relative_path)
	h = calc_height_field(relative_path)
	ph = p * h
	return ph


def calc_mh_field(relative_path):
	m = calc_poro_field(relative_path)
	h = calc_height_field(relative_path)
	mh = m * h
	return mh


def calc_conductivity_water(relative_path, mu_water):
	k = calc_perm_field(relative_path)
	h = calc_height_field(relative_path)
	return k * h / mu_water


def calc_conductivity_mixture(relative_path, mu_water, mu_oil):
	k = calc_perm_field(relative_path)
	h = calc_height_field(relative_path)
	s = calc_current_water_saturation_field(relative_path)
	k_mu = mu_water / mu_oil
	ofp = RPData(relative_path + 'relpermFVM.rp')
	return k * h * phi(s, ofp) / mu_water


def phi(s, ofp):
	n = s.__len__()
	ph = np.zeros(n, dtype = float)
	for i in range(n):
		ph[i] = ofp.fi(s[i])
	return ph


def calc_t_field(relative_path):
	t = read_fun(relative_path + 't.fun')
	return t


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


def integrate_by_st_vert_for_t(grid, color, jacob, t, tau, field):
	integral_color = np.zeros(len(color))

	for i in range(grid.Nelem):
		for j in range(grid.elem_nvert[i]):
			for k in range(len(color)):
				if tau - t[grid.elem_vert[i][j]] > 0:
					if grid.vert_color[grid.elem_vert[i][j]] == list(color[k].color):
						f = (field[grid.elem_vert[i][0]] + field[grid.elem_vert[i][1]] + field[grid.elem_vert[i][2]]) / 3
						integral_color[k] = integral_color[k] + (jacob[i] * f) / 3
				else:
					continue

	return integral_color


def integrate_by_st_vem(grid, color, jacob, field, field_u, ku):
	integral_color = np.zeros(len(color))
	u = ku * np.median(field_u)
	for i in range(grid.Nelem):
		if field_u[i] - u > 0:
			for j in range(grid.elem_nvert[i]):
				for k in range(len(color)):
					if grid.vert_color[grid.elem_vert[i][j]] == list(color[k].color):
						f = (field[grid.elem_vert[i][0]] + field[grid.elem_vert[i][1]] + field[grid.elem_vert[i][2]]) / 3
						integral_color[k] = integral_color[k] + (jacob[i] * f) / 3
		else:
			continue

	return integral_color


def calc_all_params(relative_path, grid, color, config):
	jacob = integral_jacob(grid)
	ku = config.ku
	mu_water = config.mu_water
	mu_oil = config.mu_oil
	path_rel_phase_perm = config.path_relative_phase_permeability
	output_values = []
	output_values.append(
		('Area', integrate_by_st_vert(grid, color, jacob, calc_area_field(relative_path))))
	output_values.append(
		('Volume_ST', integrate_by_st_vert(grid, color, jacob, calc_volume_field(relative_path))))
	output_values.append(
		('Volume_collector', integrate_by_st_vert(grid, color, jacob, calc_collector_field(relative_path))))
	output_values.append(
		('Volume_poro', integrate_by_st_vert(grid, color, jacob, calc_poro_volume_field(relative_path))))
	output_values.append(
		('Stock_oil', integrate_by_st_vert(grid, color, jacob, calc_init_store_oil_field(relative_path))))
	output_values.append(
		('Stock_current_oil', integrate_by_st_vert(grid, color, jacob, calc_current_store_oil_field(relative_path))))
	output_values.append(
		('Stock_6', integrate_by_st_vem(
			grid, color, jacob, calc_init_store_oil_field(relative_path), calc_velocity_field(relative_path), ku)))
	output_values.append(('p*h', integrate_by_st_vert(grid, color, jacob, calc_ph_field(relative_path))))
	output_values.append(('m*h', integrate_by_st_vert(grid, color, jacob, calc_mh_field(relative_path))))
	output_values.append(
		('m_i_water', integrate_by_st_vert(
			grid, color, jacob, calc_conductivity_water(relative_path, mu_water))/output_values[1][1]))
	output_values.append(
		('m_i', integrate_by_st_vert(
			grid, color, jacob, calc_conductivity_mixture(relative_path, mu_water, mu_oil))/output_values[1][1]))
	return output_values


def calc_t_param(relative_path, grid, color, config):

	jacob = integral_jacob(grid)

	# tau = config.tau
	# sor = config.sor # неснижаемая нефтенасыщенность

	t = calc_t_field(relative_path)
	m = calc_poro_field(relative_path)
	h = calc_height_field(relative_path)
	so = 1 - calc_current_water_saturation_field(relative_path) # (1-s) нефтенасыщенность

	tau = 2 #
	sor = 0.0001 # неснижаемая нефтенасыщенность

	# tau_arr = np.linspace(np.min(t), np.max(t), 10)

	t[t == np.inf] = np.NaN
	df = pd.DataFrame(t)
	tau_arr = np.linspace(df.min(), 0.0046, 2)
	# tau_arr = np.linspace(df.min(), df.max(), 10)

	general_field = m * h * (so - sor)

	arr_st_t_tau = []

	for i in range(tau_arr.__len__()):
		arr_st_t_tau.append(integrate_by_st_vert_for_t(grid, color, jacob, t, tau_arr[i], general_field))

	output_values = []
	for i in range(arr_st_t_tau.__len__()):
		output_values.append((str(tau_arr[i]), arr_st_t_tau[i]))

	return output_values


if __name__ == '__main__':
	raise SystemExit("CalcParamClass.py это не основное приложение!")
else:
	print('CalcParamClass.py Используется как библиотека!')
