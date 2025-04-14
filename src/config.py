from collections import namedtuple

CONFIG = {
    'duracion_simulacion': 1440,
    'tasa_llegadas': 1 / 3,
    'prioridades': [1, 2, 3, 4, 5],
    'distrib_prioridad': [0.05, 0.10, 0.30, 0.30, 0.25],
    'tiempo_atencion': {1: 20, 2: 18, 3: 15, 4: 10, 5: 5},
    'medicos': 4,
    'tiempo_max_espera': 90,
    'probabilidad_requiere_medico_especifico': 0.3,
    'probabilidad_examen': 0.2,
    'duracion_examen_promedio': 10,
    'probabilidad_segunda_consulta': 0.15
}
