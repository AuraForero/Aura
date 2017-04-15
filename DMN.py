#!/usr/bin/python
import sys
import numpy as np
import nibabel as nib

import os
import commands
import nibabel as nib

def print_list(x):
    for i in x:
        print i
        
def isize(t):
    return [len(t[:,0,0]),len(t[0,:,0]),len(t[0,0,:])]

def stdnz(a):
    return np.std(a[np.nonzero(a)])

def meannz(a):
    return np.mean(a[np.nonzero(a)])

def norma_EU(img1,img2):
    norm=(img1-img2)**2
    return norm.sum()


def lim(img, lim=[0.8,2.5]):
    imgm=meannz(img)
    imgs=stdnz(img)
    return [imgm+imgs*lim[0],imgm+imgs*lim[1]]

def flim(img, lim=[0.8,2.5]):
    limi=lim(img, lim)
    img[img>limi[1]]=limi[1]
    img[img<limi[0]]=0
    return img
    
def getKey(item):
    return item[0]

def print_lis(lis):
    for i in lis:
        print i
        
def norm_sm(img):
    #print type(img.data)
    imgmed=meannz(img)
    imgstd=stdnz(img)

    img=img-imgmed
    img[img==-imgmed]=0

    img=img/imgstd
    return img


def estad1(img,templ):
    #Dice
    os.system('echo Estadistico1')
    limits=lim(img)
    
    img[img<limits[0]]=0
    
    value_A=np.count_nonzero(img)
    value_B=np.count_nonzero(templ)
    
    templ[templ>0.0]=1.0
    templ[templ<=0.0]=0.0
    
    img=templ*img
    value_inter=np.count_nonzero(img)
    
    return 2*float(value_inter)/float(value_A+value_B)


def estad2(img,templ):
    
    os.system('echo Estadistico2')
    
    limits=lim(img)
    
    img[img>limits[1]]=limits[1]
    img[img<limits[0]]=0
    
    img2=img.copy()
    img2[img2!=0]=1.0
    
    img2=img2*templ
    
    value_A=np.sum(img2)
    value_B=91.*109.

    estat2=value_A/value_B
    
    return estat2

def Japoneses(img,templ):
    limits=lim(img)
    os.system('echo Estadistico4')
    
    img2=img.copy()
    img3=img.copy()
    
    img2[img2!=0.0]=1.0
    
    
    templ2=templ.copy()
    templ2[templ2>0]=1.0
    templ2[templ2<=0]=0.0
    
    mask=templ2*img2
    M=float(np.count_nonzero(templ2))
    
    templ=mask*templ
    img=mask*img
    
    imgmed1=meannz(img)
    imgstd1=stdnz(img)
    
    imgmed2=meannz(templ)
    imgstd2=stdnz(templ)
    
    temimg=(img-imgmed1)
    temimg[mask!=1.0]=0

    temtempl=(templ-imgmed2)
    temtempl[mask!=1.0]=0

    
    img=temimg/imgstd1
    templ=temtempl/imgstd2
    
    
    img=img*templ
    v4=float(np.sum(img))/M
    os.system('echo Estadistico4 '+str(v4))
    
    if(0<np.count_nonzero(np.isnan(v4))):
        print imgstd1
        print img
        print img3
        
        print np.sum(img)
        print float(np.count_nonzero(img))
        raise Exception('Valores locos en uno!')
    return v4 

def DMS(dir_iin,dir_iout,dirtp,FormatImgSave='/home/arbey/Escritorio/DMN_DUAL_EST4/ImagesC_Aniso1/dr_stage2_subject00000.nii'):
    
    #templs=['template_prob.nii','template_bina.nii','template_suma.nii']
    #dirtp=dir_templ+templs[0]

    templ = nib.load(dirtp)
    img = nib.load(dir_iin)
    dataTempl = templ.get_data()[:,:,:]
    listMejor=[]
    for i in range(img.get_data().shape[3]):
        data = img.get_data()[:,:,:,i]
        fitness = Japoneses(data,dataTempl)
        listMejor.append([i,fitness])
    def getKey(p):
        return p[1]
    listMejor=sorted(listMejor, key=getKey, reverse=True)
    print listMejor[0][0]
    templSave = nib.load(FormatImgSave)
    #templSave.data=img.get_data()[:,:,:,listMejor[0][0]]
    #nib.save(templSave, dir_iout)
    mask=dataTempl.copy()
    mask[mask!=0]=1.0
    mask[mask==0]=0.0
    
    new_image = nib.Nifti1Image(mask*img.get_data()[:,:,:,listMejor[0][0]], templSave.affine)
    nib.save(new_image, dir_iout)



DMS(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
