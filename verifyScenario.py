import subprocess
import json
import sys
from it.polimi.hri.domain import user_input as dom
from it.polimi.hri.domain import hri_constants as const


def read_data_from_file(file_name):
    f = open(file_name, "r")
    contents = ''
    if f.mode == 'r':
        contents = f.read()
    return contents


# MODEL

templatePath = './resources/templates/hriTemplate.xml'

# Model Instances
jsonData = read_data_from_file('resources/templates/sefm_exp/' + str(sys.argv[1]) + str(sys.argv[2]) + '.json')
loadedJson: object = json.loads(jsonData)

# Humans Instances
humansInModel = []
for h in loadedJson['humans']:
    humansInModel.append(dom.Human(h['name'], h['upp_id'], h['vel'], h['pattern'], h['p_f'], h['p_fw']))

template = read_data_from_file(templatePath)

pStr = '{'
instStr = ''
sysStr = ''
falsesStr = '{'
zeroesStr = '{'
for h in humansInModel:
    pStr += str(h.pattern)
    falsesStr += 'false'
    zeroesStr += '0.0'
    if humansInModel.index(h) != len(humansInModel) - 1:
        pStr += ', '
        falsesStr += ', '
        zeroesStr += ', '
    instStr += h.name + ' = Human_' + dom.getPattStr(h.pattern) + '(' + str(h.upp_id) + ', ' + str(
        h.vel) + ', ' + str(h.p_f) + ', ' + str(h.p_fw) + ');\n'
    sysStr += str(h.name) + ', '
pStr += '}'
falsesStr += '}'
zeroesStr += '}'

template = template.replace(const.NHUMS, str(len(humansInModel)))
template = template.replace(const.PATTERNS, pStr)
template = template.replace(const.HINSTANCES, instStr)
template = template.replace(const.HSYSTEM, sysStr)
template = template.replace(const.NFALSE, falsesStr)
template = template.replace(const.NZEROES, zeroesStr)

# DESTINATIONS
dests = []

for d in loadedJson['destinations']:
    dests.insert(d['h_id'], dom.Point(d['x'], d['y']))

destXStr = 'double destX[' + str(len(dests)) + '] = {'
destYStr = 'double destY[' + str(len(dests)) + '] = {'
for d in dests:
    destXStr += str(d.x)
    destYStr += str(d.y)
    if dests.index(d) != len(dests) - 1:
        destXStr += ', '
        destYStr += ', '
    else:
        destXStr += '};'
        destYStr += '};'

template = template.replace(const.HDEST, destXStr + '\n' + destYStr)

# FLOOR PLAN
fp = []

for p in loadedJson['floorPlan']:
    fp.append(dom.POI(p['name'], dom.Point(p['x'], p['y'])))

fpStr = ''
for p in fp:
    fpStr += 'point ' + p.name + ' = {' + str(p.coord.x) + ', ' + str(p.coord.y) + '};\n'

template = template.replace(const.FLOORPLAN, fpStr)

# ROBOTS
robotsInModel = []
for r in loadedJson['robots']:
    robotsInModel.append(dom.Robot(r['name'], r['upp_id'], r['vel'], r['acc'], r['bcharge'], r['hToServe']))

rInstStr = ''
rSysStr = ''
for r in robotsInModel:
    newR = r.name + ' = Robot(' + str(r.upp_id) + ', ' + str(r.vel) + ', ' + str(r.acc) + ');\n'
    newB = 'b' + str(r.upp_id) + ' = Battery(' + str(r.upp_id) + ', ' + str(r.bcharge) + ');\n'
    rInstStr += newR + newB
    rSysStr += r.name + ', ' + 'b' + str(r.upp_id) + ', '

template = template.replace(const.RINSTANCES, rInstStr)
template = template.replace(const.RSYSTEM, rSysStr)
template = template.replace(const.NHUMSTOSERVE, str(robotsInModel[0].hToServe))

print(template)

# QUERIES
exp = []
for e in loadedJson['experiments']:
    exp.append(dom.Experiment(e["type"], e["tb"]))

queries = ''
newExp = ''
for e in exp:
    if e.type == 's':
        newExp = const.simQuery + '\n'
        hFatg = ''
        hPosX = ''
        hPosY = ''
        hServed = ''
        for h in humansInModel:
            hFatg += 'humanFatigue[' + str(h.upp_id - 1) + ']*1000, '
            hPosX += 'humanPositionX[' + str(h.upp_id - 1) + '], '
            hPosY += 'humanPositionY[' + str(h.upp_id - 1) + '], '
            hServed += 'served[' + str(h.upp_id - 1) + ']*100, '
        newExp = newExp.replace(const.Q_HFATG, hFatg)
        newExp = newExp.replace(const.Q_HPOS, hPosX + hPosY)
        newExp = newExp.replace(const.Q_HSERVED, hServed)
    elif e.type == 'pfail':
        newExp = const.pFailQuery + '\n'
    elif e.type == 'pscs':
        newExp = const.pScsQuery + '\n'
    newExp = newExp.replace(const.TIME_BOUND, str(e.tb))
    queries += newExp

print(queries)

newModel = open(const.modelPath, "w+")
newModel.write(template)
newModel.close()

newQueries = open(const.queryPath, "w+")
newQueries.write(queries)
newQueries.close()

# Run Verification
list_files = subprocess.call(['./run_exp.sh', str(sys.argv[1]), str(sys.argv[2])])
