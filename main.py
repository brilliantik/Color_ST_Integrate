import subprocess
from StatisticsAnaliz import stat_analiz
from MeshAndPixel_Size import give_nelem_and_npixel
from ctypes import *
from TMap_2 import create_t_map
# from RPData import RPData


def main():
	# give_nelem_and_npixel('C:\Stud\ST_LT\SL_ST_EXAMPLE\Sarapal_ST_Integrate_test\\')

	# give_nelem_and_npixel('C:\Stud\ST_LT\SL_ST_EXAMPLE\Ex2\\')
	# args = 'C:\Stud\ST_LT\SL_ST_EXAMPLE\Ex2\info.xml'

	# args = 'C:\Stud\ST_LT\Color_ST_Integrate\info.xml'
	# subprocess.call(['python.exe', 'C:\Stud\ST_LT\Color_ST_Integrate\ImageCreate.py', args])
	# subprocess.call(['python.exe', 'C:\Stud\ST_LT\Color_ST_Integrate\IntegratorST.py', args])


	# stat_analiz('C:\Stud\ST_LT\SL_ST_EXAMPLE\Ex1\Color_ST_analiz\\')

	# stat_analiz('C:\Stud\ST_LT\SL_ST_EXAMPLE\Sarapal_ST_Integrate_test\Color_ST_analiz\\')


	# give_nelem_and_npixel('C:\Stud\ST_LT\SL_ST_EXAMPLE\example_optimize_3\\')
	# args = 'C:\Stud\ST_LT\SL_ST_EXAMPLE\\example_optimize_3\info.xml'



	# subprocess.call(['python.exe', 'C:\Stud\ST_LT\Color_ST_Integrate\ImageCreate.py', args])
	# create_t_map('C:\Stud\ST_LT\SL_ST_EXAMPLE\\example_optimize_3\\')
	# subprocess.call(['python.exe', 'C:\Stud\ST_LT\Color_ST_Integrate\IntegratorST.py', args])
	# stat_analiz('C:\Stud\ST_LT\SL_ST_EXAMPLE\\example_optimize_3\Color_ST_analiz\\')

	# args = 'C:\Stud\ST_LT\SL_ST_EXAMPLE\example_6\q_025_075\\t_300\info.xml'
	# subprocess.call(['python.exe', 'C:\Stud\ST_LT\Color_ST_Integrate\ImageCreate.py', args])
	# create_t_map('C:\Stud\ST_LT\SL_ST_EXAMPLE\example_6\q_025_075\\t_300\\')
	# subprocess.call(['python.exe', 'C:\Stud\ST_LT\Color_ST_Integrate\IntegratorST.py', args])
	# stat_analiz('C:\Stud\ST_LT\SL_ST_EXAMPLE\example_6\q_025_075\\t_300\Color_ST_analiz\\')


	# give_nelem_and_npixel('C:\Stud\ST_LT\SL_ST_EXAMPLE\example_optimize_7\\')
	args = 'C:\Stud\ST_LT\SL_ST_EXAMPLE\example_optimize_7\info.xml'
	subprocess.call(['python.exe', 'C:\Stud\ST_LT\Color_ST_Integrate\ImageCreate.py', args])
	create_t_map('C:\Stud\ST_LT\SL_ST_EXAMPLE\example_optimize_7\\')
	subprocess.call(['python.exe', 'C:\Stud\ST_LT\Color_ST_Integrate\IntegratorST.py', args])
	stat_analiz('C:\Stud\ST_LT\SL_ST_EXAMPLE\example_optimize_7\\Color_ST_analiz\\')


if __name__ == '__main__':
	main()
else:
	raise SystemExit('Это не библиотека!')
