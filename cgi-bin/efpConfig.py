'''
Created on Nov 24, 2009

@author: rtbreit

Modified 4 Aug 2011 by N. Provart - slight tweak to output text to include link to XML file and position of probe set labels
'''

DB_HOST = ''           # hostname of MySQL database server
DB_USER = ''            # username for database access
DB_PASSWD = ''          # password for database access
DB_ANNO = None	# database name for annotations lookup
DB_ORTHO = None		# ortholog DB

# lookup table for gene annotation
DB_ANNO_TABLE = None
DB_ANNO_GENEID_COL = None

# lookup table for probeset id
DB_LOOKUP_TABLE = None
DB_LOOKUP_GENEID_COL = None
DB_LOOKUP_ARABIDOPSIS_COL = None

# lookup tables for ncbi ids
DB_NCBI_GENE_TABLE = None
DB_NCBI_PROT_TABLE = None
DB_NCBI_GENEID_COL = None

#Check Y-AXIS message
Y_AXIS = {}
Y_AXIS['kalanchoe'] = "Expression signal"

#Check if lookup exists
LOOKUP = {}
LOOKUP['kalanchoe'] = "0"

# initial gene ids when start page is loaded
GENE_ID_DEFAULT1 = 'Kaladp0001s0001'
GENE_ID_DEFAULT2 = 'Kaladp0001s0002'

# the little graph on the tga image has a scale
# such that 1 unit is x pixels for different ranges on the x-axis of the graph
# the GRAPH_SCAL_UNIT consists of value pairs: upper end of range and scale unit
# so ((1000, 0.031), (10000, 0.003222), (1000000, 0.00031)) means:
# use 0.031 as scale unit for 0 < signal < 1000
# use 0.003222 as scale unit for 1000 < signal < 10000
# use 0.00031 as scale unit for 10000 < signal < 1000000
# see also efp.drawImage()
GRAPH_SCALE_UNIT = {}
# the default values are used if for the given data source no special values are defined
#GRAPH_SCALE_UNIT["default"] = [(10000, 0.0031), (1000000, 0.0003222)]
#GRAPH_SCALE_UNIT["default"] = [(1000, 0.031), (10000, 0.003222), (1000000, 0.00031)]
GRAPH_SCALE_UNIT["default"] = [(1000, 2), (10000, 0.2), (1000000, 0.02)]

# define additional header text for individual data sources
# you can use key 'default' for each not individually defined
datasourceHeader = {}
datasourceHeader['default'] = ''

# define additional footer text for individual data sources
# you can use key 'default' for each not individually defined
datasourceFooter = {}
datasourceFooter['default'] = ''

# regular expression for check of gene id input (here agi and probeset id allowed) 
inputRegEx = "^(Kaladp\d+s\d+)$"

# default thresholds
minThreshold_Compare = 0.6  # Minimum color threshold for comparison is 0.6, giving us [-0.6, 0.6] on the color legend
minThreshold_Relative = 0.6 # Minimum color threshold for median is 0.6, giving us [-0.6, 0.6] on the color legend ~ 1.5-Fold
minThreshold_Absolute = 10  # Minimum color threshold for max is 10, giving us [0, 10] on the color legend

# coordinates where to write gene id, probeset id and gene alias into image
GENE_ID1_POS = (15, 5)
GENE_ID2_POS = (15, 23)
GENE_PROBESET1_POS = (140, 8)
GENE_PROBESET2_POS = (140, 26)
GENE_ALIAS1_POS = (0,10)
GENE_ALIAS2_POS = (0, 10)

defaultDataSource = 'Light_Response'
dataDir = 'data_kalanchoe'

dbGroupDefault = 'group1'
# list of datasources in same group to find max signal 
groupDatasource = {}
groupDatasource["group1"] = ['Light_Response']

# mapping of xml files to show datasource name
groupDatasourceName = {}
groupDatasourceName["group1"] = {'Light_Response':'Light Response'}

# ortholog configuration
# list of species where orthologs should be tried to retrieve (names must be the same as in ortholog db)
ortholog_species = ('POP', 'TAIR8', 'MEDV3', 'RICE', 'BARLEY', 'SOYBEAN')

efpLink = {}
efpLink['POP'] = "http://bar.utoronto.ca/efp_poplar/cgi-bin/efpWeb.cgi?dataSource=Poplar&primaryGene=%s&modeInput=Absolute"
efpLink['TAIR8'] = "http://bar.utoronto.ca/efp_arabidopsis/cgi-bin/efpWeb.cgi?dataSource=Developmental_Map&primaryGene=%s&modeInput=Absolute"
efpLink['MEDV3'] = "http://bar.utoronto.ca/efp_medicago/cgi-bin/efpWeb.cgi?dataSource=medicago_mas&primaryGene=%s&modeInput=Absolute"
efpLink['SOYBEAN'] = "http://bar.utoronto.ca/efp_soybean/cgi-bin/efpWeb.cgi?dataSource=soybean&primaryGene=%s&modeInput=Absolute"
efpLink['RICE'] = "http://bar.utoronto.ca/efp_rice/cgi-bin/efpWeb.cgi?dataSource=rice_mas&primaryGene=%s&modeInput=Absolute"
efpLink['BARLEY'] = "http://bar.utoronto.ca/efp_barley/cgi-bin/efpWeb.cgi?dataSource=barley_mas&primaryGene=%s&modeInput=Absolute"

#species = 'THELLUNGIELLA'
species = 'KALANCHOE'
spec_names = {}
spec_names['POP'] = 'Poplar'
spec_names['TAIR8'] = 'Arabidopsis'
spec_names['MEDV3'] = 'Medicago'
spec_names['SOYBEAN'] = 'Soybean'
spec_names['RICE'] = 'Rice'
spec_names['BARLEY'] = 'Barley'
spec_names['EUTREMA'] = 'Eutrema'
spec_names['ARACHIS'] = 'Brachypodium'
spec_names['SELAGINELLA'] = 'Selaginella'
spec_names['KALANCHOE'] = 'Kalanchoe'

