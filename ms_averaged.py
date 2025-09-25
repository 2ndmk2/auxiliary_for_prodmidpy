import glob
import os 

# your msfile
msfile = "msfile.ms"

# out folder
out_folder="./averaged"
if not os.path.exists(out_folder):
    os.makedirs(out_folder)

# setting 
chanbin = 99999 ## average all chanels in each spw
timebin = "30s" ## you may change

# out file
out_name = os.path.join(out_folder, itemList[-1].replace(".ms", "_averaged.ms"))

# main
mstransform(vis=msfile, datacolumn='data', outputvis=out_name, keepflags=False, chanaverage=True, timeaverage=True, chanbin =chanbin, timebin="30s")
