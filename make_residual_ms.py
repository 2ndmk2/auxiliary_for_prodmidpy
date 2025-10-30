import shutil
import numpy as np
import os
import sys
import glob
import shutil
import pickle 

def put_res_vis_ms(msfile, model):

	# Use CASA table tools to get columns of UVW, DATA, WEIGHT, etc.
	tb.open(msfile, nomodify=False)
	data   = tb.getcol("DATA")
	data_new = np.array([ [data[0,0,:] - model],  [data[1,0,:] - model]])
	tb.putcol("DATA", data_new )
	tb.close()

def unpack_ragged(data, lengths):
    if len(lengths) == 0:
        return []
    split_idx = np.cumsum(lengths)[:-1]
    return np.split(data, split_idx)

def put_res_from_protomidpy(ms_file, models):

	tb = casatools.table()

	count = 0
	# Get frequencies for channel & spw 


	# spw info
	tb.open(ms_file + '/DATA_DESCRIPTION')
	spw_id = tb.getcol('SPECTRAL_WINDOW_ID')
	tb.close()

	tb.open(ms_file, nomodify=False)

	# Processing for each SPW

	for desc_id in range(len(spw_id)):

		## get data for current spw
		subtb = tb.query(f'DATA_DESC_ID=={desc_id}')
		
		if subtb.nrows() > 0:
			# load
			model_now = np.array(models[count])
			data_spw = subtb.getcol('DATA')  # shape: (npol, nchan, nvis)
			data_new = np.array([ [data_spw[0,0,:] - model_now],  [data_spw[1,0,:] - model_now]])
			subtb.putcol("DATA", data_new )
			count +=1
		else:
			print("No data")

		subtb.close()  # close the subtb to avoid memory leak
	tb.close()


def deprojected(msfile, cosi, pa):

	# Use CASA table tools to get columns of UVW, DATA, WEIGHT, etc.
	# note that "uvw" is unit of "m"
	tb.open(msfile, nomodify=False)
	uvw    = - tb.getcol("UVW") #m
	u = uvw[0]
	v = uvw[1]
	w = uvw[2]
	u_new = cosi * (np.cos(pa) * u - np.sin(pa) * v  )
	v_new =  (np.sin(pa) * u + np.cos(pa) * v  )
	uvw_new = np.array([u_new, v_new, w])
	tb.putcol("UVW", -uvw_new)
	tb.close()


def put_imag_vis_ms(msfile):

	tb.open(msfile, nomodify=False)
	data   = tb.getcol("DATA")
	data_new = np.array([ [1j * data[0,0,:].imag],  [1j * data[1,0,:].imag]])
	tb.putcol("DATA", data_new )
	tb.close()


def put_real_vis_ms(msfile):

	tb.open(msfile, nomodify=False)
	data   = tb.getcol("DATA")
	data_new = np.array([ [data[0,0,:].real],  [data[1,0,:].real]])
	tb.putcol("DATA", data_new )
	tb.close()

if __name__ == '__main__':
	target_name = "IMLup"
	## cos (dec). dec is in "rad" unit 
	cos_dec = 0.968717 ## AS209
	cos_dec = 0.786## IMLup

	##  Input files
	modelfile="./result/mcmc/%s_continuum_averagedmodel.npz" % target_name
	msfile = "./averaged/%s_continuum_averaged.ms" % target_name
	cos_dec = 0.968717 ## cos (dec). dec is in "rad" unit. This value is for AS 209
	

	## Output files
	folder_sub ="./ms_data_sub"
	folder_depro = "./phase_shifted_sub_deprojected" 
	folder_shift = "./phase_shifted_sub"
	folder_imag ="./ms_data_sub_only_imag"
	folder_real ="./ms_data_sub_only_real"
	
	basename = os.path.basename(msfile)
	subfile = os.path.join(folder_sub, basename)
	shiftfile = os.path.join(folder_shift, basename)
	deprojectfile = os.path.join(folder_depro, basename)
	imagfile = os.path.join(folder_imag ,basename)
	realfile = os.path.join(folder_real ,basename)

	###  Model subtraction
	if not os.path.exists(folder_sub):
		os.makedirs(folder_sub)

	if os.path.exists(subfile):
		shutil.rmtree(subfile,ignore_errors=True)
	shutil.copytree(msfile, subfile)
	vis_model = np.load(modelfile)
	data = vis_model["vis_model_all"]
	lengths = vis_model["lengths"]
	vis_model_spw = unpack_ragged(data, lengths)
	put_res_from_protomidpy(subfile, vis_model_spw)

	###  Aligning phasecenter with disk center

	if not os.path.exists(folder_shift):
		os.makedirs(folder_shift)
	if os.path.exists(shiftfile):
		shutil.rmtree(shiftfile,ignore_errors=True)

	sample = np.load(modelfile)["sample_best"] # get MAP estimate
	delta_x = sample[4]
	delta_y = sample[5]	
	if delta_y>0:
		phasecenter= "%.4fs +00d00m%.5f" % (delta_x/15.0/cos_dec, delta_y)
	else:
		phasecenter= "%.4fs -00d00m%.5f" % (delta_x/15.0/cos_dec, -delta_y)
	fixvis(vis = subfile, outputvis = shiftfile, phasecenter = phasecenter)


	#### Deprojection 

	if not os.path.exists(folder_depro):
		os.makedirs(folder_depro)
	if os.path.exists(deprojectfile):
		shutil.rmtree(deprojectfile, ignore_errors=True) 
	shutil.copytree(shiftfile,deprojectfile) 
	sample = np.load(modelfile)["sample_best"] 
	cosi = sample[2]
	pa = sample[3]
	deprojected(deprojectfile, cosi, pa)


	## Decomposing msfiles into real & imaginary parts

	if not os.path.exists(folder_imag):
		os.makedirs(folder_imag)
	if os.path.exists(imagfile):
		shutil.rmtree(imagfile, ignore_errors=True) 
	shutil.copytree(deprojectfile, imagfile) 
	put_imag_vis_ms(imagfile)

	if not os.path.exists(folder_real):
		os.makedirs(folder_real)
	if os.path.exists(realfile):
		shutil.rmtree(realfile, ignore_errors=True) 
	shutil.copytree(deprojectfile, realfile) 
	put_real_vis_ms(realfile)




