# Simulación de Sala de Urgencias Médicas 🏥

Este proyecto implementa una simulación basada en eventos discretos para modelar el comportamiento de una sala de urgencias médicas, con el objetivo de analizar métricas clave como el tiempo de espera, abandono de pacientes y uso de médicos bajo diferentes configuraciones.

## 🧠 Descripción

El sistema simula la dinámica de atención en una sala de urgencias, considerando:
- Llegadas de pacientes con diferentes tasas.
- Asignación fija de médicos.
- Priorización de pacientes críticos.
- Derivaciones a pruebas médicas u otros médicos.
- Abandonos por espera prolongada.

Se utilizaron clases específicas para representar pacientes, eventos y el motor de simulación (`SalaUrgencias`), procesando los eventos en orden cronológico a través de una cola de prioridad.



