import xml.etree.ElementTree as ET
import sys


class Config:
	def __init__(self, pixel, path_file_names, path_file_names_for_save, path_folder_save, path_relative_folder, kku,
				mmu_water, mmu_oil, path_table_rel_phase_perm):
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
		self.mu_water = mmu_water
		self.mu_oil = mmu_oil
		self.path_relative_phase_permeability = path_table_rel_phase_perm


def read_xml_config():
	path_xml_file = sys.argv[1]
	tree = ET.parse(path_xml_file)
	root = tree.getroot()
	pixel_size = int(root.find('pixel_size').text)
	ku = float(root.find('ku').text)
	mu_water = float(root.find('mu_water').text)
	mu_oil = float(root.find('mu_oil').text)
	path_rel_phase_perm = root.find('path_rel_perm').text
	relative_path = root.find('relative_path').text
	relative_path_for_save = root.find('relative_path_for_save').text
	folder_name = root.find('folder_name_for_save').text
	path_save = relative_path_for_save + folder_name + '\\'
	path_file_names = [relative_path + file_name.text for file_name in root.find('file_names').findall('file_name')]
	path_file_names_for_save = [
		path_save + file_names_for_save.text for file_names_for_save in
		root.find('file_names_for_save').findall('file_name_save')]
	cfg = Config(pixel_size, path_file_names, path_file_names_for_save, path_save, relative_path, ku, mu_water, mu_oil,
				path_rel_phase_perm)
	return cfg
