"""Порядок вызова систем. Единственное место, где меняется очередь."""
from . import (input as _input, player, traffic, police, combat,
               bosses, spawning, interactions, weather_time,
               effects, wanted)

ORDER = [
    player, traffic, police, bosses, combat,
    spawning, weather_time, effects, wanted,
]

input = _input
