import numpy as np
import os
import tifffile
import argparse
#import matplotlib.pyplot as plt
import cv2
from scipy import ndimage
from skimage.morphology import white_tophat, disk
import marshmallow as mm
from json_module import JsonModule,ModuleParameters,InputDir

class multIntensityCorrParams(ModuleParameters):
    inputImage = mm.fields.Str(required=True,
        metadata={'description':'Path of input image'})
    outputImage = mm.fields.Str(required=True,
        metadata={'description':'Path of where to save the output image'})
    flatfieldStandardImage = mm.fields.Str(required=True,
        metadata={'description':'Flat field standard Image'})

class multIntensityCorr(JsonModule):
    def __init__(self,schema_type=None,*args,**kwargs):
        if schema_type is None:
            schema_type = multIntensityCorrParams
        super(multIntensityCorr,self).__init__(schema_type = schema_type,*args,**kwargs)
        #self.render=renderapi.render.connect(**self.args['render'])
    def run(self):

        inputImage = self.args['inputImage']
        outputImage = self.args['outputImage']
        flatfieldStandardImage = self.args['flatfieldStandardImage']

        print inputImage
        print outputImage
        print flatfieldStandardImage
        #exit(0)

        img = tifffile.imread(inputImage)
        ff = tifffile.imread(flatfieldStandardImage)

        img = img.astype(float)
        ff = ff.astype(float)

        num = np.ones((ff.shape[0],ff.shape[1]))
        fac = np.divide(num* np.amax(ff),ff+0.0001)
        result = np.multiply(img,fac)
        result = np.multiply(result,np.mean(img)/np.mean(result))
        result_int = np.uint16(result)

        dirout = os.path.dirname(outputImage)
        if not os.path.exists(dirout):
        	os.makedirs(dirout)

        tifffile.imsave(outputImage,result_int)

if __name__ == '__main__':

    mod = multIntensityCorr(schema_type=multIntensityCorrParams)
    mod.run()
