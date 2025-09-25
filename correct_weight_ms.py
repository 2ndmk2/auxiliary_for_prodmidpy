import shutil
import os

# Your ms file
msfile = './averaged/AS209_continuum_averaged.ms'
#corrected ms file to be made
new_ms = './averaged/AS209_continuum_averaged_corrected.ms'

if not os.path.exists(new_ms):
    shutil.copytree(msfile, new_ms)
    print(f"Copied to {new_ms}")

# Set your value (from compute_bias_weight.py)
weight_bias =  3.4206

# Modify weight ' sigma
tb.open(new_ms, nomodify=False)     
weights = tb.getcol('WEIGHT')
sigmas  = tb.getcol('SIGMA')
tb.putcol('WEIGHT', weights / weight_bias )
tb.putcol('SIGMA',  sigmas  * (weight_bias **0.5))  # sqrt(3)倍に
tb.close()