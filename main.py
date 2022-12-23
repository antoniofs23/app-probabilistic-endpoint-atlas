# Copyright (c) 2020 brainlife.io
#
# This file is a template for a python-based brainlife.io App
# brainlife stages this git repo, writes `config.json` and execute this script.
# this script reads the `config.json` and execute pynets container through singularity
#
# you can run this script(main) without any parameter to test how this App will run outside brainlife
# you will need to copy config.json.brainlife-sample to config.json before running `main` as `main`
# will read all parameters from config.json
#
# Author: Antonio Fernandez
# The University of Texas at Austin

# set up environment
import json
import os
import nibabel as nib
import numpy as np

# load inputs from config.json
with open('config.json') as config_json:
	config = json.load(config_json)

# Load into variables predefined code inputs
data_file = str(config['t1'])
 
'''
run time is approx 3-4 min
'''
# set project directory (where all subject directories are)
project_dir = '/Users/antonio/Desktop/proj-6396777a6881d56fbfcd0bbc/'
out_dir = '/Users/antonio/Desktop/proj-6396777a6881d56fbfcd0bbc/atlas'

#make output directory if it does not exist
if not os.path.exists(out_dir):
    os.mkdir(out_dir)
    
# get all subject directories -> first output is directory name
temp_dir = [direct[0] for direct in os.walk(project_dir)]

# only keep dir with the roi subdirectory as there are nested folders in project to subject roi dir
sub_dir = [direct for direct in temp_dir if '/rois' in direct]

# keep track of number of subjects for division
n = len(sub_dir)

# get all tract names by indexing into a subject directory and sorting
# this makes indexing easier as LPI is now odd and RAS is even; also same tracts are stacked together in twos
tract_names = sorted(next(os.walk(sub_dir[0]))[2])

# tract counter
tract_count = 1
# load the files sum and divide to create probability map
for jj in range(len(tract_names)):
    # split tract names for easier searching and saving
    name = tract_names[jj].split('_')      
    
    for ii in range(len(sub_dir)):
        # load the tract for all subs
        img = nib.load(sub_dir[ii]+'/'+tract_names[jj]) 
        
        # initialize the data mats
        if ii == 0:
            data = np.zeros((img.get_fdata()).shape)        
        # sum across subjects
        data += img.get_fdata()
    
    # have to match affine transform for output
    input_affine = img.affine
    
    #normalize
    data = data/n
    converted_array = np.array(data,dtype=np.float32)
    new_img = nib.Nifti1Image(converted_array,affine=input_affine) #turn into nifti
    filename = str(tract_count)+'_'+name[3]+'_'+name[0]+'_'+'[min_'+str(np.min(data))+'_'+'max_'+str(np.max(data))+']'+'.nii.gz'
    nib.save(new_img,os.path.join(out_dir+'/',filename)) # save file
    if jj%2:
        tract_count+=1 # update tract counter
