import numpy as np
import os
import sys
import subprocess
from astropy.time import Time


try:
    psr = sys.argv[1]
    freq = int(sys.argv[2])
except IndexError:
	print "I'm afraid I can't do that, Dave" % sys.argv[0]
	sys.exit(1)


#psr='B1929+10'
#freq=1


###READ IN TIMES FROM TIMESTAMP FILE###
timestamp = np.loadtxt(psr+'_PAvoltage.raw0.timestamp.B1.dat',unpack=True, usecols=(7,8,9,10,11,12,13,))

year,month,day,hour,minute,sec,fracsec = timestamp[0][0],timestamp[1][0],timestamp[2][0],timestamp[3][0],timestamp[4][0],timestamp[5][0],timestamp[6][0]


if month < 9.9:
	mon = '0'+str(int(month))
else:
	mon = str(int(month))



###DEFINE VALUES FOR DSPSR RUN###

if freq == 1:
	centerfreq = 322.667 #MHz
else:
	centerfreq = 607.667 #MHz

print(centerfreq)
ist = day+hour/24+minute/60/24+sec/3600/24
utc = ist - 5.5/24
utchour = int((utc - int(utc))*24)
if day < 9.9:
	utc_day = '0'+str(int(day))
else:
	utc_day = str(int(day))
if utchour < 9.9:
	utc_hour = '0'+str(utchour)
else:
	utc_hour = str(utchour)
utcmin = int(((utc - int(utc))*24 - utchour)*60)
if utcmin < 9.9:
	utc_min = '0'+str(utcmin)
else:
	utc_min = str(utcmin)	
utcsec = int((((utc - int(utc))*24 - utchour)*60 - utcmin)*60)
if utcsec < 9.9:
	utc_sec = '0'+str(utcsec+fracsec)
else:
	utc_sec = str(utcsec+fracsec)	
time = str(int(year))+'-'+mon+'-'+utc_day+'T'+utc_hour+':'+utc_min+':'+utc_sec
t = Time(time,format='isot',scale='utc')
mjd = int(t.mjd)


###offset is HH MM SS.SS in seconds from mjd in UTC###
sample_offset = utchour*3600 + utcmin*60 + utcsec + fracsec
print(sample_offset)

parfile = np.genfromtxt('/nanograv/projects/GMRT/parfiles/'+psr+'.par',usecols=(1),dtype=str)
coordinates = parfile[1]+parfile[2]
psrj = parfile[0]

###RUN DSPSR ON VOLTAGE FILE###

cmd='dspsr -set coord='+coordinates+' -f '+str(centerfreq)+' -b 1024 -B 33.333333 -m '+str(mjd)+' -N '+psr+' -C '+str(sample_offset)+' -O '+psr+'_'+str(freq)+'_voltage_'+str(mjd)+' -E /nanograv/projects/GMRT/parfiles/'+psr+'.par -F 32:D -UminX2 '+psr+'_PA_voltage.'+str(freq)+'.dat'

os.system(cmd)

###PIPE PSREDIT RESULTS AND READ 'EM IN###

cmd = 'psrstat -Q -c length '+psr+'_'+str(freq)+'_voltage_'+str(mjd)+'.ar' 
proc = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
out, err = proc.communicate()
length = out.strip().split()[1]


###MAKE INTENSITY HEADER###

filename = psr+'_PA_intensity.'+str(freq)+'.dat.gmrt_hdr'
file = open(filename,'w')
file.write('# DATA FILE HEADER #\n')
file.write('Site            : GMRT\n')
file.write('Observer        : FERMI\n')
file.write('Proposal        : TIMING\n')
file.write('Array Mode      : PA\n')
file.write('Observing Mode  : Search\n')
file.write('Date            : '+utc_day+'/'+mon+'/'+str(int(year))+'\n')
file.write('Num Antennas    : 13\n')
file.write('Antenna List    : C00 C01 C03 C04 C05 C06 C08 C09 C10 C11 C12 C13 C14\n')
file.write('Num Channels    : 512\n')
file.write('Channel width   : 0.065105\n')
if freq == 1: 
	file.write('Frequency Ch.1  : 306.000000\n')
else:
	file.write('Frequency Ch.1  : 591.000000\n')
file.write('Sampling Time   : 15.36\n')
file.write('Num bits/sample : 16\n')
file.write('Data Format     : integer binary, little endian\n')
file.write('Polarizations   : Total I\n')
file.write('MJD             : '+str(mjd)+'\n') 
file.write('UTC             : '+utc_hour+':'+utc_min+':'+str(utcsec+fracsec)+'\n')
file.write('Source          : '+psrj+'\n') 
file.write('Coordinates     : '+parfile[1]+', '+parfile[2]+'\n')
file.write('Coordinate Sys  : J2000\n')
file.write('Drift Rate      : 0.0, 0.0\n')
file.write('Obs. Length     : '+length+'\n')
file.write('Bad Channels    : 2:1-20,500-512\n')
file.write('Bit shift value : 1\n')
file.close()


os.system('ln -s '+psr+'_PA_intensity.'+str(freq)+'.dat '+psr+'_PA_intensity.'+str(freq)+'.dat.gmrt_dat')

cmd = 'dspsr -set coord='+coordinates+' -b 1024 -f '+str(centerfreq)+' -O '+psr+'_'+str(freq)+'_intensity'+' -E /nanograv/projects/GMRT/parfiles/'+psr+'.par '+psr+'_PA_intensity.'+str(freq)+'.dat.gmrt_dat'
#os.system(cmd)

print("---Done---")

