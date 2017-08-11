#input, root directory of images
import argparse
import os
import csv
import tifffile
import numpy as np
import glob
from scipy.ndimage.filters import gaussian_filter
import marshmallow as mm
from json_module import JsonModule,ModuleParameters,InputDir

class makeMedianParams(ModuleParameters):
    inputDirectory = mm.fields.Str(required=True,
        metadata={'description':'Input Directory Path'})
    outputImage = mm.fields.Str(required=True,
        metadata={'description':'Path of output Image'})
    filepart = mm.fields.Str(required=False,
        metadata={'description':'Part of filename to parse by (usually the channel name or section name or combination)'})

class makeMedian(JsonModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = makeMedianParams
        super(makeMedian,self).__init__(schema_type = schema_type,*args,**kwargs)
        #self.render=renderapi.render.connect(**self.args['render'])
    def run(self):

		inputDirectory = self.args['inputDirectory']
		outputImage = self.args['outputImage']
		filepart = self.args['filepart']

		spch = ''
		if len(filepart) > 0:
			spch = '*'
		querystr = inputDirectory + '/*' + filepart + spch + '.tif'
		files = glob.glob(querystr)

		print files
		#exit(0)

		#read the first image to find the size of the stack
		img0 = tifffile.imread(files[0])
		(N,M)=img0.shape
		Z=len(files)
		#setup the image stack in memory
		stack = np.zeros((N,M,Z),dtype=img0.dtype)
		##read in the stack
		j = 0
		for i,file in enumerate(files):
			print "reading image %d"%i
			print file
			inpimg = tifffile.imread(file);
			st = np.std(inpimg)
			print st
			stack[:,:,j]=inpimg
			j = j+1

		stack = stack[:,:,0:j];

		np.median(stack,axis=2,overwrite_input=True)
		(A,B,C)=stack.shape

		if (j%2 == 0):
			med1 = stack[:,:,j/2-1]
			med2 = stack[:,:,j/2+1]
			med = (med1+med2)/2
		else:
			med = stack[:,:,(j-1)/2]

		print med.dtype
		med = gaussian_filter(med,10)

		dirmap = os.path.dirname(outputImage)
		if not os.path.exists(dirmap):
			os.makedirs(dirmap)

		tifffile.imsave(outputImage,med)


if __name__ == '__main__':

	mod = makeMedian(schema_type=makeMedianParams)
	mod.run()
