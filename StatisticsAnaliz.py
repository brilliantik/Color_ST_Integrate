import numpy as np
import pandas as pd
import time
import sys

dict_wells = {}
st_value_info = []
dic_st_value = []
df: pd.DataFrame
well_inj = []
well_prod = []
well_nowork = []
slr_info = []
sl_info = []
df_sl_info = []
st_ft_info: pd.DataFrame


class SL:
	def __init__(self):
		self.ln = None
		self.index = None
		self.L = None
		self.p = None
		self.interior_indexes_nodes = None
		self.w = None
		self.s = None
		self.u = None
		self.k = None
		self.h = None
		self.interior_indexes_half_nodes = None


class SLR:
	def __init__(self, st, index):
		self.ln = int(st[0])
		if int(st[1]) != -1:
			self.wFrom = int(st[1]) - 1
		elif int(st[1]) == -1:
			self.wFrom = int(st[1])
		if int(st[2]) != -1:
			self.wTo = int(st[2]) - 1
		elif int(st[2]) == -1:
			self.wTo = int(st[2])
		self.q = float(st[3]) / (24.0 * 60.0 * 60.0)
		self.phi = float(st[4])
		self.psi = float(st[5])
		self.index = index


def read_st_value_info(path):
	global dic_st_value, df, st_ft_info
	file = open(path, 'r')
	file_info = file.readlines()
	file.close()
	file_0_str = file_info[0].split()
	file_info.pop(0)
	file_info.pop(0)
	data = {}

	for i in range(len(file_0_str)):
		if i < 6:
			data[file_0_str[i]] = [int(file_info[j].split()[i]) for j in range(len(file_info))]
		else:
			data[file_0_str[i]] = [float(file_info[j].split()[i]) for j in range(len(file_info))]

	dic_st_value = data
	df = pd.DataFrame(data)


def read_well_info(path):
	global dict_wells, well_prod, well_inj, well_nowork
	file = open(path, 'r')
	file_info = file.readlines()
	file.close()
	file_info.pop(0)
	d = {}
	for s in file_info:
		ss = s.split()
		d[int(ss[0])] = ss[2]
	dict_wells = d
	for dw in dict_wells:
		if dict_wells[dw] == 'injection':
			well_inj.append(dw)
		elif dict_wells[dw] == 'producer':
			well_prod.append(dw)
		elif dict_wells[dw] == 'no_working':
			well_nowork.append(dw)


def interaction_inj_with_prod_well_mu():
	n_well_inj = len(well_inj)
	r_variable = np.zeros(n_well_inj)
	ddf = df[df['Well_From'] > -1]
	for i in range(n_well_inj):
		r_variable[i] = r_variable[i] \
						+ ddf[ddf['Well_From'] == well_inj[i]].__len__() \
						+ ddf[ddf['Well_To'] == well_inj[i]].__len__()
	return pd.DataFrame(r_variable).describe()[0]


# return r_variable.mean()


def read_slr_info(path):
	file = open(path, 'r')
	file_info = file.readlines()
	file.close()

	global slr_info
	n_slr = file_info.__len__()
	slr_info = [SLR(file_info[i].split(), i) for i in range(n_slr)]
	pass


def read_sl_info(path):
	sls = []
	global slr_info
	for i in range(slr_info.__len__()):
		file = open(path + '\\SLR_auto_' + str(slr_info[i].ln) + '.dat')
		ln = int(file.readline().split()[3])
		n_nodes = int(file.readline().split()[0]) + 1
		n_half_nodes = n_nodes + 1
		file_info = file.readlines()
		file.close()

		file_info_l_p_i = file_info[:n_nodes]
		file_info_w_s_u_k_h_i = file_info[n_nodes:]

		l_p_i = pd.DataFrame(np.array([file_info_l_p_i[j].split() for j in range(n_nodes)]))
		w_s_u_k_h_i = pd.DataFrame(np.array([file_info_w_s_u_k_h_i[j].split() for j in range(n_half_nodes)]))

		# Передалтаь обхелденит slr и sl info
		sl = SL()
		sl.ln = int(ln)
		sl.index = int(i)
		sl.L = l_p_i[0].values.astype('float64')
		sl.p = l_p_i[1].values.astype('float64')
		sl.interior_indexes_nodes = l_p_i[2].values.astype('int64')

		sl.w = w_s_u_k_h_i[0].values.astype('float64')
		sl.s = w_s_u_k_h_i[1].values.astype('float64')
		sl.u = w_s_u_k_h_i[2].values.astype('float64')
		sl.k = w_s_u_k_h_i[3].values.astype('float64')
		sl.h = w_s_u_k_h_i[4].values.astype('float64')
		sl.interior_indexes_half_nodes = w_s_u_k_h_i[5].values.astype('str')
		sls.append(sl)
	global sl_info
	sl_info = sls


def create_dataframe():
	dataframe = pd.DataFrame()
	dataframe['WellFrom'] = [s.wFrom for s in slr_info]
	dataframe['WellTo'] = [s.wTo for s in slr_info]
	dataframe['q'] = [s.q for s in slr_info]
	dataframe['phi'] = [s.phi for s in slr_info]
	dataframe['psi'] = [s.psi for s in slr_info]

	dataframe['ln'] = [s.ln for s in sl_info]
	dataframe['L'] = [s.L for s in sl_info]
	dataframe['p'] = [s.p for s in sl_info]
	dataframe['interior_indexes_nodes'] = [s.interior_indexes_nodes for s in sl_info]
	dataframe['w'] = [s.w for s in sl_info]
	dataframe['s'] = [s.s for s in sl_info]
	dataframe['u'] = [s.u for s in sl_info]
	dataframe['k'] = [s.k for s in sl_info]
	dataframe['h'] = [s.h for s in sl_info]
	dataframe['interior_indexes_half_nodes'] = [s.interior_indexes_half_nodes for s in sl_info]
	global df_sl_info
	df_sl_info = dataframe


def calc_press_st_info():
	p_i = df['p*h'].values / df['Volume_ST'].values
	p_d = df['p*h'].sum() / df['Volume_ST'].sum()
	e_p_i = p_i - p_d
	df['p'] = p_i
	df['E_p_i'] = e_p_i
	pass


def calc_ID_st_info(path):
	lt_ft = df_sl_info[['WellFrom', 'WellTo']].values
	st_unique_ft = np.unique(lt_ft, axis = 0)

	n_st_unique_ft = st_unique_ft.__len__()

	q = np.zeros(n_st_unique_ft)
	phi = np.zeros(n_st_unique_ft)
	psi = np.zeros(n_st_unique_ft)
	dp_i = np.zeros(n_st_unique_ft)

	tau_ij = np.zeros(n_st_unique_ft, dtype = np.ndarray)
	q_ij = np.zeros(n_st_unique_ft, dtype = np.ndarray)
	for i in range(n_st_unique_ft):
		d = df_sl_info[df_sl_info['WellFrom'] == st_unique_ft[i][0]]
		d = d[d['WellTo'] == st_unique_ft[i][1]]
		q[i] = d['q'].sum()
		phi[i] = d['phi'].sum()
		psi[i] = d['psi'].sum()
		p_aver = d['p'].sum() / d['p'].__len__()
		dp_i[i] = p_aver[0] - p_aver[-1]

		q_ij[i] = d['q'].values
		u = d['u'].values
		ll = d['L'].values
		tau_ij[i] = np.zeros(u.__len__(), dtype = np.ndarray)
		for j in range(u.__len__()):
			u[j] = np.delete(u[j], [0, -1])
			ll[j] = np.array([ll[j][k + 1] - ll[j][k] for k in range(ll[j].__len__() - 1)])
			tau_ij[i][j] = (ll[j] / u[j]).sum()

	a = df[df['Well_From'] >= -1]
	a = a[a['Well_From'] != 999999999]
	a = a[a['Well_To'] >= -1]
	a = a[a['Well_To'] != 999999999]
	st_n = a.__len__()
	if n_st_unique_ft != st_n:
		print('Error: Кол-во трубок тока не совпадает с кол-вом взаимодействующих скважин тз файла .slr')

	aa = a[['Well_From', 'Well_To']].values
	n1 = aa.__len__()
	n2 = n_st_unique_ft
	q_ft = np.zeros(n1)
	phi_ft = np.zeros(n1)
	psi_ft = np.zeros(n1)
	dp_i_ft = np.zeros(n1)

	m = np.zeros(n1)
	tau_i_min = np.zeros(n1, dtype = np.ndarray)
	tau_i = np.zeros(n1, dtype = np.ndarray)
	# adc = []
	for i in range(n1):
		adc = a[a['Well_From'] == aa[i][0]]
		adc = adc[adc['Well_To'] == aa[i][1]]
		m[i] = adc['m*h'].values / adc['Volume_ST'].values
		for j in range(n2):
			if aa[i][0] == st_unique_ft[j][0] and aa[i][1] == st_unique_ft[j][1] or aa[i][0] == st_unique_ft[j][1] and aa[i][1] == st_unique_ft[j][0]:
				q_ft[i] = q[j]
				phi_ft[i] = phi[j]
				psi_ft[i] = psi[j]
				dp_i_ft[i] = dp_i[j]
				tau_i[i] = (m[i] * tau_ij[j] * q_ij[j]).sum() / q[j]
				tau_i_min[i] = np.min(m[i] * tau_ij[j])

	global st_ft_info
	st_ft_info = pd.DataFrame()
	st_ft_info['###st_number'] = a['###st_number'].values
	st_ft_info['Well_From'] = a['Well_From'].values
	st_ft_info['Well_To'] = a['Well_To'].values
	st_ft_info['q'] = pd.Series(q_ft)
	st_ft_info['phi'] = pd.Series(phi_ft)
	st_ft_info['psi'] = pd.Series(psi_ft)
	st_ft_info['ID'] = pd.Series(q_ft / dp_i_ft)
	st_ft_info['tau_i'] = pd.Series(tau_i)
	st_ft_info['tau_i_min'] = pd.Series(tau_i_min)

	st_ft_info = pd.merge(a, st_ft_info, on = ["Well_From", "Well_To", "###st_number"])


def save(path):
	with pd.ExcelWriter(path + '\st_ft_info.xlsx') as writer:
		df.to_excel(writer, sheet_name = 'Все ТТ')
		st_ft_info.to_excel(writer, sheet_name = 'Взаимодействующие ТТ')
		# df.to_csv(path + 'st_ft_info_2.csv', sep='\t')


def stat_analiz(path):
	start_time = time.time()
	read_well_info(path + '\\well_info.txt')
	read_st_value_info(path + '\\st_ft_color_value.txt')
	# print('Параметры по взаимодействию с нагнетательными скважинами(без учета контура):', '\n',
	# 	  interaction_inj_with_prod_well_mu())
	read_slr_info(path.replace('Color_ST_analiz', 'Result') + '\\SLRates_PROD.slr')
	read_sl_info(path.replace('Color_ST_analiz', 'Result') + '\\SL_ST_PROD')
	create_dataframe()
	calc_press_st_info()
	calc_ID_st_info(path)

	save(path)
	print('time', time.time() - start_time)
	pass


if __name__ == '__main__':
	stat_analiz(sys.argv[1])
	print('StatisticsAnaliz.py Используется как исполняемый файл!')
else:
	print('StatisticsAnaliz.py Используется как библиотека!')
