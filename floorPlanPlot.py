import matplotlib.pyplot as plt
import math
from typing import List

import numpy as np

SIM_FILE_PATH = "resources/sims/sefm/exp2/exp2a.txt"
ROB_X_VAR_NAME = "robPositionX"
ROB_Y_VAR_NAME = "robPositionY"
HUM_X_VAR_NAME = "humanPositionX"
HUM_Y_VAR_NAME = "humanPositionY"
HUM_FATIGUE = "humanFatigue"


class TimedPoint:
    def __init__(self, time, x, y):
        self.time = time
        self.x = x
        self.y = y


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# read data from sim file
def read_data_from_file(file_name, header, x, startTime, stopTime):
    f = open(file_name, "r")
    contents = ''
    if f.mode == 'r':
        contents = f.read()
    variables = contents.split('#')
    right_index = 0
    for s in variables:
        if s.replace(' ', '') == header:
            right_index = variables.index(s)
    data = variables[right_index + 1].split("\n")
    data = data[3:len(data) - 1]
    data_num = list(map(lambda i: data[i].split(' ')[1], range(len(data))))
    data_num = list(map(lambda i: float(data_num[i]), range(len(data))))
    data_time = list(map(lambda i: data[i].split(' ')[0], range(len(data))))
    data_time = list(map(lambda i: math.floor(float(data_time[i])), range(len(data))))
    points = []
    for d in data_num:
        if startTime <= data_time[data_num.index(d)] <= stopTime:
            if x:
                points.append(TimedPoint(data_time[data_num.index(d)], d, 0))
            else:
                points.append(TimedPoint(data_time[data_num.index(d)], 0, d))
    return points


# Match x and y in lists of timed points
def getPointList(x: List[TimedPoint], y: List[TimedPoint], startTime, stopTime):
    result: List[Point] = []
    last_max_x = 0
    last_max_y = 0
    for i in range(startTime, stopTime):
        new_point = Point(0, 0)
        for px in x:
            if px.time <= i:
                last_max_x = x.index(px)
            else:
                break
        new_point.x = x[last_max_x].x
        for py in y:
            if py.time <= i:
                last_max_y = y.index(py)
            else:
                break
        new_point.y = y[last_max_y].y
        result.append(new_point)

    return result


def getFieldPoints(header1: str, header2: str, startTime, stopTime):
    points_x = read_data_from_file(SIM_FILE_PATH, header1, 1, startTime, stopTime)
    points_y = read_data_from_file(SIM_FILE_PATH, header2, 0, startTime, stopTime)
    return getPointList(points_x, points_y, startTime, stopTime)


# img = plt.imread("resources/sims/sefm/exp1/fph.png", format='png')
# fig, ax = plt.subplots()
# ax.imshow(img, extent=[90, 1420, 0, 660], interpolation='none')

# ROBOT DATA
# points_robot = getFieldPoints(ROB_X_VAR_NAME, ROB_Y_VAR_NAME, 0, 50)
#
# ax.plot(list(map(lambda i: points_robot[i].x, range(len(points_robot)))),
#         list(map(lambda i: points_robot[i].y, range(len(points_robot)))),
#         '--', linewidth=1, color='firebrick')
# ax.plot(points_robot[0].x, points_robot[0].y, 'o',
#         linewidth=10, color='firebrick')
# ax.plot(points_robot[len(points_robot) - 1].x, points_robot[len(points_robot) - 1].y, 'o',
#         linewidth=10, color='firebrick')
#
# points_robot_b = getFieldPoints(ROB_X_VAR_NAME, ROB_Y_VAR_NAME, 0, 2000)
#
# ax.plot(list(map(lambda i: points_robot_b[i].x, range(len(points_robot_b)))),
#         list(map(lambda i: points_robot_b[i].y, range(len(points_robot_b)))),
#         '--', linewidth=1, color='firebrick')
# ax.plot(points_robot_b[len(points_robot_b) - 1].x, points_robot_b[len(points_robot_b) - 1].y, 'o',
#         linewidth=10, color='firebrick')
#
# # HUMAN DATA
# points_human: List[Point] = getFieldPoints(HUM_X_VAR_NAME + '[0]', HUM_Y_VAR_NAME + '[0]', 0, 50)
#
# ax.plot(list(map(lambda i: points_human[i].x, range(len(points_human)))),
#         list(map(lambda i: points_human[i].y, range(len(points_human)))),
#         '--', linewidth=1, color='green')
# ax.plot(points_human[0].x, points_human[0].y, 'x',
#         linewidth=10, color='green')
# ax.plot(points_human[len(points_human) - 1].x, points_human[len(points_human) - 1].y, 'o',
#         linewidth=10, color='green')
#
# points_human_b: List[Point] = getFieldPoints(HUM_X_VAR_NAME + '[0]', HUM_Y_VAR_NAME + '[0]', 0, 2000)
#
# ax.plot(list(map(lambda i: points_human_b[i].x, range(len(points_human_b)))),
#         list(map(lambda i: points_human_b[i].y, range(len(points_human_b)))),
#         '--', linewidth=1, color='green')
# ax.plot(points_human_b[len(points_human_b) - 1].x, points_human_b[len(points_human_b) - 1].y, 'o',
#         linewidth=10, color='green')

# points_human2 = getFieldPoints(HUM_X_VAR_NAME + '[1]', HUM_Y_VAR_NAME + '[1]', 0, 360)
#
# ax.plot(list(map(lambda i: points_human2[i].x, range(len(points_human2)))),
#         list(map(lambda i: points_human2[i].y, range(len(points_human2)))),
#         '--', linewidth=1, color='blue')
# ax.plot(points_human2[0].x, points_human2[0].y, 'x',
#         linewidth=10, color='blue')
# ax.plot(points_human2[len(points_human2) - 1].x, points_human2[len(points_human2) - 1].y, 'o',
#         linewidth=10, color='blue')
#
# points_human2_b = getFieldPoints(HUM_X_VAR_NAME + '[1]', HUM_Y_VAR_NAME + '[1]', 0, 360)
#
# ax.plot(list(map(lambda i: points_human2_b[i].x, range(len(points_human2_b)))),
#         list(map(lambda i: points_human2_b[i].y, range(len(points_human2_b)))),
#         '--', linewidth=1, color='blue')
# ax.plot(points_human2_b[len(points_human2_b) - 1].x, points_human2_b[len(points_human2_b) - 1].y, 'o',
#         linewidth=10, color='blue')

# points_human3 = getFieldPoints(HUM_X_VAR_NAME + '[2]', HUM_Y_VAR_NAME + '[2]', 1000, 1000)
#
# ax.plot(list(map(lambda i: points_human3[i].x, range(len(points_human3)))),
#         list(map(lambda i: points_human3[i].y, range(len(points_human3)))),
#         '--', linewidth=0, color='orange')

# plt.savefig('resources/sims/sefm/exp1/h1a.png', dpi=600)

# Fatigue plot
def getTime(elem):
    return elem.time


ftgPts = read_data_from_file(SIM_FILE_PATH, ROB_Y_VAR_NAME, 1, 0, 265)
ftgPts.sort(key=getTime)
fig, ax = plt.subplots()
line, = ax.plot(list(map(lambda i: ftgPts[i].time, range(len(ftgPts)))),
                list(map(lambda i: ftgPts[i].x, range(len(ftgPts)))),
                '-', linewidth=1.5, color='firebrick')
line.set_label('R_pos_y')
ax.legend(loc='upper right')

ftgPts2 = read_data_from_file(SIM_FILE_PATH, HUM_Y_VAR_NAME+'[0]', 1, 0, 500)
ftgPts2.sort(key=getTime)
line2, = ax.plot(list(map(lambda i: ftgPts2[i].time, range(len(ftgPts2)))),
                list(map(lambda i: ftgPts2[i].x, range(len(ftgPts2)))),
                '-', linewidth=1.5, color='blue')
line2.set_label('H1_pos_y')
ax.legend(loc='upper right')

ftgPts3 = read_data_from_file(SIM_FILE_PATH, HUM_Y_VAR_NAME+'[1]', 1, 0, 500)
ftgPts3.sort(key=getTime)
line2, = ax.plot(list(map(lambda i: ftgPts3[i].time, range(len(ftgPts3)))),
                list(map(lambda i: ftgPts3[i].x, range(len(ftgPts3)))),
                '-', linewidth=1.5, color='green')
line2.set_label('H2_pos_y')
ax.legend(loc='upper right')


plt.xlabel('t [s]')
plt.ylabel('pos_y [cm]')
plt.yticks(np.arange(0, 1400, step=100))
plt.xticks(np.arange(0, 500, step=200))
plt.savefig('resources/sims/sefm/exp2/exp2aY.png', dpi=600, figsize=(3, 6))
