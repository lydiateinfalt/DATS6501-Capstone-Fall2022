#!/usr/bin/env Rscript
# Description: Converts a Stata dataset to a raster
# Author: Clement Gorin
# Contact: gorin@gate.cnrs.fr
# Date: 2020/10/08

# Packages
pacman::p_load(optparse, data.table, raster, readstata13, stringr, xml2)

# Parameters
arguments <- list(
  make_option('--srcval',   type='character', default='',   help='Input Stata dataset'),
  make_option('--srcids',   type='character', default='',   help='Input raster of identifiers'),
  make_option('--outdir',   type='character', default='',   help='Output directory'),
  make_option('--idvar',    type='character', default='id', help='Identifier variable'),
  make_option('--nocolour', type='character', default='',   help='Pattern for modality without colour')
  )
params <- parse_args(OptionParser(usage='Converts a Stata dataset to a raster', option_list=arguments))

# Prints arguments
cat('\nConverts a Stata dataset to raster(s) (version 20/11/13)\nParameters:', sprintf('--%-8s = %s', names(params), unlist(params)), sep='\n')

# Default strings
params$nocolour <- ifelse(nchar(params$nocolour) == 0, '(?!.*)', params$nocolour)

# Tests arguments
if(!dir.exists(params$outdir)) dir.create(params$outdir)
t      <- new.env()
t$test <- sapply(params[1:3], file.exists)
if(sum(t$test) != length(t$test)) stop ('Wrong argument(s): ', paste(names(t$test)[which(!t$test)], collapse=', '), '\n')
if(!(params$idvar %in% names(read.dta13(params$srcval, select.rows=1)))) stop('Wrong argument: idvar \n')

# Functions ---------------------------------------------------------------

# Creates QGIS style file
make_qml <- function(file=NULL, identifier, colour, category, alpha) {
  colour  <- str_to_lower(str_remove(colour, "FF$")) # Removes FF at the end for QGIS compatibility
  style   <- read_xml("<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'><qgis version='3.10.3-A Coruña' hasScaleBasedVisibilityFlag='0' minScale='1e+08' maxScale='0' styleCategories='AllStyleCategories'><flags><Identifiable>1</Identifiable><Removable>1</Removable><Searchable>1</Searchable></flags><customproperties><property key='WMSBackgroundLayer' value='false'/><property key='WMSPublishDataSourceUrl' value='false'/><property key='embeddedWidgets/count' value='0'/><property key='identify/format' value='Value'/></customproperties><pipe><rasterrenderer band='1' type='paletted' alphaBand='-1' opacity='1'><rasterTransparency/><minMaxOrigin><limits>None</limits><extent>WholeRaster</extent><statAccuracy>Estimated</statAccuracy><cumulativeCutLower>0.02</cumulativeCutLower><cumulativeCutUpper>0.98</cumulativeCutUpper><stdDevFactor>2</stdDevFactor></minMaxOrigin><colorPalette></colorPalette><colorramp name='[source]' type='randomcolors'/></rasterrenderer><brightnesscontrast contrast='0' brightness='0'/><huesaturation colorizeGreen='128' colorizeStrength='100' grayscaleMode='0' saturation='0' colorizeBlue='128' colorizeOn='0' colorizeRed='255'/><rasterresampler maxOversampling='2'/></pipe><blendMode>0</blendMode></qgis>")
  colours <- "paletteEntry value='%d' color='%s' label='%s' alpha='%d'"
  colours <- sprintf(colours, identifier, colour, category, alpha)
  invisible(sapply(colours, function(colour) xml_add_child(xml_find_first(style, ".//colorPalette"), colour)))
  write_xml(style, file)
}

# Converts a Stata dataset to raster(s)
dta2tif <- function(variable) {
  cat(paste0('- ', variable, '\n'))
  values  <- dataset[[variable]]
  outfile <- file.path(params$outdir, paste0(label, variable))
  # Character class
  if(class(values) == 'character') {
    values <- as.factor(values)
    outqml <- str_c(outfile, '.qml')
    if(!file.exists(outqml)) {
      category   <- levels(values)
      identifier <- seq(category)
      colour     <- rainbow(length(category))
      alpha      <- ifelse(str_detect(category, params$nocolour), 0, 255)
      make_qml(outqml, identifier, colour, category, alpha)
    }
  }
  layer <- setValues(reference, values)
  writeRaster(layer, str_c(outfile, '.tif'), overwrite=T)
}

# Computations ------------------------------------------------------------

cat('Reading data\n')
dataset   <- data.table(read.dta13(params$srcval))
reference <- raster(params$srcids)
cat('Matching to raster\n')
dataset   <- dataset[match(getValues(reference), dataset[[params$idvar]])]
variables <- setdiff(names(dataset), params$idvar)
cat('Writing raster(s)\n')
label <- gsub('\\.dta$', '', basename(params$srcval))
invisible(lapply(variables, dta2tif))
cat('Done')

# (!) Testing only --------------------------------------------------------
# params <- modifyList(params, list(
#   srcval='D:/alban_george/Dropbox/arthisto/BDF_laurent/Delimitations/de2015bavd10b1000_ur.dta',
#   srcids='D:/alban_george/Dropbox/arthisto/data_cerema/source/ca.tif',
#   outdir='~/Desktop/test',
#   # nocolour='',
#   nocolour='U000x|U0000|U00x0|U00xx',
#   idvar='id'))
# (!) Testing only --------------------------------------------------------