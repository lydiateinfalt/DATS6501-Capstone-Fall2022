#!/usr/bin/env Rscript
# Description: Converts a raster to a Stata dataset
# Author: Clement Gorin
# Contact: gorinclem@gmail.com
# Date: 2021.12.10

# Packages
suppressMessages(if(!require('pacman')) install.packages('pacman', repos = 'https://cloud.r-project.org/'))
pacman::p_load(data.table, optparse, raster, readstata13)

# Parameters
arguments <- list(
  make_option('--srcval', type='character', default='', help='Input raster of values'),
  make_option('--srcids', type='character', default='', help='Input raster of identifiers'),
  make_option('--outdir', type='character', default='', help='Output directory')
  )
params <- parse_args(OptionParser(usage='Converts a raster to a Stata dataset', option_list=arguments))

# (!) Testing only --------------------------------------------------------
# params <- modifyList(params, list(
#   srcval='~/Desktop/mdg_upo15.tif',
#   srcids='~/Desktop/mdg_ids.tif',
#   outdir='~/Desktop'))
# -------------------------------------------------------------------------

# Prints arguments
cat('\nConverts a raster to a Stata dataset (version 2021.12.10)\nParameters:', sprintf('--%-6s = %s', names(params), unlist(params)), sep='\n')

# Tests arguments
if(!dir.exists(params$outdir)) dir.create(params$outdir)
test <- sapply(params[1:3], file.exists)
if (sum(test) != length(test)) stop ('Wrong argument(s): ', paste(names(test)[which(!test)], collapse=', '), '\n')

# Functions ---------------------------------------------------------------

# Converts a raster to a Stata dataset
tif2dta <- function(params) {
  cat('Reading data\n')
  id    <- raster(params$srcids)
  value <- raster(params$srcval)
  cat('Matching rasters\n')
  matched <- data.table(id=getValues(id), value=getValues(value))
  matched <- matched[!is.na(id)][order(id)]
  # Check
  if(all(is.nan(matched$value)) | all(is.na(matched$value))) {
    stop("Matched data contains only NA or NaN values.")
  }
  cat('Writing dataset\n')
  fileName <- gsub('\\.tif$', '', basename(params$srcval))
  save.dta13(matched, file.path(params$outdir, paste0(fileName, '.dta')))
  cat('Done\n')
}

tif2dta(params)
