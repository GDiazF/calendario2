from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from calendario.models import (
    Estado, EstadoFuente, Turno, TurnoBloque, 
    Faena, Personal, AsignacionFaena, TipoAusentismo, Ausentismo
)
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Crea datos de ejemplo para el calendario de planificación'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos de ejemplo...')
        
        # 1. Crear Estados básicos
        self.crear_estados()
        
        # 2. Crear Turnos comunes
        self.crear_turnos()
        
        # 3. Crear Faenas
        self.crear_faenas()
        
        # 4. Crear EstadosFuente para conectar con modelos existentes
        self.crear_estados_fuente()
        
        # 5. Crear algunas asignaciones de ejemplo
        self.crear_asignaciones_ejemplo()
        
        self.stdout.write(
            self.style.SUCCESS('¡Datos de ejemplo creados exitosamente!')
        )

    def crear_estados(self):
        """Crea estados básicos del calendario"""
        estados_data = [
            {
                'nombre': 'Disponible',
                'color': '#FFFFFF',
                'background_color': '#E9ECEF',
                'prioridad': 5,
                'es_bloqueante': False
            },
            {
                'nombre': 'Día',
                'color': '#FFFFFF',
                'background_color': '#28A745',
                'prioridad': 10,
                'es_bloqueante': False
            },
            {
                'nombre': 'Noche',
                'color': '#FFFFFF',
                'background_color': '#343A40',
                'prioridad': 10,
                'es_bloqueante': False
            },
            {
                'nombre': 'Descanso',
                'color': '#000000',
                'background_color': '#FFC107',
                'prioridad': 8,
                'es_bloqueante': False
            },
            {
                'nombre': 'Permiso',
                'color': '#FFFFFF',
                'background_color': '#FF7675',
                'prioridad': 15,
                'es_bloqueante': True
            },
            {
                'nombre': 'Licencia',
                'color': '#FFFFFF',
                'background_color': '#FDCB6E',
                'prioridad': 20,
                'es_bloqueante': True
            },
            {
                'nombre': 'Vacaciones',
                'color': '#FFFFFF',
                'background_color': '#55A3FF',
                'prioridad': 12,
                'es_bloqueante': False
            }
        ]
        
        for estado_data in estados_data:
            estado, created = Estado.objects.get_or_create(
                nombre=estado_data['nombre'],
                defaults=estado_data
            )
            if created:
                self.stdout.write(f'Estado creado: {estado.nombre}')
            else:
                self.stdout.write(f'Estado ya existe: {estado.nombre}')

    def crear_turnos(self):
        """Crea turnos comunes"""
        # Turno 7x7
        turno_7x7, created = Turno.objects.get_or_create(
            nombre='7x7',
            defaults={
                'descripcion': '7 días de trabajo, 7 días de descanso',
                'activo': True
            }
        )
        if created:
            self.stdout.write(f'Turno creado: {turno_7x7.nombre}')
        
        # Crear bloques para 7x7
        estado_dia = Estado.objects.get(nombre='Día')
        estado_descanso = Estado.objects.get(nombre='Descanso')
        
        TurnoBloque.objects.get_or_create(
            turno=turno_7x7,
            orden=1,
            defaults={
                'duracion_dias': 7,
                'estado': estado_dia
            }
        )
        
        TurnoBloque.objects.get_or_create(
            turno=turno_7x7,
            orden=2,
            defaults={
                'duracion_dias': 7,
                'estado': estado_descanso
            }
        )
        
        # Turno 5x2
        turno_5x2, created = Turno.objects.get_or_create(
            nombre='5x2',
            defaults={
                'descripcion': '5 días de trabajo, 2 días de descanso',
                'activo': True
            }
        )
        if created:
            self.stdout.write(f'Turno creado: {turno_5x2.nombre}')
        
        # Crear bloques para 5x2
        TurnoBloque.objects.get_or_create(
            turno=turno_5x2,
            orden=1,
            defaults={
                'duracion_dias': 5,
                'estado': estado_dia
            }
        )
        
        TurnoBloque.objects.get_or_create(
            turno=turno_5x2,
            orden=2,
            defaults={
                'duracion_dias': 2,
                'estado': estado_descanso
            }
        )

    def crear_faenas(self):
        """Crea faenas de ejemplo"""
        faenas_data = [
            {
                'nombre': 'COLLAHUASI',
                'ubicacion': 'Región de Tarapacá, Chile',
                'descripcion': 'Mina de cobre a rajo abierto'
            },
            {
                'nombre': 'QUEBRADA BLANCA',
                'ubicacion': 'Región de Antofagasta, Chile',
                'descripcion': 'Mina de cobre y oro'
            }
        ]
        
        for faena_data in faenas_data:
            faena, created = Faena.objects.get_or_create(
                nombre=faena_data['nombre'],
                defaults=faena_data
            )
            if created:
                self.stdout.write(f'Faena creada: {faena.nombre}')
            else:
                self.stdout.write(f'Faena ya existe: {faena.nombre}')

    def crear_estados_fuente(self):
        """Crea EstadosFuente para conectar con modelos existentes"""
        # Conectar Permiso con Ausentismo
        try:
            estado_permiso = Estado.objects.get(nombre='Permiso')
            content_type_ausentismo = ContentType.objects.get_for_model(Ausentismo)
            
            EstadoFuente.objects.get_or_create(
                estado=estado_permiso,
                defaults={
                    'content_type': content_type_ausentismo,
                    'campo_fecha_inicio': 'fechaini',
                    'campo_fecha_fin': 'fechafin',
                    'campo_personal': 'personal_id'
                }
            )
            self.stdout.write('EstadoFuente creado: Permiso → Ausentismo')
        except Exception as e:
            self.stdout.write(f'Error creando EstadoFuente para Permiso: {e}')

    def crear_asignaciones_ejemplo(self):
        """Crea algunas asignaciones de ejemplo"""
        try:
            # Obtener personal existente
            personal = Personal.objects.filter(activo=True).first()
            if not personal:
                self.stdout.write('No hay personal activo para crear asignaciones')
                return
            
            # Obtener faena y turno
            faena = Faena.objects.filter(activo=True).first()
            turno = Turno.objects.filter(activo=True).first()
            
            if not faena or not turno:
                self.stdout.write('No hay faenas o turnos activos')
                return
            
            # Obtener primer bloque del turno
            bloque_inicio = TurnoBloque.objects.filter(turno=turno, orden=1).first()
            if not bloque_inicio:
                self.stdout.write('No hay bloques en el turno')
                return
            
            # Crear asignación
            asignacion, created = AsignacionFaena.objects.get_or_create(
                personal=personal,
                faena=faena,
                turno=turno,
                defaults={
                    'fecha_inicio': date.today(),
                    'bloque_inicio': bloque_inicio,
                    'activo': True
                }
            )
            
            if created:
                self.stdout.write(f'Asignación creada: {personal.nombre} → {faena.nombre}')
            else:
                self.stdout.write(f'Asignación ya existe para {personal.nombre}')
                
        except Exception as e:
            self.stdout.write(f'Error creando asignación de ejemplo: {e}')
