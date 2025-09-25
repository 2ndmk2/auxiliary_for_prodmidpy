import numpy as np
def load_ms(ms_file):

    tb = casatools.table()
    c = 299792458.0 * 1e3/1e9 #mm Ghz

    # list to store u, v, visibility, weights, fruquencies
    u_list = []
    v_list = []
    vis_list = []
    weights_list = []
    freq_list = []


    # Get frequencies for channel & spw 

    tb.open(ms_file + '/SPECTRAL_WINDOW')

    num_spws = tb.nrows()
    spw_freq_dict = {}
    for spw_idx in range(num_spws):
        chan_freq = tb.getcell('CHAN_FREQ', spw_idx)
        spw_freq_dict[spw_idx] = chan_freq/1e9   ##  GHz
    tb.close()

    # spw info
    tb.open(ms_file + '/DATA_DESCRIPTION')
    spw_id = tb.getcol('SPECTRAL_WINDOW_ID')
    tb.close()

    tb.open(ms_file)

    # Processing for each SPW

    for desc_id in range(len(spw_id)):

        ## current spw
        spw = spw_id[desc_id]
        spw_freqs = spw_freq_dict[spw] ##  GHz
        wavelengths =c/spw_freqs ## mm

        ## get data for current spw
        subtb = tb.query(f'DATA_DESC_ID=={desc_id}')

        if subtb.nrows() > 0:
            # load
            uvw_spw = subtb.getcol('UVW')  # shape: (3, nvis)
            data_spw = subtb.getcol('DATA')  # shape: (npol, nchan, nvis)
            weight_spw = subtb.getcol('WEIGHT')  # shape: (npol, nvis)
            flag_spw = subtb.getcol('FLAG')  # shape: (npol, nchan, nvis)

            # shape info
            nchan = data_spw.shape[1] 
            nvis = data_spw.shape[2] 

            # u, v: m -> λ
            u_lambda = uvw_spw[0][None, :] * 1e3 / wavelengths[:, None] # shape: (nchan, nvis)
            v_lambda = uvw_spw[1][None, :] * 1e3 / wavelengths[:, None] # shape: (nchan, nvis)

            ## Make frequency matrix
            spw_freqs_map = np.tile(spw_freqs[:, None], (1, nvis)) # shape: (nchan, nvis)

            # Apply flag to weight
            flag_bool = flag_spw.astype(bool)
            eff_w = weight_spw[:, None, :] * (~flag_bool) ##  # shape: (npol, nchan, nvis) 

            # Compute weighted data
            data_weight_sum = np.sum(data_spw * eff_w, axis=0)  # shape: (nchan, nvis)
            weight_sum = np.sum(eff_w, axis=0)[:]  # shape: (nchan, nvis)
            data_weighted = np.zeros_like(data_weight_sum, dtype=data_spw.dtype)
            valid = (weight_sum > 0)                     # shape: (nchan, nvis)
            data_weighted = data_weight_sum[valid]/weight_sum[valid]

            # Add data to list
            u_list.extend(np.ravel(u_lambda[valid]))
            v_list.extend(np.ravel(v_lambda[valid]))
            vis_list.extend(np.ravel(data_weighted))
            weights_list.extend(np.ravel(weight_sum[valid]))
            freq_list.extend(np.ravel(spw_freqs_map[valid]))
        else:
            print("No data")



        subtb.close()  # close the subtb to avoid memory leak
    tb.close()
    return u_list, v_list, vis_list, weights_list, freq_list


#msfile = "./raw/AS209_continuum.ms"
#outfile ="./out.npz"
msfile ="./averaged/AS209_continuum_averaged_corrected.ms"
outfile ="./averaged_npz/AS209_continuum_averaged_corrected.vis.npz"

u_list, v_list, vis_list, weights_list, freq_list = load_ms(msfile )
print(np.shape(u_list), np.shape(vis_list))

## "-" is needed to match true (u,v)
np.savez(outfile , u_obs = - np.array(u_list), v_obs = - np.array(v_list), \
    vis_obs = vis_list, freq_obs= freq_list, wgt_obs = weights_list)
    
    