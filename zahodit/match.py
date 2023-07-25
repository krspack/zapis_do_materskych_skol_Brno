import pandas as pd
import csv
from matching.games import HospitalResident

priorities = {"0": ["0", "3"], "1": ["2", "1"], "2": ["0", "3", "2", "1"], "3": ["0", "3", "1"], "4": ["0"], "5": ["1", "3", "2"], "6": ["2"], "7": ["0"], "8": ["1"], "9": ["0", "2"], "10": ["1", "0", "3", "2"], "11": ["3", "2"], "12": ["0"], "13": ["0", "1", "3", "2"], "14": ["0", "1", "2"], "15": ["0", "2"], "16": ["3"], "17": ["2"], "18": ["0", "1"], "19": ["0", "3"]}
schools_longlists = {"0": ["12", "9", "19", "15", "18", "7", "13", "3", "2"], "1": ["14", "18", "3", "10", "8", "1", "2", "5"], "2": ["10", "11", "14", "17", "13"], "3": ["16", "10", "0", "11", "13", "19", "2", "5"]}
schools_capacities = {"0": 4, "1": 4, "2": 3, "3": 3}

game = HospitalResident.create_from_dictionaries(priorities, schools_longlists, schools_capacities)
result = game.solve(optimal="resident")
print(result)






