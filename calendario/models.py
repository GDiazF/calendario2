from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, CheckConstraint, F
from datetime import datetime, timedelta
# Create your models here.

class Personal(models.Model):
    personal_id = models.AutoField(primary_key=True, null=False, blank=False)
    rut = models.CharField(max_length=8, null=False, blank=False, unique=True)
    dvrut = models.CharField(max_length=1, null=False, blank=False)
    nombre = models.CharField(max_length=100, null=False, blank=False)
    apepat = models.CharField(max_length=50, null=False, blank=False)
    apemat = models.CharField(max_length=50)
    fechanac = models.DateField(null=True, blank=True)
    correo = models.CharField(max_length=100, null=False, blank=False, unique=True)
    direccion = models.CharField(max_length=150, null=True, blank=True)
    activo = models.BooleanField(default=True, verbose_name='Estado')

    class Meta:
        verbose_name = 'Personal'
        verbose_name_plural = 'Personal'
        db_table = 'personal'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class DeptoEmpresa(models.Model):
    depto_id = models.AutoField(primary_key=True, blank=False, null=False)
    depto = models.CharField(max_length=50, db_column='depto', blank=False, null=False)

    def __str__(self):
        return self.depto


class Cargo(models.Model):
    cargo_id = models.AutoField(primary_key=True, blank=False, null=False)
    depto_id = models.ForeignKey(DeptoEmpresa, on_delete=models.CASCADE, db_column='depto_id', blank=False, null=False)
    cargo = models.CharField(max_length=50, db_column='cargo', blank=False, null=False)

    def __str__(self):
        return self.cargo


class InfoLaboral(models.Model):
    infolab_id = models.AutoField(primary_key=True, null=False, blank=False)
    personal_id = models.ForeignKey(Personal, on_delete=models.CASCADE, db_column='personal_id', null=False, blank=False)
    depto_id = models.ForeignKey(DeptoEmpresa, on_delete=models.CASCADE, db_column='depto_id', null=False, blank=False)
    cargo_id = models.ForeignKey(Cargo, on_delete=models.CASCADE, db_column='cargo_id',blank=False, null=False)
    fechacontrata = models.DateField(blank=False, null=False)


class TipoAusentismo(models.Model):
    tipoausen_id = models.AutoField(primary_key=True, null=False, blank=False)
    tipo = models.CharField(max_length=100, null=False, blank=False, db_column='tipo' )

    def __str__(self):
        return self.tipo


class Ausentismo(models.Model):
    ausentismo_id = models.AutoField(primary_key=True, null=False, blank=False)
    tipoausen_id = models.ForeignKey(TipoAusentismo, on_delete=models.CASCADE, db_column='tipoausen_id', null=False, blank=False)
    personal_id = models.ForeignKey(Personal, on_delete=models.CASCADE, db_column='personal_id', null=False, blank=False)
    fechaini = models.DateField(null=False, blank=False)
    fechafin = models.DateField(null=False, blank=False)
    observacion = models.TextField(max_length=250, blank=True, null=True)

    def __str__(self):
        trabajador = f"{self.personal_id.nombre} {self.personal_id.apepat} {self.personal_id.apemat}"
        return f"{self.tipoausen_id} - {trabajador} ({self.fechaini} a {self.fechafin})"


class TipoLicenciaMedica(models.Model):
    tipoLicenciaMedica_id = models.AutoField(primary_key=True, null=False, blank=False)
    tipoLicenciaMedica = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.tipoLicenciaMedica

class LicenciaMedicaPorPersonal(models.Model):
    licenciaMedicaPorPersonal_id = models.AutoField(primary_key=True, null=False, blank=False)
    personal_id = models.ForeignKey(Personal, on_delete=models.CASCADE, db_column='personal_id', null=False, blank=False)
    tipoLicenciaMedica_id = models.ForeignKey(TipoLicenciaMedica, on_delete=models.CASCADE, db_column='tipoLicenciaMedica_id', null=False, blank=False)
    fechaEmision = models.DateField(null=False, blank=False)
    fecha_fin_licencia = models.DateField(null=False, blank=False, help_text="Fecha de fin de la licencia médica")
    observacion = models.TextField(max_length=250, null=True, blank=True)


#MODELOS NUEVOS PARA CALENDARIO Y TENER ESTADOS DINAMICOS


#1 ESTADOS DINAMICOS
class Estado(models.Model):
    """
    Estado configurable desde admin. Ejemplos: 'Día', 'Noche', 'Descanso',
    'Licencia', 'Permiso', 'Vacaciones', 'Disponible', etc.
    """
    nombre = models.CharField(max_length=100, unique=True)
    nombre_corto = models.CharField(
        max_length=10, 
        blank=True, 
        null=True,
        help_text="Nombre corto para mostrar en el calendario (ej: 'D' para 'Día', 'N' para 'Noche')"
    )
    color = models.CharField(
        max_length=7,
        help_text="Color HEX para el texto del estado (ej: #0EA5E9)"
    )
    background_color = models.CharField(
        max_length=7,
        help_text="Color HEX para el fondo del estado (ej: #0EA5E9)"
    )
    prioridad = models.PositiveIntegerField(
        default=10,
        help_text="Mayor número => mayor prioridad si hay conflicto"
    )
    es_bloqueante = models.BooleanField(
        default=False,
        help_text="Si es True, este estado siempre sobreescribe cualquier otro que coincida"
    )
    es_predeterminado = models.BooleanField(
        default=False,
        help_text="Si es True, este será el estado por defecto cuando no haya asignaciones"
    )
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["-activo", "-prioridad", "nombre"]
        verbose_name = "Estado"
        verbose_name_plural = "Estados"
        constraints = [
            CheckConstraint(
                check=Q(es_predeterminado=False) | Q(es_predeterminado=True),
                name='solo_un_estado_predeterminado'
            )
        ]

    def clean(self):
        """Validar que solo haya un estado predeterminado"""
        if self.es_predeterminado:
            # Verificar si ya existe otro estado predeterminado
            otros_predeterminados = Estado.objects.filter(
                es_predeterminado=True,
                activo=True
            ).exclude(pk=self.pk)
            
            if otros_predeterminados.exists():
                raise ValidationError(
                    'Ya existe otro estado marcado como predeterminado. '
                    'Solo puede haber un estado predeterminado a la vez.'
                )

    def save(self, *args, **kwargs):
        """Asegurar que solo haya un estado predeterminado"""
        if self.es_predeterminado:
            # Desmarcar otros estados predeterminados
            Estado.objects.filter(
                es_predeterminado=True
            ).exclude(pk=self.pk).update(es_predeterminado=False)
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

class EstadoFuente(models.Model):
    """
    Mapea un Estado a una FUENTE EXTERNA de datos (cualquier modelo),
    para poder consultar si la persona está en ese estado por rangos de fechas,
    SIN tocar código.

    Ejemplos:
    - Estado 'Permiso' -> content_type = Ausentismo, campo_inicio='desde', campo_fin='hasta', campo_personal='personal'
    - Estado 'Licencia' -> content_type = LicenciaMedica, campo_inicio='inicio', campo_fin='fin'
    """
    estado = models.OneToOneField(Estado, on_delete=models.CASCADE, related_name="fuente")
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE,
        help_text="Modelo origen (ej: Ausentismo, LicenciaMedica, etc.)"
    )
    campo_fecha_inicio = models.CharField(max_length=50, default="fecha_inicio")
    campo_fecha_fin = models.CharField(max_length=50, default="fecha_fin")
    campo_personal = models.CharField(max_length=50, default="personal")
    # Filtro extra opcional como JSON simple (texto) para casos especiales (ej: tipo='Permiso')
    filtro_extra = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = "Fuente de Estado"
        verbose_name_plural = "Fuentes de Estados"

    def __str__(self):
        return f"Fuente({self.estado.nombre}) → {self.content_type.app_label}.{self.content_type.model}"

#2 TURNOS Y CICLOS
class Turno(models.Model):
    """
    Turno configurable, p. ej. '7x7', '7x7x7x7', '5x2', '15x15', o personalizados.
    NO define la secuencia en sí; la secuencia vive en TurnoBloque.
    """
    nombre = models.CharField(max_length=120, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"

    def __str__(self):
        return self.nombre

    @property
    def longitud_ciclo(self) -> int:
        """
        Suma total de días del ciclo (ej: 7+7+7+7 = 28).
        """
        return sum(self.bloques.values_list("duracion_dias", flat=True))

class TurnoBloque(models.Model):
    """
    Cada bloque del turno con su duración y el Estado que representa.
    Ejemplo para '7x7x7x7':
      - orden=1, duracion_dias=7, estado='Día'
      - orden=2, duracion_dias=7, estado='Descanso'
      - orden=3, duracion_dias=7, estado='Noche'
      - orden=4, duracion_dias=7, estado='Descanso'
    """
    turno = models.ForeignKey(Turno, on_delete=models.CASCADE, related_name="bloques")
    orden = models.PositiveIntegerField(help_text="Posición del bloque dentro del ciclo (1..n)")
    duracion_dias = models.PositiveIntegerField()
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, related_name="bloques_turno")

    class Meta:
        ordering = ["turno", "orden"]
        unique_together = [("turno", "orden")]
        verbose_name = "Bloque de Turno"
        verbose_name_plural = "Bloques de Turno"

    def __str__(self):
        return f"{self.turno.nombre} · bloque {self.orden} · {self.estado.nombre} ({self.duracion_dias}d)"


#3 FAENAS Y ASIGNACIONES


class Faena(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    ubicacion = models.CharField(max_length=200, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Faena"
        verbose_name_plural = "Faenas"

    def __str__(self):
        return self.nombre



class AsignacionFaena(models.Model):
    """
    Asigna una persona a una faena + turno, con fecha de inicio y (opcional) fin.
    El 'bloque_inicio' permite definir con qué parte del ciclo comienza (día, noche, descanso, etc.).
    """
    personal = models.ForeignKey("Personal", on_delete=models.CASCADE, related_name="asignaciones_faena", db_index=True)
    faena = models.ForeignKey(Faena, on_delete=models.CASCADE, related_name="asignaciones", db_index=True)
    turno = models.ForeignKey(Turno, on_delete=models.CASCADE, related_name="asignaciones", db_index=True)

    fecha_inicio = models.DateField(db_index=True)
    fecha_fin = models.DateField(blank=True, null=True, db_index=True)

    bloque_inicio = models.ForeignKey(
        TurnoBloque,
        on_delete=models.CASCADE,
        related_name="asignaciones_inicio",
        help_text="Bloque del turno desde el cual arranca el ciclo para esta persona"
    )

    observaciones = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["personal", "fecha_inicio"]
        verbose_name = "Asignación a Faena"
        verbose_name_plural = "Asignaciones a Faenas"
        indexes = [
            models.Index(fields=["personal", "fecha_inicio", "fecha_fin"]),
            models.Index(fields=["faena", "turno"]),
        ]
        constraints = [
            CheckConstraint(
                check=Q(fecha_fin__gte=F("fecha_inicio")) | Q(fecha_fin__isnull=True),
                name="asig_faena_rango_valido",
            )
        ]

    def __str__(self):
        ffin = self.fecha_fin or "∼"
        return f"{self.personal} → {self.faena} [{self.turno}] {self.fecha_inicio} → {ffin}"

    def clean(self):
        # Validación: el bloque_inicio debe pertenecer al turno
        if self.bloque_inicio and self.bloque_inicio.turno_id != self.turno_id:
            raise ValidationError({"bloque_inicio": _("El bloque de inicio no pertenece al turno asignado.")})

    def obtener_estado_en_fecha(self, fecha):
        """
        Calcula el estado de la persona en una fecha específica basado en el turno.
        Retorna el Estado correspondiente.
        """
        if not self.activo or fecha < self.fecha_inicio:
            return None
        
        if self.fecha_fin and fecha > self.fecha_fin:
            return None
        
        # Calcular días transcurridos desde el inicio
        dias_transcurridos = (fecha - self.fecha_inicio).days
        
        # Encontrar el bloque correspondiente
        longitud_ciclo = self.turno.longitud_ciclo
        if longitud_ciclo == 0:
            return None
        
        # Calcular posición en el ciclo
        posicion_ciclo = dias_transcurridos % longitud_ciclo
        
        # Encontrar el bloque que corresponde a esa posición
        bloques = self.turno.bloques.all().order_by('orden')
        
        # Ajustar por bloque_inicio si está configurado
        offset_inicio = 0
        if self.bloque_inicio:
            # Calcular el offset basado en el bloque de inicio
            for bloque in bloques:
                if bloque.orden < self.bloque_inicio.orden:
                    offset_inicio += bloque.duracion_dias
                else:
                    break
        
        # Ajustar la posición del ciclo con el offset
        posicion_ajustada = (posicion_ciclo + offset_inicio) % longitud_ciclo
        
        # Encontrar el bloque que corresponde a esa posición ajustada
        dias_acumulados = 0
        for bloque in bloques:
            if posicion_ajustada < dias_acumulados + bloque.duracion_dias:
                return bloque.estado
            dias_acumulados += bloque.duracion_dias
        
        return None


#4 ESTADOS MANUALES

class EstadoManual(models.Model):
    """
    Permite fijar un estado manual por rango (sobrescribe según prioridad/bloqueo).
    Útil para casos puntuales sin depender de otras tablas.
    """
    personal = models.ForeignKey("Personal", on_delete=models.CASCADE, related_name="estados_manuales", db_index=True)
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT, related_name="aplicaciones_manuales", db_index=True)
    fecha_inicio = models.DateField(db_index=True)
    fecha_fin = models.DateField(db_index=True)
    motivo = models.CharField(max_length=200, blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["personal", "fecha_inicio"]
        verbose_name = "Estado Manual"
        verbose_name_plural = "Estados Manuales"
        indexes = [
            models.Index(fields=["personal", "fecha_inicio", "fecha_fin"]),
        ]
        constraints = [
            CheckConstraint(
                check=Q(fecha_fin__gte=F("fecha_inicio")),
                name="estado_manual_rango_valido",
            )
        ]

    def __str__(self):
        return f"{self.personal} · {self.estado.nombre} · {self.fecha_inicio} → {self.fecha_fin}"

#5 MÉTODO UTILITARIO PARA CALCULAR ESTADO FINAL
def obtener_estado_final_personal_fecha(personal, fecha):
    """
    Método utilitario que calcula el estado final de una persona en una fecha,
    considerando todas las fuentes y prioridades.
    
    Orden de prioridad:
    1. Estados manuales (más alta prioridad)
    2. Estados de fuentes externas (según prioridad del estado)
    3. Estados derivados de turnos (más baja prioridad)
    
    Retorna una lista de estados cuando hay conflictos de prioridad.
    """
    from django.db.models import Q
    
    # 1. Buscar estados manuales activos
    estados_manuales = EstadoManual.objects.filter(
        personal=personal,
        fecha_inicio__lte=fecha,
        fecha_fin__gte=fecha,
        activo=True
    ).select_related('estado').order_by('-estado__prioridad')
    
    if estados_manuales.exists():
        # Si hay estados bloqueantes, retornar el de mayor prioridad
        bloqueantes = [em for em in estados_manuales if em.estado.es_bloqueante]
        if bloqueantes:
            return [bloqueantes[0].estado]
        # Si no hay bloqueantes, retornar el de mayor prioridad
        return [estados_manuales.first().estado]
    
    # 2. Buscar estados de fuentes externas
    estados_fuente = []
    for estado_fuente in EstadoFuente.objects.select_related('estado', 'content_type').all():
        if not estado_fuente.estado.activo:
            continue
            
        # Construir consulta dinámica
        modelo = estado_fuente.content_type.model_class()
        if not modelo:
            continue
            
        filtros = Q(**{
            f"{estado_fuente.campo_personal}": personal,
            f"{estado_fuente.campo_fecha_inicio}__lte": fecha,
            f"{estado_fuente.campo_fecha_fin}__gte": fecha,
        })
        
        # Aplicar filtros extra si existen
        if estado_fuente.filtro_extra:
            for campo, valor in estado_fuente.filtro_extra.items():
                filtros &= Q(**{campo: valor})
        
        if modelo.objects.filter(filtros).exists():
            estados_fuente.append(estado_fuente.estado)
    
    # 3. Buscar estado derivado de turno
    estado_turno = None
    asignaciones_activas = AsignacionFaena.objects.filter(
        personal=personal,
        fecha_inicio__lte=fecha,
        activo=True
    ).filter(
        Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=fecha)
    ).select_related('turno').first()
    
    if asignaciones_activas:
        estado_turno = asignaciones_activas.obtener_estado_en_fecha(fecha)
    
    # 4. Resolver conflictos de prioridad
    todos_estados = []
    
    # Debug: mostrar qué estados se encontraron
    print(f"DEBUG PRIORIDADES: {personal.nombre} - {fecha}")
    print(f"  Estados de fuente: {[e.nombre for e in estados_fuente]}")
    print(f"  Estado de turno: {estado_turno.nombre if estado_turno else 'None'}")
    
    # Agregar estados de fuentes externas
    for estado in estados_fuente:
        todos_estados.append({
            'estado': estado,
            'tipo': 'fuente',
            'prioridad': estado.prioridad
        })
    
    # Agregar estado de turno si existe
    if estado_turno:
        todos_estados.append({
            'estado': estado_turno,
            'tipo': 'turno',
            'prioridad': estado_turno.prioridad
        })
    
    if not todos_estados:
        # Si no hay nada, retornar estado por defecto
        try:
            estado_predeterminado = Estado.objects.filter(
                activo=True,
                es_predeterminado=True
            ).first()
            
            if estado_predeterminado:
                return [estado_predeterminado]
            
            return []
        except:
            return []
    
    # Ordenar por prioridad (mayor número = mayor prioridad)
    todos_estados.sort(key=lambda x: x['prioridad'], reverse=True)
    
    # Si hay estados bloqueantes, solo retornar el de mayor prioridad
    bloqueantes = [x for x in todos_estados if x['estado'].es_bloqueante]
    if bloqueantes:
        return [bloqueantes[0]['estado']]
    
    # Obtener la prioridad más alta
    prioridad_maxima = todos_estados[0]['prioridad']
    
    # Retornar todos los estados que tengan la prioridad más alta
    estados_misma_prioridad = [
        x['estado'] for x in todos_estados 
        if x['prioridad'] == prioridad_maxima
    ]
    
    # Debug: imprimir para verificar
    print(f"DEBUG: {personal.nombre} - {fecha}")
    estados_info = [f"{x['estado'].nombre}({x['prioridad']})" for x in todos_estados]
    print(f"  Estados encontrados: {estados_info}")
    print(f"  Prioridad máxima: {prioridad_maxima}")
    print(f"  Estados seleccionados: {[e.nombre for e in estados_misma_prioridad]}")
    
    return estados_misma_prioridad

def obtener_calendario_mensual(anio, mes, personal_filtro=None):
    """
    Obtiene el calendario completo para un mes específico.
    
    Args:
        anio: Año (ej: 2025)
        mes: Mes (1-12)
        personal_filtro: QuerySet opcional para filtrar personal
    
    Returns:
        dict con estructura: {
            'personal': [lista de personal],
            'estados': {personal_id: {dia: estado}}
        }
    """
    from datetime import date
    from calendar import monthrange
    
    # Obtener rango de fechas del mes
    _, ultimo_dia = monthrange(anio, mes)
    fecha_inicio = date(anio, mes, 1)
    fecha_fin = date(anio, mes, ultimo_dia)
    
    # Obtener personal activo
    if personal_filtro is None:
        personal = Personal.objects.filter(activo=True).order_by('nombre')
    else:
        personal = personal_filtro.filter(activo=True).order_by('nombre')
    
    # Inicializar estructura de resultados
    calendario = {
        'personal': list(personal),
        'estados': {},
        'fechas': [fecha_inicio + timedelta(days=i) for i in range(ultimo_dia)]
    }
    
    # Calcular estado para cada persona en cada día
    for persona in personal:
        calendario['estados'][persona.personal_id] = {}
        
        for fecha in calendario['fechas']:
            estados = obtener_estado_final_personal_fecha(persona, fecha)
            calendario['estados'][persona.personal_id][fecha.day] = estados
    
    return calendario
