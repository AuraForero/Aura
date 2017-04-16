#!/usr/bin/python
from nifti import *
import nifti
import numpy as np
import os
import commands
import matplotlib.pyplot as plt
import time 
import commands
import sys

class Noise:
    def __init__(self,iin, iout,fol_out, noiseDir,nVols):
        self.iin=iin
        self.iout=iout
        self.fol_out=fol_out
        self.noiseDir=noiseDir
        self.nVols=nVols
        
    def run(self):
        self.Img_noise(self.iin,self.fol_out, self.noiseDir)
        
    #escribe matrices
    def write_mat(self,T,dir_out_mat):
        fil=open(dir_out_mat,'w')
        for i in range (4):
            text=''
            for j in range (4):
                text= text+' '+str(T[i,j])
            fil.write(text+'\n')  

    #genera matrices de transformacion
    def genera_matriz(self,x,y,z,a,b,g):#angulos en radianes
        Rx=np.array([[1,0,0,0],
                      [0,np.cos(a), -1*np.sin(a),0],
                      [0,np.sin(a), np.cos(a),0],
                      [0,0,0,1]])

        Ry=np.array([[np.cos(b),0, np.sin(b),0],
                      [0,1,0,0],
                      [-1*np.sin(b),0,np.cos(b),0],
                      [0,0,0,1]])    

        Rz=np.array([[np.cos(g), -1*np.sin(g),0,0],
                     [np.sin(g), np.cos(g),0,0],
                     [0,0,1,0],
                     [0,0,0,1]])

        T=np.array([[0,0,0,x],
                    [0,0,0,y],
                    [0,0,0,z],
                    [0,0,0,0]])

        Rt=np.dot(np.dot(Rx,Ry),Rz)
        T=Rt+T
        return T

    def Trasformacion(self,dp=np.array([0,0,0]),da=np.array([0,0,0]),dir_img='',dir_out_mat='',save=False):
        if((dir_img=='')or(dir_out_mat=='')):
            raise Exception('Falta la direccion')
        print '-------------Error',dir_img,'+----------'

        lista=commands.getstatusoutput('fsl5.0-fslhd '+dir_img)[1].rsplit('\n')
        print 'lista raw',lista
        lista=[float(i[15:]) for i in lista[18:21]]

        #img=NiftiImage(dir_img) 
        #lista=img.getVoxDims()
        time.sleep(1)
        comm='fsl5.0-fslstats '+dir_img+' -C'
        print comm
        textt=commands.getstatusoutput(comm)[1].rsplit(' ')
        print 'tt',textt
        print 'lis',lista
        cent=np.array([float(i)*d for i,d in zip(textt[:3],lista) if(i!='')])
        print 'cent',cent
        #t1 traslada a cero
        t1=cent[:]*-1
        print 't1',t1
        T1=self.genera_matriz(t1[0],t1[1],t1[2],0.,0.,0.)

        #rotacion con el cerebro centrado en el punto 0,0,0
        T2=self.genera_matriz(0.,0.,0.,da[0],da[1],da[2])

        #    
        t3=dp+cent
        T3=self.genera_matriz(t3[0],t3[1],t3[2],0.,0.,0.)
        T=np.dot(np.dot(T3,T2),T1)
        if save:
            self.write_mat(T,dir_out_mat)
        return T



    def genera_ruido(self,noiseDir):
        f = open(noiseDir,'r') 
        vec=[]
        salida=[]
        for fila in f.read().split('\n'):
            filv=[]
            filaRead=fila.split(' ')
            for j,col in enumerate(filaRead):
                #print float(col),
                if(j==0):
                    vec.append(int(col))
                    filv.append(int(col))
            filv.append(np.array([float(filaRead[1]),float(filaRead[2]),float(filaRead[3])]))
            filv.append(np.array([float(filaRead[4]),float(filaRead[5]),float(filaRead[6])]))
            salida.append(filv)    
        return vec,salida

    def guarda_vec(self,vector,dir_out='/home/arbey/Documentos/data_noise.nose'):
        file_=open('data_noise.nose','w')
        for i in vector:
            file_.writelines(str(i)+'\n')
        file_.close()
        comm='mv data_noise.nose '+dir_out
        os.system(comm)

    def orden(self,comm):
        os.system('echo '+comm)
        os.system(comm)
        
    def Img_noise(self,iin,fol_out, noiseDir):
        self.orden('rm -r '+fol_out+'im_split')
        self.orden('rm -r '+fol_out+'im_merge')

        self.orden('mkdir '+fol_out+'im_split')
        self.orden('mkdir '+fol_out+'im_merge')
        self.orden('fsl5.0-fslsplit '+iin+'  '+fol_out+'im_split/ -t')
        time.sleep(5)

        vec,vector=self.genera_ruido(noiseDir)
        cons=0
        for i in vector:
            print i
        
        for v in range(self.nVols):
            if(v in vec):
                iin=fol_out+'im_split/'+str(v).zfill(4)+'.nii.gz'
                iout=fol_out+'im_merge/'+str(v).zfill(4)+'.nii.gz'
                iref=iin
                matin=fol_out+'im_merge/'+str(v).zfill(4)+'.mat'
                print '------iin',iin
                T=self.Trasformacion(vector[cons][1],
                                vector[cons][2]*np.pi/180.,
                                iin,
                                str(v).zfill(4)+'.mat',
                                True)

                self.orden('mv '+str(v).zfill(4)+'.mat '+fol_out+'im_merge/'+str(v).zfill(4)+'.mat')
                matin=fol_out+'im_merge/'+str(v).zfill(4)+'.mat'
                self.orden('fsl5.0-flirt -in '+ iin+' -ref '+ iref +' -applyxfm -init  '+matin+' -o '+iout)
                cons+=1
            else:
                self.orden('mv '+fol_out+'im_split/'+str(v).zfill(4)+'.nii.gz'+' '+fol_out+'im_merge/'+str(v).zfill(4)+'.nii.gz')
        
        text=''
        for j in range(self.nVols):
            text=text+' '+fol_out+'im_merge/'+str(j).zfill(4)+'.nii.gz'
            
        self.orden('fsl5.0-fslmerge -t '+self.iout.replace('.nii.gz','')+' '+text)
        self.orden('rm -r '+fol_out+'im_split')
        for v in range(self.nVols):
            self.orden('rm '+fol_out+'im_merge/'+str(v).zfill(4)+'.nii.gz')
        
        #orden('rm -r '+fol_out+'im_merge')


#tem=Noise(iin ,fol_out, noiseDir,nVols)
print sys.argv
tem=Noise(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],int(sys.argv[5]))
tem.run()
