from typing import List

from domain.hafeatures import SignalPoint, ChangePoint, TimeInterval, Labels


def identify_change_pts(entries: List[SignalPoint]):
    change_pts: List[ChangePoint] = []
    increasing = False

    for (index, entry) in enumerate(entries):
        old_increasing = increasing
        increasing = entry.value > entries[index - 1].value
        if old_increasing != increasing:
            label = Labels.STARTED if increasing else Labels.STOPPED
            change_pts.append(ChangePoint(TimeInterval(entries[index - 1].timestamp, entry.timestamp), label))

    return change_pts
