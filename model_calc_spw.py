import numpy as np
import matplotlib.pyplot as plt
import glob
from protomidpy import data_gridding
from protomidpy import sample
from protomidpy import utils
from protomidpy import mcmc_utils
from protomidpy import hankel
import os

ARCSEC_TO_RAD= 1/206265.0
mcmc_result_folder ="./result/mcmc"
files = glob.glob(os.path.join(mcmc_result_folder, "*.vis_mcmc.npz"))

for file in files:

    ### Load mcmc result
    target_id = file.split("/")[-1].replace("_continuum_averaged.vis_mcmc.npz","")
    mcmc_para = os.path.join(mcmc_result_folder, "%s_continuum_averaged.vis_mcmc.npz" % target_id)
    mcmc_result = np.load(mcmc_para)
    sample_now = mcmc_result["sample"]
    log_posterior = mcmc_result["log_prior"] + mcmc_result["log_likelihood"] 
    sample_goods = sample_now[20000:,:]
    sample_best = sample_now[np.argmax(np.ravel(log_posterior)),:]
    n_bin_log = mcmc_result["n_bin_log"]
    nrad = mcmc_result["nrad"] 
    dpix= mcmc_result["dpix"] * ARCSEC_TO_RAD
    cov = mcmc_result["cov"]
    R_out = nrad * dpix
    q_min_max_bin = [mcmc_result["qmin"], mcmc_result["qmax"]]



    ### To compute models
    visfile = "./vis_data/%s_continuum_averaged.vis.npz" % target_id
    out_residual = mcmc_para.replace(".vis_mcmc", "model")
    u_d, v_d, vis_d, wgt_d, freq_d = utils.load_obsdata(visfile)
    mask = freq_d > 100
    u_d = u_d[mask]
    v_d = v_d[mask]
    wgt_d = wgt_d[mask]
    vis_d = vis_d[mask]
    
    coord_for_grid_lg, rep_positions_for_grid_lg, uu_for_grid_pos_lg, vv_for_grid_pos_lg = data_gridding.log_gridding_2d(q_min_max_bin[0], q_min_max_bin[1], n_bin_log)
    u_grid_2d, v_grid_2d, vis_grid_2d, noise_grid_2d, sigma_mat_2d, d_data,  binnumber = \
        data_gridding.data_binning_2d(u_d, v_d,vis_d, wgt_d, coord_for_grid_lg)
    r_n, jn, qmax, q_n, H_mat_model, q_dist_2d_model, N_d, r_dist, d_A_minus1_d, logdet_for_sigma_d  = hankel.prepare(R_out, nrad,  d_data, sigma_mat_2d)

    
    flux_arr = []
    for sample_now in sample_goods[:1,:]:
        flux_sampled, H_mat = sample.sample_radial_profile(r_dist, sample_now, u_grid_2d, v_grid_2d, R_out, \
                    nrad, dpix, d_data, sigma_mat_2d, q_dist_2d_model, H_mat_model, cov=cov)
        flux_arr.append(flux_sampled)

    sample_one_taken, H_mat = sample.map_map(r_dist, sample_best, u_grid_2d, v_grid_2d, R_out, \
                    nrad, dpix, d_data, sigma_mat_2d, q_dist_2d_model, H_mat_model, cov=cov)
    H_mat, q_dist, d_real_mod, d_imag_mod, vis_model_real, vis_model_imag, u_mod, v_mod= mcmc_utils.obs_model_comparison(sample_one_taken, u_grid_2d, v_grid_2d, sample_best, d_data, R_out, nrad, dpix)
    vis_model, residual  = mcmc_utils.make_model_and_residual(u_d, v_d, sample_best, sample_one_taken, vis_d, R_out, nrad, dpix)


    ### To compute model for measurement set
    spw_visfile = "./vis_data/%s_vis_each_spw.npz" % target_id
    data_spw = np.load(spw_visfile, allow_pickle=True)
    u_spw, v_spw = data_spw["u_spw"],  data_spw["v_spw"]

    lengths = [len(u) for u in u_spw]
    u_all = np.concatenate(u_spw)
    v_all = np.concatenate(v_spw)
    vis_model_spw = []
    vis_model_all, residual_all = mcmc_utils.make_model_and_residual(
    u_all, v_all, sample_best, sample_one_taken, np.ones_like(u_all),
    R_out, nrad, dpix )
    split_idx = np.cumsum(lengths)[:-1]
    vis_model_spw = np.split(vis_model_all, split_idx)

    
    np.savez(out_residual, sample_best = sample_best, r_arr = r_n, flux_best = sample_one_taken, flux_arr = flux_arr, vis_model = vis_model, residual = residual, vis_model_all =vis_model_all, lengths =lengths, 
        q_best = q_dist, vis_model_best = vis_model_real+1j*vis_model_imag, d_real_best = d_real_mod,  d_imag_best = d_imag_mod, noise_best =  noise_grid_2d)
