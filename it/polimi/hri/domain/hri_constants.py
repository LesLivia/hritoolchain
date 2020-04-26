import sys

# Constants
PATTERNS = '#PATTERNS#'
HINSTANCES = '#HINSTANCES#'
RINSTANCES = '#RINSTANCES#'
HSYSTEM = '#HSYSTEM#'
RSYSTEM = '#RSYSTEM#'
HDEST = '#HDESTINATIONS#'
NHUMS = '#NHUMS#'
NFALSE = '#NFALSE#'
NZEROES = '#NZEROES#'

FLOORPLAN = '#FLOORPLAN#'

# Paths
verifytaPath = '/Applications/Dev/uppaal64-4.1.24/bin-Darwin/'
# modelPath = '/Applications/Dev/uppaal64-4.1.24/bin-Darwin/human-robot-three-patterns.xml'
modelPath = 'models/' + str(sys.argv[1]) + '/' + str(sys.argv[1]) + str(sys.argv[2]) + '.xml'
# queryPath = '/Applications/Dev/uppaal64-4.1.24/bin-Darwin/hri.q'
queryPath = 'models/' + str(sys.argv[1]) + '/' + str(sys.argv[1]) + str(sys.argv[2]) + '.q'

# Queries
TIME_BOUND = '#TB#'
Q_HPOS = '#HPOS#'
Q_HSERVED = '#HSERVED#'

simQuery = 'simulate[<=#TB#]{batteryCharge, robPositionX, robPositionY, #HPOS# o.mission_accomplished*200, ' \
           '#HSERVED# o.mission_failed*150} '

pFailQuery = 'Pr[<=#TB#](<> o.mission_failed)'
pScsQuery = 'Pr[<=#TB#](<> o.mission_accomplished)'
