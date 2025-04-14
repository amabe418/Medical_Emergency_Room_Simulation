class Paciente:
    def __init__(self, id, llegada, prioridad, medico_asignado=None):
        self.id = id
        self.llegada = llegada
        self.prioridad = prioridad
        self.inicio_atencion = None
        self.fin_atencion = None
        self.abandona = False
        self.medico_asignado = medico_asignado

class Medico:
    def __init__(self, id):
        self.id = id
        self.ocupado = False

