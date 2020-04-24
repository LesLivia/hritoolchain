import subprocess
from enum import Enum
import json


class Pattern(Enum):
    FOLLOWER = 0
    LEADER = 1
    RECEIVER = 2


class Human:
    def __init__(self, name, upp_id, vel, pattern):
        self.name = name
        self.upp_id = upp_id
        self.vel = vel
        self.pattern = pattern


# Constants
PATTERNS = '#PATTERNS#'
HINSTANCES = '#HINSTANCES#'
HSYSTEM = '#HSYSTEM#'


def getPattStr(value):
    if value == 0:
        return 'Follower'
    elif value == 1:
        return 'Leader'
    elif value == 2:
        return 'Recipient'


def read_data_from_file(file_name):
    f = open(file_name, "r")
    contents = ''
    if f.mode == 'r':
        contents = f.read()
    return contents


# Paths
templatePath = './templates/hriTemplate.xml'
verifytaPath = '/Applications/Dev/uppaal64-4.1.24/bin-Darwin/'
modelPath = '/Applications/Dev/uppaal64-4.1.24/bin-Darwin/human-robot-three-patterns.xml'
queryPath = '/Applications/Dev/uppaal64-4.1.24/bin-Darwin/hri.q'

# Model Instances
jsonData = read_data_from_file('./templates/input.json')
loadedJson: object = json.loads(jsonData)
humansInModel = []
for h in loadedJson['humans']:
    humansInModel.append(Human(h['name'], h['upp_id'], h['vel'], h['pattern']))

template = read_data_from_file(templatePath)

pStr = '{'
instStr = ''
sysStr = ''
for h in humansInModel:
    pStr += str(h.pattern)
    if humansInModel.index(h) != len(humansInModel) - 1:
        pStr += ', '
    instStr += h.name + ' = Human_' + getPattStr(h.pattern) + '(' + str(h.upp_id) + ', ' + str(h.vel) + ');\n'
    sysStr += str(h.name) + ', '
pStr += '}'
template = template.replace(PATTERNS, pStr)
template = template.replace(HINSTANCES, instStr)
template = template.replace(HSYSTEM, sysStr)

newModel = open(modelPath, "w+")
newModel.write(template)
newModel.close()

# Run Verification
list_files = subprocess.call(['./scripts/verify.sh', verifytaPath, modelPath, queryPath])
