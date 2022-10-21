#!/usr/bin/env Rscript
# Description: Checks rasters for the WorldBank project
# Author: Clement Gorin
# Contact: gorinclem@gmail.com
# Date: 2021.12.09

# Packages
pacman::p_load(future.apply, optparse, raster, stringr)

# Parallel
options(scipen = 999)
plan(multiprocess, workers=availableCores() -1, .cleanup = T)

# Parameters
arguments <- list(
  make_option('--srcdir',  type='character', default='', help='Path to raster directory'),
  make_option('--srcref',  type='character', default='', help='Path to reference raster'),
  make_option('--exclude', type='character', default='', help='Regular expression of files to exclude')
)
params <- parse_args(OptionParser(usage='Checks rasters information', option_list = arguments))

# (!) Testing only --------------------------------------------------------
# params <- modifyList(params, list(
#   srcdir="~/Dropbox/research/artWB/data/ben",
#   srcref="~/Dropbox/research/artWB/data/ben/ben1k_gpo.tif",
#   exclude="urban|no_data"
# ))
# -------------------------------------------------------------------------

# Prints arguments
cat('\nChecks raster for the WolrdBank project (version 2021.12.09)\nParameters:', sprintf('--%-7s = %s', names(params), unlist(params)), sep='\n')

# Tests arguments
test <- sapply(params[str_detect(names(params), "src")], file.exists)
if(sum(test) != length(test)) stop('Wrong argument(s): ', paste(names(test)[which(!test)], collapse = ', '), '\n')

# Identifiers -------------------------------------------------------------

cat('\nComputing identifiers\n')
ref  <- raster(params$srcref)
vals <- getValues(ref)
vals <- replace(vals, !is.na(vals), 1:sum(!is.na(vals)))
ids  <- setValues(raster(ref), vals)
ids  <- setNames(ids, "ids")
out  <- file.path(dirname(params$srcref), paste0(sub("_.*", "", basename(params$srcref)), "_ids.tif"))
writeRaster(ids, out, datatype = "INT4U", overwrite = T)
rm(vals)

# Data --------------------------------------------------------------------

cat('\nReading data\n')
files <- dir(params$srcdir, pattern="\\.tif$", full.names=T)
pat   <- ifelse(nchar(params$exclude), str_c(basename(params$srcref), params$exclude, sep='|'), basename(params$srcref)) 
files <- str_subset(files, pat, negate=T)
rsts  <- setNames(lapply(files, raster), str_remove(basename(files), "\\.tif"))

# Tests -------------------------------------------------------------------

# Spatial information
cat('\nChecking spatial information (TRUE indicates compatibility with the reference raster)\n\n')
exts <- sapply(rsts, function(rst) extent(rst) == extent(ids))
dims <- sapply(rsts, function(rst) all(dim(rst) == dim(ids)))
crss <- sapply(rsts, function(rst) projection(rst) == projection(ids))
ress <- sapply(rsts, function(rst) all(res(rst) == res(ids)))
orig <- sapply(rsts, function(rst) all(origin(rst) == origin(ids)))
diag <- cbind(extent = exts, dimensions = dims, crs = crss, resolution = ress, origin = orig)
print(diag)

# Values: Missing  and non-missing
cat('\nChecking pixel values\n')
cat(' - Difference 1: Non-missing pixels in the raster that are missing in the reference raster\n')
cat(' - Difference 2: Missing pixels in the raster that are non-missing in the reference raster\n')
cat(' - Share in %\n\n')
naref  <- is.na(ids)
pxdif1 <- future_sapply(rsts, function(rst) cellStats(!is.na(rst) & naref,  sum), future.seed = T) # !NA in rst NA in ids
pxdif2 <- future_sapply(rsts, function(rst) cellStats(is.na(rst)  & !naref, sum), future.seed = T) # NA in rst !NA in ids
diag   <- data.frame(
  difference1 = pxdif1, 
  difference2 = pxdif2, 
  share1 = (pxdif1 / ncell(ids) * 100), 
  share2 = (pxdif2 / ncell(ids) * 100))
print(round(diag, 4))

# Descriptive statistics
cat("\nComputing descriptive statistics\n")
ref    <- setNames(list(ref), basename(params$srcref))
rsts   <- c(ref, rsts)
mins   <- future_sapply(rsts, function(rst) suppressWarnings(cellStats(rst, min)), future.seed = T)
means  <- future_sapply(rsts, function(rst) suppressWarnings(cellStats(rst, mean)), future.seed = T)
maxs   <- future_sapply(rsts, function(rst) suppressWarnings(cellStats(rst, max)), future.seed = T)
quants <- future_sapply(rsts, function(rst) suppressWarnings(quantile(rst)), future.seed = T)
quants <- setNames(data.frame(t(quants)), str_c("quantile ", c(0, 25, 50, 75, 100)))
diag   <- cbind(data.frame(min = mins, mean = means, max = maxs), quants)
print(round(diag, 4))

print(str_c("Contains a single value: ", str_c(rownames(diag)[diag$min == diag$max], collapse= ", ")))

# Corrects rasters
cat("\nCorrecting slope raster\n")
slo <- rsts[[str_which(names(rsts), "_slo$")]]
slo <- replace(slo, slo < 0, 0)
writeRaster(slo, files[str_which(files, "slo\\.tif$")], overwrite = T)

cat("\nCorrecting elevation raster\n")
ele <- rsts[[str_which(names(rsts), "_ele$")]]
ele <- replace(ele, ele < 0, 0)
writeRaster(ele, files[str_which(files, "ele\\.tif$")], overwrite = T)

cat('\nDone\n')