id=$1

L8_all=(LC80130332013145LGN00 
LC80140332013104LGN01 
LC80140332013200LGN00 
LC80140332014299LGN00 
LC80150402013175LGN00 
LC80150402013207LGN00  
LC80150402013239LGN00  
LC80150402014002LGN00  
LC80150402014018LGN00  
LC80150402014114LGN00  
LC80150402014210LGN00  
LC80150402014258LGN00 
LC80150402014290LGN00  
LC80160382013134LGN03  
LC80160382013150LGN00  
LC80160382013166LGN04  
LC80160382013246LGN00  
LC80160382013278LGN00  
LC80160382014089LGN00  
LC80160382014137LGN00  
LC80160382014185LGN00  
LC80160382014233LGN00  
LC80160382014265LGN00  
LC80160392013134LGN03  
LC80160392013198LGN00  
LC80160392014041LGN00  
LC80240272013158LGN00  
LC80240272014225LGN00  
LC80240402013110LGN01  
LC80240402013142LGN01  
LC80240402013158LGN00  
LC80240402013190LGN00  
LC80240402013302LGN00  
LC80240402014017LGN00  
LC80240402014113LGN00  
LC80240402014289LGN00  
LC80410372013101LGN01  
LC80410372013133LGN01  
LC80410372013149LGN00  
LC80410372013181LGN00  
LC80410372014072LGN00  
LC80410372014104LGN00  
LC80410372014136LGN00  
LC80160302013166LGN04  
LC80160302013262LGN00  
LC80160302014153LGN00  
LC80160302014185LGN00  
LC80170302013237LGN00  
LC80170302013285LGN00  
LC80170302014144LGN00  
LC80170302014192LGN00 
LC80170302014272LGN00  
LC80200292013226LGN00  ) # all ids

ids_4=(LC80140332014299LGN00 
LC80150402014290LGN00 
LC80160382014265LGN00 
LC80240402014289LGN00 
LC80170302014272LGN00) # missing wgrib

ids_6=(
LC80160382013166LGN04 
)  # interpolation error (array of sample points is empty), narr, merra
# this is the modtran output
# ******* ERROR >>>>>>  SETDIS--beam angle=computational angle; change NSTR
 
ids_8=(LC80140332014299LGN00 
LC80160302014153LGN00
LC80160302013166LGN04
LC80170302014272LGN00) # modeled radiance is a nan (merra)

# LC80150402013175LGN00
#******* WARNING >>>>>>  UPBEAM--SGECO SAYS MATRIX NEAR SINGULAR

#LC80410372014104LGN00
# Traceback (most recent call last):
#  File "./buoy-calib", line 41, in <module>
#    cc.calc_all()
#  File "/cis/ugrad/nid4986/Buoy_Calibration/bin/BuoyCalib.py", line 164, in calc_all
#    self.calculate_buoy_information()
#  File "/cis/ugrad/nid4986/Buoy_Calibration/bin/BuoyCalib.py", line 307, in calculate_buoy_information
#    temp, pres, atemp, dewp = buoy_data.find_skin_temp(self, unzipped_file, depths[urls.index(url)])
#  File "/cis/ugrad/nid4986/Buoy_Calibration/bin/buoy_data.py", line 292, in find_skin_temp
#    T_zt = float(data[t][14])    # temperature data from closest hour
# IndexError: index 19 is out of bounds for axis 0 with size 4



L8_wo_wgrib=(LC80130332013145LGN00 
LC80140332013104LGN01 
LC80140332013200LGN00  
LC80150402013175LGN00 
LC80150402013207LGN00  
LC80150402013239LGN00  
LC80150402014002LGN00  
LC80150402014018LGN00  
LC80150402014114LGN00  
LC80150402014210LGN00  
LC80150402014258LGN00   
LC80160382013134LGN03  
LC80160382013150LGN00  
LC80160382013166LGN04  
LC80160382013246LGN00  
LC80160382013278LGN00
LC80160382014089LGN00  
LC80160382014137LGN00  
LC80160382014185LGN00  
LC80160382014233LGN00    
LC80160392013134LGN03  
LC80160392013198LGN00  
LC80160392014041LGN00   
LC80160302013166LGN04  
LC80160302013262LGN00  
LC80160302014153LGN00 
LC80160302014185LGN00  
LC80170302013237LGN00  
LC80170302013285LGN00  
LC80170302014144LGN00  
LC80170302014192LGN00   
LC80200292013226LGN00
LC80240272013158LGN00  
LC80240272014225LGN00  
LC80240402013110LGN01  
LC80240402013142LGN01  
LC80240402013158LGN00  
LC80240402013190LGN00  
LC80240402013302LGN00  
LC80240402014017LGN00  
LC80240402014113LGN00  
LC80410372013101LGN01  
LC80410372013133LGN01  
LC80410372013149LGN00  
LC80410372013181LGN00  
LC80410372014072LGN00  
LC80410372014104LGN00  
LC80410372014136LGN00 )

landsat_7=(
LE70160382012364EDC00
LE70160382012348EDC00
LE70160382012332EDC00
LE70160382012268EDC00 )

landsat_5=(
LT50410372011240PAC01
LT50410372011144PAC01
LT50410372011096PAC01
LT50410372011064PAC01
LT50410372011048PAC01
)

for i in "${L8_wo_wgrib[@]}"
do 
   echo $i
   ./buoy-calib $i -r
   echo
done
