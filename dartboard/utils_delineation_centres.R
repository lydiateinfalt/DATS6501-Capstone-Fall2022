#!/usr/bin/env Rscript
# Description: Computes urban centres from urban raster
# Author: Clement Gorin
# Contact: gorinclem@gmail.com
# Version: 2022.09.01

# Packages
suppressMessages(if(!require('pacman')) install.packages('pacman', repos = 'https://cloud.r-project.org/'))
pacman::p_load(compiler, fst, future.apply, imager, matrixStats, memuse, optparse, raster, rgdal, tictoc)
options(warn = -1, future.globals.maxSize = (2048 * 1024^2))

# Parameters
arguments <- list(
  make_option('--density',   type = 'character', default = '',  help = 'Path to density raster'),
  make_option('--unlivable', type = 'character', default = '',  help = 'Path to unlivable raster'),
  make_option('--urban',     type = 'character', default = '',  help = 'Path to delineation raster'),
  make_option('--outdir',    type = 'character', default = '',  help = 'Path to output directory'),
  make_option('--tmpdir',    type = 'character', default = '',  help = 'Path to temporary directory'),
  make_option('--nboots',    type = 'integer',   default = 100, help = 'Number of bootstrapped counterfactual densities (default 100)'),
  make_option('--niter',     type = 'integer',   default = 1,   help = 'Number of iteration for the centres (default 1)'),
  make_option('--bandwidth', type = 'integer',   default = 15,  help = 'Kernel bandwidth in pixels (default 15)'),
  make_option('--quantile',  type = 'integer',   default = 95,  help = 'Quantile for threshold (default 95)'),
  make_option('--replace',   type = 'integer',   default = 1,   help = 'Bootstrap with replacement (default 1)'),
  make_option('--joinall',   type = 'integer',   default = 0,   help = 'Joins delineations up to [value] pixels apart (default 0)'),
  make_option('--joinunl',   type = 'integer',   default = 0,   help = 'Joins delineations up to [value] unlivable pixels apart (default 0)'),
  make_option('--filter',    type = 'integer',   default = 0,   help = 'Keeps delineations that are larger than [value] pixels (default 0)'),
  make_option('--workers',   type = 'integer',   default = -1,  help = 'Number of available centres (default -1 for all centres)'),
  make_option('--memory',    type = 'integer',   default = -1,  help = 'Available memory in GB (default -1 for all memory)'),
  make_option('--usedisk',   type = 'integer',   default = 1,   help = 'Forces writing bootstraps to the disk (default 1)'),
  make_option('--seed',      type = 'integer',   default = 1,   help = 'Bootstrap seed (default 1)')
)

params <- parse_args(OptionParser(usage = 'Computes urban delineations from raster', option_list = arguments))
params <- subset(params, names(params) != 'help')

# (!) Testing only --------------------------------------------------------
# setwd('~/Desktop/delineation_centre')
# # Interactive
# params <- modifyList(params, list(
#   density   = 'input/density.tif',
#   unlivable = 'input/unlivable.tif',
#   urban     = 'input/urban.tif',
#   outdir    = 'output',
#   tmpdir    = 'temporary'
#   ))
# -------------------------------------------------------------------------

# Checks directories
if(!dir.exists(params$outdir)) dir.create(params$outdir)
if(!dir.exists(params$tmpdir)) dir.create(params$tmpdir)
unlink(dir(params$tmpdir, pattern = '^boot_.*\\.fst$', full.names = T), recursive = T)

# Checks parameters
tests <- list(
  density   = file.exists,
  unlivable = file.exists,
  urban     = file.exists,
  outdir    = file.exists,
  tmpdir    = file.exists,
  nboots    = function(.) is_greater_than(., 0),
  niter     = function(.) is_greater_than(., 0),
  bandwidth = function(.) is_greater_than(., 1),
  quantile  = function(.) is_in(., 0:100),
  replace   = function(.) is_in(., 0:1),
  joinall   = function(.) is_weakly_greater_than(., 0),
  joinunl   = function(.) is_weakly_greater_than(., 0),
  filter    = function(.) is_weakly_greater_than(., 0),
  workers   = function(.) equals(., -1) | is_greater_than(., 0),
  memory    = function(.) equals(., -1) | is_greater_than(., 0),
  usedisk   = function(.) is_in(., 0:1),
  seed      = is.integer)

tests <- mapply(function(test, param) do.call(test, list(param)), tests, params)
if(sum(tests) != length(tests)) stop('Wrong argument(s): ', paste(names(tests)[which(!tests)], collapse = ', '), '\n')
rm(arguments, tests)

# Checks workers and memory
maxcor <- availableCores() - 1
maxmem <- round(Sys.meminfo()$totalram@size)
params$workers <- ifelse(params$workers == -1, maxcor, min(params$workers, maxcor))
params$memory  <- ifelse(params$memory  == -1, maxmem, min(params$memory,  maxmem))
rm(maxcor, maxmem)

# Prints parameters
cat('\nComputes urban centres from urban raster (version 2022.09.01)\n')
cat('\nParameters:', sprintf('- %-10s= %s', names(params), unlist(params)), sep = '\n')

# Sets up workers
cat('\nOperations:')
plan(multiprocess, workers = params$workers, gc = T)

# Functions ---------------------------------------------------------------

# Displays cimg
display <- cmpfun(function(cimg, discrete = F) {
  ebimg <- EBImage::as.Image(cimg)
  if(discrete) ebimg <- EBImage::colorLabels(ebimg, normalize = T)
  EBImage::display(ebimg, method = 'raster')
})

# Reads raster as cimg
read_foo <- cmpfun(function(file, livable = NULL) {
  image <- raster(file)
  image <- as.cimg(image, maxpixels = ncell(image))
  if(!is.null(livable)) {
    image <- pad(image, (nrow(livable) - nrow(image)), 'xy')
    image <- replace(image, !livable, 0)
  }
  return(image)
})

# Creates file names
filename_foo <- cmpfun(function(label, params) {
  filename <- sub('\\.csv$|\\.tif$', '', basename(params$density))
  filename <- file.path(params$outdir, paste0(filename, 'd', params$bandwidth, 'b', params$nboots, '_', label, '.tif'))
  return(filename)
})

# Writes cimg as raster
write_foo <- cmpfun(function(image, label, params, navalue = -1) {
  container <- raster(params$density) < 0
  image     <- crop.borders(image, nPix = ((nrow(image) - ncol(container)) / 2))
  image     <- setValues(container, c(image))
  image     <- mask(image, container)
  filename  <- filename_foo(label, params)
  writeRaster(image, filename, NAflag = navalue, overwrite = T)  
})

# Optimises computations
optimise_foo <- cmpfun(function(previous, params, memshr = 0.1) {
  nvalues    <- sum(previous > 0)
  bootsize   <- 8 * nvalues / 1024^3
  sliceindex <- ceiling(bootsize * params$nboots / (memshr * params$memory))
  sliceindex <- round(seq(0, nvalues, length.out = sliceindex + 1))
  usedisk    <- ifelse(params$usedisk, 1, as.integer(length(sliceindex) > 2))
  params     <- modifyList(params, list(sliceindex = sliceindex))
  return(params)
})

# Computes bi-squared kernel
kernel_foo <- cmpfun(function(bandwidth) {
  size     <- ifelse(bandwidth %% 2 == 0, bandwidth + 1, bandwidth)
  kernel   <- matrix(0, size, size)
  centre   <- ceiling(size / 2)
  distance <- sqrt((col(kernel) - centre)^2 + (row(kernel) - centre)^2)
  distance <- ifelse(distance <= bandwidth / 2, (1 - (distance / bandwidth * 2)^2)^2, 0)
  kernel   <- as.cimg(distance / sum(distance))
  return(kernel)
})

# Computes single bootstrap for centres
bootstrap_centres_foo <- cmpfun(function(density, previous, buffer, kernel, params) {
  indexes   <- previous + buffer
  subset    <- indexes > 0
  bootstrap <- ave(density[subset], indexes[subset], FUN=function(values) sample(values, replace = params$replace))
  bootstrap <- replace(indexes, subset, bootstrap)
  bootstrap <- convolve(bootstrap, kernel)
  bootstrap <- subset(bootstrap, previous > 0)
  return(bootstrap)
})

# Computes multiple bootstraps for centres
bootstraps_centres_foo <- cmpfun(function(density, previous, buffer, kernel, params) {
  if(params$usedisk) {
    bootstraps <- future_sapply(1:params$nboots, function(.) {
      bootstrap <- bootstrap_centres_foo(density, previous, buffer, kernel, params)
      file      <- tempfile('boot_', params$tmpdir, '.fst')
      write_fst(data.frame(bootstrap), file, compress = 0)
      gc()
      return(file)
    }, future.seed = params$seed)
  } else {
    # (!) Issue with future library on M1 version
    bootstraps <- future_replicate(params$nboots, bootstrap_centres_foo(density, previous, buffer, kernel, params), future.seed = params$seed)
  }
  return(bootstraps)
})

# Computes threshold
threshold_foo <- cmpfun(function(bootstraps, previous, params) {
  if(params$usedisk) {
    threshold <- lapply(head(seq(params$sliceindex), -1), function(i) {
      slice <- future_sapply(bootstraps, function(file) as.matrix(read_fst(file, from = params$sliceindex[i] + 1, to = params$sliceindex[i + 1])))
      slice <- rowQuantiles(slice, probs = (params$quantile / 100))
      gc()
      return(slice)
    })
    threshold <- do.call(c, threshold)
  } else {
    threshold <- rowQuantiles(bootstraps, probs = (params$quantile / 100))
  } 
  threshold <- replace(as.cimg(previous), previous > 0, threshold)
  return(threshold)
})

# Computes delineations
delineation_foo <- cmpfun(function(density, previous, threshold, kernel) {
  delineation <- convolve(density, kernel)
  delineation <- replace(delineation, previous == 0, 0)
  delineation <- as.cimg(delineation > threshold)
  return(delineation)
})

# Computes ranks
rank_foo <- cmpfun(function(identifier) {
  values     <- subset(identifier, identifier > 0)
  position   <- rank(-tabulate(values), ties = 'first')
  position   <- position[match(values, seq(max(values)))]
  identifier <- replace(identifier, identifier > 0, position)
  return(identifier)
})

# Computes identifiers
identifier_foo <- cmpfun(function(delineation, livable, params) {
  identifier <- delineation
  if(params$joinall > 0) {
    identifier <- identifier | (fill(delineation, params$joinall + 1) & !delineation) 
  }
  if(params$joinunl > 0) {
    identifier <- identifier | (fill(delineation, params$joinunl + 1) & !livable) 
  }
  identifier <- label(identifier, high_connectivity = T) + 1
  identifier <- replace(identifier, !delineation, 0)
  if(params$filter > 0) {
    filtered   <- seq(max(identifier))[tabulate(identifier) <= params$filter]
    identifier <- replace(identifier, identifier %in% filtered, 0)
  }
  identifier <- rank_foo(identifier)
  return(identifier)
})

# Urban centres -----------------------------------------------------------

tic('Runtime')

# Urban areas data
cat('\n- Computing urban centres: data...')
kernel   <- kernel_foo(params$bandwidth)
livable  <- read_foo(params$unlivable)
livable  <- replace(livable, px.na(livable), 1) == 0
livable  <- pad(livable, nPix = params$bandwidth, 'xy')
density  <- read_foo(params$density, livable)
density  <- replace(density, px.na(density), 0)
previous <- read_foo(params$urban, livable)
previous <- replace(previous, px.na(previous), 0)

for(iter in seq(params$niter)) {
  # First iteration is not indexed
  centrelab <- ifelse(iter == 1, '', as.character(iter))
 
  # Urban centres data
  cat('\n- Computing urban centres: data...')

  # Computes bootstrap buffer
  buffer <- convolve(previous, kernel) > 0
  buffer <- replace(label(buffer, high_connectivity = T) + max(previous), buffer == 0, 0)
  buffer <- replace(buffer, previous > 0 | !livable, 0)
  
  # Centres computations
  params      <- optimise_foo(previous, params)                                   ; cat(' bootstraps...')
  bootstraps  <- bootstraps_centres_foo(density, previous, buffer, kernel, params); cat(' thresholds...')
  threshold   <- threshold_foo(bootstraps, previous, params)                      ; cat(' delineations...')
  delineation <- delineation_foo(density, previous, threshold, kernel)            ; cat(' identifiers...')
  centres     <- identifier_foo(delineation, livable, params)                     ; cat(' saving')
  
  # Writes centres
  write_foo(threshold, sprintf('et%s', centrelab), params)
  write_foo(centres, sprintf('ce%s', centrelab), params, navalue = 0)
  if(params$usedisk) unlink(bootstraps, recursive = T)
  rm(buffer, bootstraps, threshold, delineation)
  
  # Updates reference
  previous <- centres
}

toc()