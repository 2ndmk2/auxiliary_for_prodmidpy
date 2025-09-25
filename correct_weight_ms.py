import shutil
import os

msfile = './averaged/AS209_continuum_averaged.ms' # 元のMS
new_ms = './averaged/AS209_continuum_averaged_corrected.ms' # 元のMS

if not os.path.exists(new_ms):
    shutil.copytree(msfile, new_ms)
    print(f"Copied to {new_ms}")

weight_bias =  3.4206
tb.open(new_ms, nomodify=False)     # 書き込み可能で開く
weights = tb.getcol('WEIGHT')
sigmas  = tb.getcol('SIGMA')
tb.putcol('WEIGHT', weights / weight_bias )
tb.putcol('SIGMA',  sigmas  * (weight_bias **0.5))  # sqrt(3)倍に
tb.close()