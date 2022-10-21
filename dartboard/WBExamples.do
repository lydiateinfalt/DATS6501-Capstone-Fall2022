#delimit;

set more off;
clear all ;

do C:/dropbox/artwb/code/ScriptsCG/utilitiesWB.do; /* wrapper for utilities to be usable from stata, to run before any code */

/******************** creation of the rasters for unlivable pixels */

unlivable, density("`Sources'/xx.tif") outdir("`Rasters'") label("unlxx")
crit1("`Sources'/wat.tif") crit2("`Sources'/slo.tif") crit3("`Sources'/ele.tif") crit4("`Sources'/des.tif") 
quant1(1) quant2(0.99) quant3(0.99) quant4(1) ;

/* density(""`Sources'/xx.tif"): tif for the variable used to draw the delineation (`Sources' is the directory where source data is).
outdir: directory where the raster for unlivable pixels will be stored 
label: how the rasters produced will be named
crit1 to crit3 or 4: rasters with data for criteria considered as unlivable (water, slope,etc)
quant1 to quant 3 or 4: criteria: 99th percentile or 1 if 0/1 criteria */


/**************** computation of the delineations */

delineation_raster, density("`Sources'/xx.tif") unlivable("`Rasters'/unlxx.tif") 
outdir("`Delineations'")
joinall(1) joinunl(2) filter(1)
workers(52)
tmpdir("$DirTemp") nboots(nb) bandwidth(bd) ;

/* density(""`Sources'/xx.tif"): tif for the variable used to draw the delineation, the same as for the unlivable utility
unlivable: directory where the unlivable raster has been saved, cf unlivable utility.
outdir: directory where the delineation raster will be stored
joinall(n): fills holes of n pixels within a delineation
joinunl(n): filles holes of n unlivable pixels within a delineation
filter(n) do not consider urban areas of less than n pixel as an urban area
workers(n): manually reduce the number of cores that can be used
tmpdir: directory where the boostrap files are stored (cleaned each time a new delineation is drawned 
nboots(n): number of bootstraps (3000? check the code with a few hundreds first)
bandwidth(n): bandwidth used to smooth the data.*/

/***************** tests of the sources rasters and creation of a pixel identifier stored in raster yyids.tif */ 

checkRasters, srcdir("`Sources'") srcref("`Sources'/xx.tif") exclude("NO_DATA|urban|dbu");

/* srcdir("`Sources'") directory where the rasters to be checked are located
srcref("`Sources'/xx.tif"): reference raster supposed to be the 'good' one, to which all other ones are comapred 
exclude: rasters with some string chains in their name */

/***************** conversion of a tif into a dta data set */ 

tif2dta, srcval("`Sources'/xx.tif") srcids("`Sources'/yyids.tif") outdir("`Stata'")  ;

/* srcval: raster to be converted
srcids: pixel identifiers
outdir: directory where the dta file is stored. */


