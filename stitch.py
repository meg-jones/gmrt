#! /usr/bin/env python

import numpy as np
import sys
import os
from pylab import *
import scipy as sy

pname=np.loadtxt('psrs.txt', unpack=True, usecols=(0,), dtype='str')


loc = 

#psrs = pulsar list for those in that directory

for i in range(0,len(pname)):
	file1 = '/nanograv/projects/GMRT/25_049_'+loc+'.node49'
	file2 = '/nanograv/projects/GMRT/25_049_'+loc+'.node57'
	outdir = '/nanograv/projects/GMRT/'+loc
	filename = pname+'_PAvoltage.raw0'
	nint_pa = 1

	timestamp = np.loadtxt(file1+'/'+pname+'_PAvoltage.raw0.timestamp.B1.dat', unpack=True, usecols=(0,))	
	obs_length = len(timestamp)

	#Run polarization stitching
	os.system('mpirun -ppn 2 ./pols2_read_dual_polar.4bit '+file2+' '+file2+' '+file1+' '+file1+' '+filename+' '+outdir+' '+str(obs_length)+' '+str(nint_pa))


	#Rename output files
	os.system('cd '+outdir)
	out1 = pname+'_PA_intensity.1.dat'
	out2 = pname+'_PA_intensity.2.dat'
	out3 = pname+'_PA_voltage.1.dat'
	out4 = pname+'_PA_voltage.2.dat'

	os.system('mv PA_intensity.1.dat '+out1)
	os.system('mv PA_intensity.2.dat '+out2)
	os.system('mv PA_voltage.1.dat '+out3)
	os.system('mv PA_voltage.2.dat '+out4)
	
	os.system('cd ..')




