from django.core.management.base import BaseCommand
from calendario.models import Personal, DeptoEmpresa, Cargo, InfoLaboral, Faena, Turno, TurnoBloque, AsignacionFaena
from datetime import date

class Command(BaseCommand):
    help = 'Crea personal de ejemplo con información laboral completa'

    def handle(self, *args, **options):
        self.stdout.write('Creando personal de ejemplo...')
        
        # 1. Crear departamentos
        self.crear_departamentos()
        
        # 2. Crear cargos
        self.crear_cargos()
        
        # 3. Crear personal
        self.crear_personal()
        
        # 4. Crear información laboral
        self.crear_info_laboral()
        
        # 5. Crear asignaciones de faena
        self.crear_asignaciones_faena()
        
        self.stdout.write(
            self.style.SUCCESS('¡Personal de ejemplo creado exitosamente!')
        )

    def crear_departamentos(self):
        """Crea departamentos de ejemplo"""
        departamentos = [
            'OPERACIONES',
            'MANTENCIÓN',
            'LOGÍSTICA',
            'ADMINISTRACIÓN'
        ]
        
        for depto_nombre in departamentos:
            depto, created = DeptoEmpresa.objects.get_or_create(
                depto=depto_nombre
            )
            if created:
                self.stdout.write(f'Departamento creado: {depto.depto}')
            else:
                self.stdout.write(f'Departamento ya existe: {depto.depto}')

    def crear_cargos(self):
        """Crea cargos de ejemplo"""
        cargos_data = [
            ('MECÁNICO', 'MANTENCIÓN'),
            ('OPERADOR HORQUILLA', 'LOGÍSTICA'),
            ('RIGGER', 'OPERACIONES'),
            ('SUPERVISOR', 'OPERACIONES'),
            ('ADMINISTRATIVO', 'ADMINISTRACIÓN')
        ]
        
        for cargo_nombre, depto_nombre in cargos_data:
            depto = DeptoEmpresa.objects.get(depto=depto_nombre)
            cargo, created = Cargo.objects.get_or_create(
                cargo=cargo_nombre,
                depto_id=depto
            )
            if created:
                self.stdout.write(f'Cargo creado: {cargo.cargo} en {depto.depto}')
            else:
                self.stdout.write(f'Cargo ya existe: {cargo.cargo}')

    def crear_personal(self):
        """Crea personal de ejemplo"""
        personal_data = [
            {
                'rut': '12345678',
                'dvrut': '9',
                'nombre': 'KEVIN',
                'apepat': 'RIOS',
                'apemat': 'GALLARDO',
                'correo': 'kevin.rios@empresa.com',
                'direccion': 'Santiago, Chile'
            },
            {
                'rut': '23456789',
                'dvrut': '0',
                'nombre': 'JORGE',
                'apepat': 'CUBILLOS',
                'apemat': 'DIAZ',
                'correo': 'jorge.cubillos@empresa.com',
                'direccion': 'Antofagasta, Chile'
            },
            {
                'rut': '34567890',
                'dvrut': '1',
                'nombre': 'EMILIO',
                'apepat': 'ROJAS',
                'apemat': 'DIAZ',
                'correo': 'emilio.rojass@empresa.com',
                'direccion': 'Iquique, Chile'
            },
            {
                'rut': '45678901',
                'dvrut': '2',
                'nombre': 'GUILLERMO',
                'apepat': 'DIAZ',
                'apemat': 'FLORES',
                'correo': 'guillermo.diaz@empresa.com',
                'direccion': 'Calama, Chile'
            },
            {
                'rut': '56789012',
                'dvrut': '3',
                'nombre': 'FRANCISCO',
                'apepat': 'ROMAN',
                'apemat': 'FUENTES',
                'correo': 'francisco.roman@empresa.com',
                'direccion': 'Copiapó, Chile'
            }
        ]
        
        for persona_data in personal_data:
            persona, created = Personal.objects.get_or_create(
                rut=persona_data['rut'],
                defaults=persona_data
            )
            if created:
                self.stdout.write(f'Personal creado: {persona.nombre} {persona.apepat}')
            else:
                self.stdout.write(f'Personal ya existe: {persona.nombre} {persona.apepat}')

    def crear_info_laboral(self):
        """Crea información laboral para el personal"""
        # Asignar cargos específicos
        asignaciones_cargo = [
            ('KEVIN RIOS', 'MECÁNICO'),
            ('JORGE CUBILLOS', 'OPERADOR HORQUILLA'),
            ('EMILIO ROJAS', 'OPERADOR HORQUILLA'),
            ('GUILLERMO DIAZ', 'RIGGER'),
            ('FRANCISCO ROMAN', 'RIGGER')
        ]
        
        for nombre_completo, cargo_nombre in asignaciones_cargo:
            try:
                # Buscar personal
                nombre, apepat = nombre_completo.split(' ', 1)
                persona = Personal.objects.get(nombre=nombre, apepat=apepat)
                
                # Buscar cargo
                cargo = Cargo.objects.get(cargo=cargo_nombre)
                
                # Buscar departamento del cargo
                depto = cargo.depto_id
                
                # Crear o actualizar información laboral
                info_laboral, created = InfoLaboral.objects.get_or_create(
                    personal_id=persona,
                    defaults={
                        'depto_id': depto,
                        'cargo_id': cargo,
                        'fechacontrata': date(2020, 1, 1)
                    }
                )
                
                if created:
                    self.stdout.write(f'Info laboral creada: {persona.nombre} → {cargo.cargo}')
                else:
                    self.stdout.write(f'Info laboral ya existe: {persona.nombre} → {cargo.cargo}')
                    
            except Exception as e:
                self.stdout.write(f'Error creando info laboral para {nombre_completo}: {e}')

    def crear_asignaciones_faena(self):
        """Crea asignaciones de faena para el personal"""
        try:
            # Obtener faena y turno
            faena = Faena.objects.filter(activo=True).first()
            turno = Turno.objects.filter(activo=True).first()
            
            if not faena or not turno:
                self.stdout.write('No hay faenas o turnos activos para crear asignaciones')
                return
            
            # Obtener primer bloque del turno
            bloque_inicio = TurnoBloque.objects.filter(turno=turno, orden=1).first()
            if not bloque_inicio:
                self.stdout.write('No hay bloques en el turno')
                return
            
            # Asignar personal a faenas
            personal_activo = Personal.objects.filter(activo=True)
            
            for persona in personal_activo:
                # Alternar entre faenas si hay más de una
                faena_asignar = faena
                if Faena.objects.filter(activo=True).count() > 1:
                    # Asignar COLLAHUASI a los primeros, QUEBRADA BLANCA a los últimos
                    if persona.personal_id % 2 == 0:
                        faena_asignar = Faena.objects.filter(activo=True).last()
                
                asignacion, created = AsignacionFaena.objects.get_or_create(
                    personal=persona,
                    defaults={
                        'faena': faena_asignar,
                        'turno': turno,
                        'fecha_inicio': date(2025, 1, 1),
                        'bloque_inicio': bloque_inicio,
                        'activo': True
                    }
                )
                
                if created:
                    self.stdout.write(f'Asignación creada: {persona.nombre} → {faena_asignar.nombre}')
                else:
                    self.stdout.write(f'Asignación ya existe para {persona.nombre}')
                    
        except Exception as e:
            self.stdout.write(f'Error creando asignaciones de faena: {e}')
