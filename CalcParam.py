from FemFrameTool import read_fun


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
	store_oil = e * h * m * (1 - s0)
	return store_oil


def calc_current_water_saturation_field(relative_path):
	s = read_fun(relative_path + 's.fun')
	return s


def calc_current_store_oil_field(relative_path):
	e = calc_sandiness_field(relative_path)
	h = calc_height_field(relative_path)
	m = calc_poro_field(relative_path)
	s = calc_current_water_saturation_field(relative_path)
	store_oil = e * h * m * (1 - s)
	return store_oil
