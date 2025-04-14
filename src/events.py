class Evento:
    def __init__(self, tiempo, tipo, paciente=None):
        self.tiempo = tiempo
        self.tipo = tipo  # "llegada", "inicio_atencion", "fin_atencion"
        self.paciente = paciente

    def __lt__(self, otro):
        return self.tiempo < otro.tiempo  # para usar en heapq



