
from matching.games import HospitalResident

priorities = {
    "0": ["0", "1"],
    "1": ["1"],
    "2": ["1"]
}

schools_shortlists = {
    "0": ["0"],
    "1": ["1", "0", "2"]
}

schools_capacities = {
    "0": 1,
    "1": 1,
    "2": 1
}

game = HospitalResident.create_from_dictionaries(priorities, schools_shortlists, schools_capacities)
print(game)
matching = game.solve(optimal="resident")
print(matching)

