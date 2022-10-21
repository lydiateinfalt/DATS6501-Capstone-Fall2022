#!/usr/bin/env Rscript
# Description: Computes non-buildable area for the WorldBank project
# Author: Clement Gorin
# Contact: gorinclem@gmail.com
# Version: 2022.02.11

suppressMessages(if(!require('pacman')) install.packages('pacman', repos = 'https://cloud.r-project.org/'))
pacman::p_load(dplyr, optparse, sf, stringr, raster)

# Parameters
arguments <- list(
  make_option('--density',    type = 'character', default = '',          help = 'Path to density raster'),
  make_option('--outdir',     type = 'character', default = '',          help = 'Path to output raster'),
  make_option('--label',      type = 'character', default = 'unlivable', help = 'Output label'),
  make_option('--crit1',      type = 'character', default = '',          help = 'Path to criterion raster 1'),
  make_option('--crit2',      type = 'character', default = '',          help = '-- 2'),
  make_option('--crit3',      type = 'character', default = '',          help = '-- 3'),
  make_option('--crit4',      type = 'character', default = '',          help = '-- 4'),
  make_option('--crit5',      type = 'character', default = '',          help = '-- 5'),
  make_option('--quant1',     type = 'numeric',   default = .99,         help = 'Quantile threshold for criterion 1'),
  make_option('--quant2',     type = 'numeric',   default = .99,         help = '-- 2'),
  make_option('--quant3',     type = 'numeric',   default = .99,         help = '-- 3'),
  make_option('--quant4',     type = 'numeric',   default = .99,         help = '-- 4'),
  make_option('--quant5',     type = 'numeric',   default = .99,         help = '-- 5'),
  make_option('--writecrits', type = 'numeric',   default = 1,           help = 'Writes intermediate rasters'))

params <- parse_args(OptionParser(usage='Computes unlivable areas', option_list=arguments))
params <- subset(params, names(params) != 'help')
ncrits <- params[str_detect(names(params), 'crit\\d')] != ''
params <- params[c(rep(T, 3), ncrits, ncrits)]

# Prints arguments
cat('\nComputes unlivable areas (version 2022.02.11)\nParameters:', sprintf('--%-10s = %s', names(params), unlist(params)), sep='\n')

# Checks arguments
if(!dir.exists(params$outdir)) dir.create(params$outdir)
test <- sapply(params[str_detect(names(params), "density|outdir|crit\\d")], file.exists)
if (sum(test) != length(test)) stop ('Wrong argument(s): ', paste(names(test)[which(!test)], collapse = ', '), '\n')
rm(arguments, test)

# Functions ---------------------------------------------------------------

compute_mask <- function(file, quant, density, params) {
  crit <- raster(file)
  nval <- length(unique(crit[!is.na(crit)])) # Number of unique values
  if(nval > 1) {
    nodens <- mask(crit, density > 0, maskvalue=0, updatevalue = NA)
    crit   <- crit >= quantile(nodens, quant, na.rm = T)
  } else { # If the raster has one value, everything is livable
    crit[!is.na(crit)] <- 0
  }
  if(params$writecrits) {
    outfile <- file.path(params$outdir, str_c(params$label, "_", names(file), '.tif'))
    writeRaster(crit, outfile, overwrite = T) 
  }
  return(crit)
}

# Data --------------------------------------------------------------------

cat('\nLoading data\n')
density <- raster(params$density)
files   <- unlist(params[str_detect(names(params), 'crit\\d')])
quants  <- unlist(params[str_detect(names(params), 'quant\\d')])

# Computation
cat('Computing unlivable areas\n')
crits     <- lapply(seq(files), function(i) compute_mask(files[i], quants[i], density, params))
unlivable <- Reduce('+', crits) > 0

cat('Saving files\n')
writeRaster(unlivable, file.path(params$outdir, str_c(params$label, "_all", '.tif')), overwrite = T)

cat('Done\n')

# (!) Testing only --------------------------------------------------------
# setwd('~/Dropbox/research/artWB/data/ben')
# params <- modifyList(params, list(
#   density    = 'ben1k_gpo.tif',
#   label      = 'test',
#   outdir     = '~/Desktop',
#   crit1      = 'ben1k_wat.tif',
#   crit2      = 'ben1k_slo.tif',
#   quant1     = 1,
#   quant2     = .99,
#   writecrits = 1
# ))
# -------------------------------------------------------------------------