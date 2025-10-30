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

    u_mat = []
    v_mat = []
    freq_mat = []

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
            u_mat.append(-u_lambda[0])
            v_mat.append(-v_lambda[0])
            spw_freqs_map = np.tile(spw_freqs[:, None], (1, nvis)) # shape: (nchan, nvis)
            freq_mat.append(spw_freqs_map[0])
        else:
            print("No data")

        subtb.close()  # close the subtb to avoid memory leak
    tb.close()
    return u_mat, v_mat, freq_mat

if __name__ == '__main__':
    msfile = "./averaged/AS209_continuum_averaged.ms"
    outfile = "./vis_data/AS209_vis_each_spw.npz"

    u_mat, v_mat, freq_mat = load_ms(msfile )

    np.savez(outfile,
            u_spw=np.array(u_mat, dtype=object),
            v_spw=np.array(v_mat, dtype=object),
            freq_spw=np.array(freq_mat, dtype=object))    
