import heapq
import random
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict, deque
from entities import Paciente
from entities import Medico
from events import Evento
from config import CONFIG


class SimuladorUrgencias:
    def __init__(self):
        self.resetear()

    def resetear(self):
        self.tiempo_actual = 0
        self.cola_eventos = []
        self.cola_espera = defaultdict(deque)
        self.medicos = [Medico(i) for i in range(CONFIG['medicos'])]
        self.pacientes = []
        self.registro = {
            'esperas': [],
            'abandono': 0,
            'atendidos': 0,
            'uso_medico_tiempo': 0,
            'espera_por_prioridad': defaultdict(list),
            'abandono_por_prioridad': defaultdict(int),
            'atendidos_por_prioridad': defaultdict(int),
            'pacientes_criticos': 0
        }
        self.id_paciente = 0

    def generar_prioridad(self):
        return random.choices(CONFIG['prioridades'], CONFIG['distrib_prioridad'])[0]

    def tiempo_atencion(self, prioridad):
        return random.expovariate(1 / CONFIG['tiempo_atencion'][prioridad])

    def tiempo_llegada(self):
        return random.expovariate(CONFIG['tasa_llegadas'])

    def planificar_evento(self, evento):
        heapq.heappush(self.cola_eventos, evento)

    def iniciar_simulacion(self):
        self.planificar_evento(Evento(self.tiempo_llegada(), 'LlegadaPaciente'))

        while self.cola_eventos and self.tiempo_actual <= CONFIG['duracion_simulacion']:
            evento = heapq.heappop(self.cola_eventos)
            self.tiempo_actual = evento.tiempo

            if evento.tipo == 'LlegadaPaciente':
                self.procesar_llegada()
            elif evento.tipo == 'InicioAtencion':
                self.procesar_inicio_atencion(evento.paciente)
            elif evento.tipo == 'FinAtencion':
                self.procesar_fin_atencion(evento.paciente)
            elif evento.tipo == 'PacienteCritico':
                self.procesar_paciente_critico(evento.paciente)
            elif evento.tipo == 'abandono':
                self.procesar_abandono(evento.paciente)
            elif evento.tipo == 'InicioExamen':
                self.procesar_inicio_examen(evento.paciente)
            elif evento.tipo == 'FinExamen':
                self.procesar_fin_examen(evento.paciente)

    def procesar_inicio_examen(self, paciente):
        # Esto podría incluir más lógica si quieres ocupar una máquina específica, por ejemplo
        pass  # el evento "FinExamen" ya está planificado en el mismo momento

    def procesar_fin_examen(self, paciente):
        self.registro.setdefault('examenes', 0)
        self.registro['examenes'] += 1

    def procesar_llegada(self):
        prioridad = self.generar_prioridad()

        medico_asignado = None
        if random.random() < CONFIG.get('probabilidad_requiere_medico_especifico', 0.3):
            medico_asignado = random.randint(0, CONFIG['medicos'] - 1)

        paciente = Paciente(self.id_paciente, self.tiempo_actual, prioridad, medico_asignado)

        self.pacientes.append(paciente)
        self.cola_espera[prioridad].append(paciente)
        self.id_paciente += 1

        self.planificar_evento(Evento(self.tiempo_actual + self.tiempo_llegada(), 'LlegadaPaciente'))
        self.planificar_evento(Evento(self.tiempo_actual + CONFIG['tiempo_max_espera'], 'abandono', paciente))

        if random.random() < CONFIG.get('probabilidad_critico', 0.01):
            self.planificar_evento(Evento(self.tiempo_actual, 'PacienteCritico', paciente))

        self.asignar_medico()

    def asignar_medico(self):
        for prioridad in sorted(CONFIG['prioridades']):
            for paciente in list(self.cola_espera[prioridad]):
                # 1. Si el paciente requiere un médico específico
                if paciente.medico_asignado is not None:
                    medico = self.medicos[paciente.medico_asignado]
                    if not medico.ocupado:
                        self.cola_espera[prioridad].remove(paciente)
                        medico.ocupado = True
                        self.planificar_evento(Evento(self.tiempo_actual, 'InicioAtencion', paciente))
                        return
                else:
                    # 2. Buscar cualquier médico libre
                    for medico in self.medicos:
                        if not medico.ocupado:
                            self.cola_espera[prioridad].remove(paciente)
                            medico.ocupado = True
                            paciente.medico_asignado = medico.id  # se le asigna uno dinámicamente
                            self.planificar_evento(Evento(self.tiempo_actual, 'InicioAtencion', paciente))
                            return

    def procesar_inicio_atencion(self, paciente):
        paciente.inicio_atencion = self.tiempo_actual
        duracion = self.tiempo_atencion(paciente.prioridad)
        paciente.fin_atencion = self.tiempo_actual + duracion
        self.planificar_evento(Evento(paciente.fin_atencion, 'FinAtencion', paciente))
        self.registro['uso_medico_tiempo'] += duracion

    def procesar_fin_atencion(self, paciente):
        necesita_segunda_consulta = random.random() < CONFIG.get('probabilidad_segunda_consulta', 0.15)
        necesita_examen = not necesita_segunda_consulta and random.random() < CONFIG.get('probabilidad_examen', 0.2)

        if not necesita_segunda_consulta:
            espera = paciente.inicio_atencion - paciente.llegada
            self.registro['esperas'].append(espera)
            self.registro['espera_por_prioridad'][paciente.prioridad].append(espera)
            self.registro['atendidos'] += 1
            self.registro['atendidos_por_prioridad'][paciente.prioridad] += 1

        if necesita_segunda_consulta:
            # No liberamos al médico. Simulamos otra consulta con el mismo médico.
            nueva_duracion = self.tiempo_atencion(paciente.prioridad)
            paciente.inicio_atencion = self.tiempo_actual
            paciente.fin_atencion = self.tiempo_actual + nueva_duracion
            self.planificar_evento(Evento(paciente.fin_atencion, 'FinAtencion', paciente))
            self.registro['uso_medico_tiempo'] += nueva_duracion
            return  # Salimos sin liberar médico ni reasignar

        elif necesita_examen:
            # Paciente sale temporalmente para examen
            duracion_examen = random.expovariate(1 / CONFIG.get('duracion_examen_promedio', 10))
            paciente.fin_examen = self.tiempo_actual + duracion_examen
            self.planificar_evento(Evento(self.tiempo_actual, 'InicioExamen', paciente))
            self.planificar_evento(Evento(paciente.fin_examen, 'FinExamen', paciente))
            # Médico se libera
            self.medicos[paciente.medico_asignado].ocupado = False
            paciente.medico_asignado = None
            self.asignar_medico()
            return

        # Si no necesita más nada, se cierra atención normalmente
        if paciente.medico_asignado is not None:
            self.medicos[paciente.medico_asignado].ocupado = False
            paciente.medico_asignado = None

        self.asignar_medico()
    def procesar_abandono(self, paciente):
        if paciente.inicio_atencion is None and not paciente.abandona:
            paciente.abandona = True
            self.registro['abandono'] += 1
            self.registro['abandono_por_prioridad'][paciente.prioridad] += 1
            if paciente in self.cola_espera[paciente.prioridad]:
                self.cola_espera[paciente.prioridad].remove(paciente)

    def procesar_paciente_critico(self, paciente):
        paciente.prioridad = min(CONFIG['prioridades'])  # máxima prioridad
        self.cola_espera[paciente.prioridad].appendleft(paciente)  # al frente
        self.registro['pacientes_criticos'] += 1
        if any(not m.ocupado for m in self.medicos):
            self.asignar_medico()


    def ejecutar_varias_simulaciones(self, n=50):
        resultados = []
        for _ in range(n):
            self.resetear()
            self.iniciar_simulacion()
            resultados.append(self.registro.copy())
        self.analizar_simulaciones(resultados)

    def analizar_simulaciones(self, resultados):
        medias_espera = [np.mean(sim['esperas']) for sim in resultados if sim['esperas']]
        tasas_abandono = [sim['abandono'] / (sim['atendidos'] + sim['abandono']) for sim in resultados]
        usos_medico = [sim['uso_medico_tiempo'] / (CONFIG['duracion_simulacion'] * CONFIG['medicos']) for sim in resultados]

        print("\n--- Promedios tras múltiples simulaciones ---")
        print(f"Esperas promedio (global): {np.mean(medias_espera):.2f} min ± {np.std(medias_espera):.2f}")
        print(f"Tasa de abandono promedio: {np.mean(tasas_abandono) * 100:.2f}% ± {np.std(tasas_abandono) * 100:.2f}%")
        print(f"Uso promedio de médicos: {np.mean(usos_medico) * 100:.2f}% ± {np.std(usos_medico) * 100:.2f}%")

        plt.figure()
        plt.hist(medias_espera, bins=15, color='yellow', alpha=0.7)
        plt.title("Distribución de espera media entre simulaciones")
        plt.xlabel("Espera promedio (min)")
        plt.ylabel("Frecuencia")
        plt.savefig("results/graficos/espera_promedios_30sim.png")
        plt.show()

    def explorar_parametros(self, valores_medicos, tasas_llegada, n_sim=30):
        resultados_totales = []

        for medicos in valores_medicos:
            for tasa in tasas_llegada:
                print(f"\n>>> Ejecutando simulaciones para medicos = {medicos}, tasa_llegadas = {tasa:.3f}")
                CONFIG['medicos'] = medicos
                CONFIG['tasa_llegadas'] = tasa
                self.ejecutar_varias_simulaciones(n_sim)

if __name__ == "__main__":
    sim = SimuladorUrgencias()
    valores_medicos = [2, 4, 6]
    tasas_llegada = [1/2, 1/3, 1/5]
    sim.explorar_parametros(valores_medicos,tasas_llegada)
