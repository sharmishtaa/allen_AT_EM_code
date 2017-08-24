from argschema import ArgSchemaParser, ArgSchema
from argschema.fields import Str
from argschema.schemas import DefaultSchema
import numpy as np
import os
import tifffile
#import argparse
#import matplotlib.pyplot as plt
import cv2
from scipy import ndimage
from skimage.morphology import white_tophat, disk
import marshmallow as mm
#from json_module import JsonModule,ModuleParameters,InputDir
import argschema

class multIntensityCorrParams(argschema.ArgSchema):
    inputImage = mm.fields.Str(required=True,
        metadata={'description':'Path of input image'})
    outputImage = mm.fields.Str(required=True,
        metadata={'description':'Path of where to save the output image'})
    flatfieldStandardImage = mm.fields.Str(required=True,
        metadata={'description':'Flat field standard Image'})

class multIntensityCorr(argschema.ArgSchemaParser):
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

    example_json = {
        "inputImage": "/nas2/data/Datatest/data/session0/DAPI/DAPI_S0000_F0006_Z00.tif",
        "outputImage": "/nas2/data/Datatest/testing/testoutput.tif",
        "flatfieldStandardImage": "/nas2/data/Datatest/testing/testmedian.tif",
        "output_json" : "/nas2/data/Datatest/testing/output_json1.json"
    }
    mod = multIntensityCorr(input_data=example_json, schema_type=multIntensityCorrParams)
    mod.run()
