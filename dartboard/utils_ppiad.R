#!/usr/bin/env Rscript
# Description: Computes ppiad
# Author: Clement Gorin
# Contact: gorinclem@gmail.com
# Version: 2021.11.23

# Packages
suppressMessages(if(!require('pacman')) install.packages('pacman', repos = 'https://cloud.r-project.org/'))
pacman::p_load(data.table, dplyr, magrittr, optparse, raster, readstata13, sf, stringr, tictoc)

# Parameters
arguments <- list(
  make_option('--srcids',   type = 'character', default = '',  help = 'Path to identifier raster'),
  make_option('--srcpop',   type = 'character', default = '',  help = 'Path to the population raster file'),
  make_option('--srcads',   type = 'character', default = '',  help = 'Path to the names vector file'),
  make_option('--outfile',  type = 'character', default = '',  help = 'Path to output Stata dataset'),
  make_option('--cleanad',  type = 'integer',   default = 1,   help = 'Indicates whether namead should be cleaned')
)

params <- parse_args(OptionParser(usage = 'Computes ppiad', option_list = arguments))
params <- subset(params, names(params) != 'help')

# (!) Testing only --------------------------------------------------------
# # Parameters
# params <- modifyList(params, list(
#   srcids  = '~/Dropbox/research/artWB/data/sdn/sdn_ids.tif',
#   srcpop  = '~/Dropbox/research/artWB/data/sdn/sdn_gpo.tif',
#   srcads  = '~/Dropbox/research/artWB/data/sdn/sdn_ad.gpkg',
#   outfile = '~/Desktop/sdn_ppiad.dta'
#   ))
# # Command line
# cat(paste(c('Rscript', '~/Dropbox/research/utilities/utils_ppiad.R', paste0('--', names(params), '=', params)), collapse =  ' '))
# -------------------------------------------------------------------------

# Checks parameters
tests <- list(
  srcids = file.exists,
  srcpop = file.exists,
  srcads = file.exists,
  outfile = function(.) file.exists(dirname(.)),
  cleanad = function(.) is_in(., 0:1))

tests <- mapply(function(test, param) do.call(test, list(param)), tests, params)
if(sum(tests) != length(tests)) stop('Wrong argument(s): ', paste(names(tests)[which(!tests)], collapse = ', '), '\n')
rm(arguments, tests)

# Prints parameters
cat('\nComputes ppiad (version 2021.11.23)\n')
cat('\nParameters:', sprintf('- %-8s= %s', names(params), unlist(params)), sep = '\n')

# Functions ---------------------------------------------------------------

# Removes special characters
cleanad <- function(namead) {
  namead <- namead %>%
    str_replace_all("'", "@") %>%
    iconv("UTF-8", "ASCII", "#") %>%
    str_remove_all("\\^|'|`") %>%
    str_remove_all('"|#') %>%
    str_remove_all('^\\s+|\\s+$') %>%
    str_replace_all('\\s+', ' ') %>%
    str_replace_all("@", "'")
  return(namead)
}

# Computations ------------------------------------------------------------

tic('Runtime')
cat('\nOperations:')

# Loads data
cat('\n- Loads data')
ids <- raster(params$srcids)
pop <- raster(params$srcpop)
ads <- st_read(params$srcads, quiet=T)

# Cleans ad
ads <- dplyr::select(ads, -id)
ads <- st_transform(ads, proj4string(pop))
ads <- filter(ads, typead %in% c('city', 'town', 'village', 'hamlet'))
if(params$cleanad) {
  ads <- mutate(ads, namead=cleanad(namead))
}

# Extracts ids
cat('\n- Extracts ids')
ads$pi <- extract(ids, as(ads, 'Spatial'))

# Buffers at selected distances
cat('\n- Computes buffers')
ads <- ads %>%
  group_by(typead) %>%
  group_split() %>%
  setNames(unique(ads$typead))

buffers <- data.frame(
  typead = c('city', 'town', 'village', 'hamlet'),
  buffer = c(10e3, 5e3, 2e3, 2e3)
)
buffers <- buffers$buffer[match(names(ads), buffers$typead)]

ads <- Map(function(ad, buffer) st_buffer(ad, buffer), ads, buffers)
ads <- do.call(rbind, ads)

# Population points
pop <- st_as_sf(rasterToPoints(pop, spatial=T))
pop <- rename_at(pop, vars(-contains("geometry")), function(varname) str_c(str_remove(varname, '^[a-z]{3}(1k)?_'), 'ad'))
  
# Aggregate populations
cat('\n- Computes populations')
ppiad <- st_join(pop, ads)
ppiad <- ppiad %>%
  filter(!is.na(pi)) %>%
  st_drop_geometry()
ppiad <- ppiad %>%
  group_by(pi, typead, namead) %>%
  summarise_all(function(var) round(sum(var, na.rm=T)))
ppiad <- data.table(ppiad)
ppiad <- ppiad[order(ppiad[[ncol(ppiad)]], decreasing=T)] # Orders by last variable

cat('\n- Saves data\n\n')
save.dta13(ppiad, params$outfile)

toc()