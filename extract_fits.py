#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author: Christophe Mathé
# Date: 28/02/20
# run: python3 extract_fits.py

from astropy.io import fits
from os import listdir, makedirs, remove
from os.path import isdir
from shutil import rmtree
from numpy import savetxt, where, c_


def message_error(string):
	print(string)
	exit
	

def extract_information(name, data):
	with open(name, 'w') as file_write:
		file_write.write('General information of the flyby:\n')
		file_write.write('---------------------------------\n')
		file_write.write(repr(data[0].header[4:-2]))
		file_write.write('\n')
		file_write.write('\n')
		file_write.write('\n')
		file_write.write('FP4 spectra information:\n')
		file_write.write('------------------------\n')
		file_write.write('Shift km: '+str(data['SPECTRA_FP4'].header[8])+', /!\ this shift is already applied on altitude of limb spectra.\n')
		file_write.write('Shift freq: '+str(data['SPECTRA_FP4'].header[9])+'\n')
		file_write.write('\n')
		file_write.write('FP3 spectra information:\n')
		file_write.write('------------------------\n')
		file_write.write('Shift freq: '+str(data['SPECTRA_FP3'].header[9]))


def extract_and_save_spectra(name, data, altitude):
	makedirs(name)

	nb_point = data.shape[0]
	nb_spectra = len(data[0]) - 1 # 1st: wvnb

	for i in range(nb_spectra):
		with open(name+'/limb_'+str(int(altitude.field(0)[i]))+'km.spe', "ab") as file_write:
			# the first 3 lines is adpated to our retrieval code, you can remove these lines
			file_write.write(b'# Spectrum from Mathe et al. 2019\n')
			file_write.write((str(nb_point)+"\n").encode('ascii'))
			file_write.write((str(int(altitude.field(0)[i]))+"\n").encode('ascii'))
			savetxt(file_write, c_[data.field(0), data.field(1+i)],
			        fmt='%7.2f %.4e')
		file_write.close()
		

def extract_and_save_profile(name, data):
	# Select only where information is retrieved with 1-sigma error
	mask = where(data['SIGMA'] == 1)
	data = data[mask]
	if data.shape[0] != 0:
		# field(1): pressure (mbar), T(K)/VMR, T_inf(K)/VMR_inf, T_sup(K)/VMR_sup
		savetxt(name+'.txt', c_[data.field(1), data.field(2), data.field(3), data.field(4)])


def main():
	directory_input = 'input'
	list_file = listdir('.')
	list_fits = [x for x in list_file if '.fits' in x]
	
	# Check existence of fits files
	if not list_fits:
		message_error('Warning: no fits file in the current directory!')
	
	for i, fits_name in enumerate(list_fits):
		directory_root = fits_name.split('table')[1][:-5] + '/'

		# Check if the "directory_root" already exists
		if isdir(directory_root):
			rmtree(directory_root)
			makedirs(directory_root)
		else:
			makedirs(directory_root)

		makedirs(directory_root+directory_input)

		with fits.open(fits_name) as hdul:
			
			extract_information(directory_root+'information.txt', hdul)

			data_fp3 = hdul['SPECTRA_FP3'].data
			data_altitude_fp3 = hdul['ALTITUDE_FP3'].data
			extract_and_save_spectra(directory_root+'spectra_fp3', data_fp3, data_altitude_fp3)

			data_fp4 = hdul['SPECTRA_FP4'].data
			data_altitude_fp4 = hdul['ALTITUDE_FP4'].data
			extract_and_save_spectra(directory_root+'spectra_fp4', data_fp4, data_altitude_fp4)
			
			extract_and_save_profile(directory_root+directory_input+'/thermal_profile', hdul['THERMAL_PROFILE'].data)
			extract_and_save_profile(directory_root+directory_input+'/c2h2_profile', hdul['C2H2_PROFILE'].data)
			extract_and_save_profile(directory_root+directory_input+'/c2h4_profile', hdul['C2H4_PROFILE'].data)
			extract_and_save_profile(directory_root+directory_input+'/c2h6_profile', hdul['C2H6_PROFILE'].data)
			extract_and_save_profile(directory_root+directory_input+'/c3h8_profile', hdul['C3H8_PROFILE'].data)
			extract_and_save_profile(directory_root+directory_input+'/c3h4_profile', hdul['C3H4_PROFILE'].data)
			extract_and_save_profile(directory_root+directory_input+'/c4h2_profile', hdul['C4H2_PROFILE'].data)
			extract_and_save_profile(directory_root+directory_input+'/c6h6_profile', hdul['C6H6_PROFILE'].data)
			extract_and_save_profile(directory_root+directory_input+'/hcn_profile', hdul['HCN_PROFILE'].data)
			extract_and_save_profile(directory_root+directory_input+'/hc3n_profile', hdul['HC3N_PROFILE'].data)
			extract_and_save_profile(directory_root+directory_input+'/co2_profile', hdul['CO2_PROFILE'].data)

			
if __name__ == '__main__':
	main()
