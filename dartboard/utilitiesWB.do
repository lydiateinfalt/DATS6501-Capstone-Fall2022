/* 
# !/usr/local/stata16
# Description: R utilities for Stata
# Author: Clement Gorin
# Contact: gorinclem@gmail.com
# Version: 2022.08.22
*/

/* Globals: PATH TO BE ADAPTED TO LOCAL ENVIRONMENT */
global Rscript "C:/Program Files/R/R-4.0.5/bin/x64/Rscript.exe"
global utils "C:/Dropbox/apiffy/ScriptsCG"

* Wrapper for utils_delineation_raster.R
cap: program drop delineation_raster
program define delineation_raster
	syntax, [density(string) unlivable(string) outdir(string) tmpdir(string) nboots(integer 100) niter(integer 1) bandwidth(integer 15) quantile(integer 95) replace(integer 1) joinall(integer 0) joinunl(integer 0) filter(integer 0) workers(integer -1) memory(integer -1) seed(integer 1) help pause]
	if "pause"!="" local pause "& `pause'"
	if "`help'" == "help" {
		!"${Rscript}" "${utils}/utils_delineation_raster.R" --help & pause
	}
	else {
		!"${Rscript}" "${utils}/utils_delineation_raster.R" --density="`density'" --unlivable="`unlivable'" --outdir="`outdir'" --tmpdir="`tmpdir'" --nboots=`nboots' --niter=`niter' --bandwidth=`bandwidth' --quantile=`quantile' --replace=`replace' --joinall=`joinall' --joinunl=`joinunl' --filter=`filter' --workers=`workers' --memory=`memory' --seed=`seed' `pause'
	}
end

* Wrapper for utils_delineation_centres.R
cap: program drop delineation_centres
program define delineation_centres
	syntax, [density(string) unlivable(string) urban(string) outdir(string) tmpdir(string) nboots(integer 100) niter(integer 1) bandwidth(integer 15) quantile(integer 95) replace(integer 1) joinall(integer 0) joinunl(integer 0) filter(integer 0) workers(integer -1) memory(integer -1) usedisk(integer 1) seed(integer 1) help pause]
	if "pause"!="" local pause "& `pause'"
	if "`help'" == "help" {
		!"${Rscript}" "${utils}/utils_delineation_centres.R" --help & pause
	}
	else {
		!"${Rscript}" "${utils}/utils_delineation_centres.R" --density="`density'" --unlivable="`unlivable'" --urban="`urban'" --outdir="`outdir'" --tmpdir="`tmpdir'" --nboots=`nboots' --niter=`niter' --bandwidth=`bandwidth' --quantile=`quantile' --replace=`replace' --joinall=`joinall' --joinunl=`joinunl' --filter=`filter' --workers=`workers' --memory=`memory' --usedisk=`usedisk' --seed=`seed' `pause'
	}
end

* Wrapper for utils_delineation_building.R
cap: program drop delineation_building
program define delineation_building
	syntax, [density(string) reference(string) unlivable(string) outdir(string) tmpdir(string) nboots(integer 100) niter(integer 1) bandwidth(integer 15) quantile(integer 95) replace(integer 1) joinall(integer 0) joinunl(integer 0) filter(integer 0) workers(integer -1) memory(integer -1) seed(integer 1) help pause]
	if "pause"!="" local pause "& `pause'"
	if "`help'" == "help" {
		!"${Rscript}" utils_delineation_building.R --help & pause
	}
	else {
		!"${Rscript}" utils_delineation_building.R --density="`density'" --reference="`reference'" --unlivable="`unlivable'" --outdir="`outdir'" --tmpdir="`tmpdir'" --nboots=`nboots' --niter=`niter' --bandwidth=`bandwidth' --quantile=`quantile' --replace=`replace' --joinall=`joinall' --joinunl=`joinunl' --filter=`filter'  --workers=`workers' --seed=`seed' `pause'
	}
end

* Wrapper for utils_dta2tif.R
cap: program drop dta2tif
program define dta2tif
	syntax, [srcval(string) srcids(string) outdir(string) idvar(string) nocolour(string) help pause]
	if "pause"!="" local pause "& `pause'"
	if "`help'"=="help" {
		!"${Rscript}" "${utils}/utils_dta2tif.R" --help & pause
	}
	else {
		!"${Rscript}" "${utils}/utils_dta2tif.R" --srcval="`srcval'" --srcids="`srcids'" --outdir="`outdir'" --idvar="`idvar'" --nocolour="`nocolour'" `pause'
	}
end

* Wrapper for utils_tif2dta.R
cap: program drop tif2dta
program define tif2dta
	syntax, [srcval(string) srcids(string) outdir(string) help pause]
	if "pause"!="" local pause "& `pause'"
	if "`help'"=="help" {
		!"${Rscript}" "${utils}/utils_tif2dta.R" --help & pause
	}
	else {
		!"${Rscript}" "${utils}/utils_tif2dta.R" --srcval="`srcval'" --srcids="`srcids'" --outdir="`outdir'" `pause'
	}
end

* Wrapper for utils_unlivable.R
cap: program drop unlivable
program define unlivable
	syntax, [density(string) outdir(string) label(string) crit1(string) crit2(string) crit3(string) crit4(string) crit5(string) quant1(real 0.99) quant2(real 0.99) quant3(real 0.99) quant4(real 0.99) quant5(real 0.99) writecrits(integer 1) help pause]
	if "pause"!="" local pause "& `pause'"
	if "`help'"=="help" {
		!"${Rscript}" "${utils}/utils_unlivable.R" --help & pause
	}
	else {
		!"${Rscript}" "${utils}/utils_unlivable.R" --density="`density'" --outdir="`outdir'" --label="`label'" --crit1="`crit1'" --crit2="`crit2'" --crit3="`crit3'" --crit4="`crit4'" --crit5="`crit5'" --quant1=`quant1' --quant2=`quant2' --quant3=`quant3' --quant4=`quant4' --quant5=`quant5' --writecrits=`writecrits' `pause'
	}
end
