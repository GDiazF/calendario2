from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Personal, DeptoEmpresa, Cargo, InfoLaboral,
    TipoAusentismo, Ausentismo, TipoLicenciaMedica, LicenciaMedicaPorPersonal,
    Estado, EstadoFuente, Turno, TurnoBloque, Faena, AsignacionFaena, EstadoManual
)

# ============================================================================
# ADMIN PARA MODELOS EXISTENTES
# ============================================================================

@admin.register(Personal)
class PersonalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apepat', 'apemat', 'rut', 'correo', 'activo']
    list_filter = ['activo', 'fechanac']
    search_fields = ['nombre', 'apepat', 'apemat', 'rut', 'correo']
    ordering = ['nombre', 'apepat']

@admin.register(DeptoEmpresa)
class DeptoEmpresaAdmin(admin.ModelAdmin):
    list_display = ['depto']
    search_fields = ['depto']

@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ['cargo', 'depto_id']
    list_filter = ['depto_id']
    search_fields = ['cargo']

@admin.register(InfoLaboral)
class InfoLaboralAdmin(admin.ModelAdmin):
    list_display = ['personal_id', 'depto_id', 'cargo_id', 'fechacontrata']
    list_filter = ['depto_id', 'cargo_id', 'fechacontrata']
    search_fields = ['personal_id__nombre', 'personal_id__apepat']

@admin.register(TipoAusentismo)
class TipoAusentismoAdmin(admin.ModelAdmin):
    list_display = ['tipo']
    search_fields = ['tipo']

@admin.register(Ausentismo)
class AusentismoAdmin(admin.ModelAdmin):
    list_display = ['personal_id', 'tipoausen_id', 'fechaini', 'fechafin', 'observacion']
    list_filter = ['tipoausen_id', 'fechaini', 'fechafin']
    search_fields = ['personal_id__nombre', 'personal_id__apepat', 'observacion']
    date_hierarchy = 'fechaini'

@admin.register(TipoLicenciaMedica)
class TipoLicenciaMedicaAdmin(admin.ModelAdmin):
    list_display = ['tipoLicenciaMedica']
    search_fields = ['tipoLicenciaMedica']

@admin.register(LicenciaMedicaPorPersonal)
class LicenciaMedicaPorPersonalAdmin(admin.ModelAdmin):
    list_display = ['personal_id', 'tipoLicenciaMedica_id', 'fechaEmision', 'fecha_fin_licencia', 'observacion']
    list_filter = ['tipoLicenciaMedica_id', 'fechaEmision', 'fecha_fin_licencia']
    search_fields = ['personal_id__nombre', 'personal_id__apepat', 'observacion']
    date_hierarchy = 'fechaEmision'

# ============================================================================
# ADMIN PARA MODELOS NUEVOS DEL CALENDARIO
# ============================================================================

@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'nombre_corto', 'color_preview', 'background_color_preview', 'prioridad', 'es_bloqueante', 'es_predeterminado', 'activo']
    list_filter = ['activo', 'es_bloqueante', 'es_predeterminado', 'prioridad']
    search_fields = ['nombre', 'nombre_corto']
    ordering = ['-activo', '-prioridad', 'nombre']
    
    def color_preview(self, obj):
        if obj.color:
            return format_html(
                '<div style="background-color: {}; width: 30px; height: 20px; border: 1px solid #ccc; border-radius: 3px;"></div>',
                obj.color
            )
        return "-"
    color_preview.short_description = "Color Texto"
    
    def background_color_preview(self, obj):
        if obj.background_color:
            return format_html(
                '<div style="background-color: {}; width: 30px; height: 20px; border: 1px solid #ccc; border-radius: 3px;"></div>',
                obj.background_color
            )
        return "-"
    background_color_preview.short_description = "Color Fondo"

@admin.register(EstadoFuente)
class EstadoFuenteAdmin(admin.ModelAdmin):
    list_display = ['estado', 'content_type', 'campo_fecha_inicio', 'campo_fecha_fin', 'campo_personal']
    list_filter = ['estado__activo', 'content_type']
    search_fields = ['estado__nombre']
    ordering = ['estado__nombre']

class TurnoBloqueInline(admin.TabularInline):
    model = TurnoBloque
    extra = 1
    ordering = ['orden']
    fields = ['orden', 'duracion_dias', 'estado']

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'longitud_ciclo', 'activo', 'descripcion_short']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']
    inlines = [TurnoBloqueInline]
    
    def descripcion_short(self, obj):
        if obj.descripcion:
            return obj.descripcion[:50] + "..." if len(obj.descripcion) > 50 else obj.descripcion
        return "-"
    descripcion_short.short_description = "Descripción"

@admin.register(TurnoBloque)
class TurnoBloqueAdmin(admin.ModelAdmin):
    list_display = ['turno', 'orden', 'duracion_dias', 'estado', 'estado_color_preview']
    list_filter = ['turno', 'estado', 'estado__activo']
    ordering = ['turno', 'orden']
    search_fields = ['turno__nombre', 'estado__nombre']
    
    def estado_color_preview(self, obj):
        if obj.estado and obj.estado.background_color:
            return format_html(
                '<div style="background-color: {}; color: {}; padding: 2px 6px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</div>',
                obj.estado.background_color,
                obj.estado.color,
                obj.estado.nombre
            )
        return obj.estado.nombre if obj.estado else "-"
    estado_color_preview.short_description = "Vista Previa"

@admin.register(Faena)
class FaenaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ubicacion', 'activo', 'descripcion_short']
    list_filter = ['activo']
    search_fields = ['nombre', 'ubicacion', 'descripcion']
    ordering = ['nombre']
    
    def descripcion_short(self, obj):
        if obj.descripcion:
            return obj.descripcion[:50] + "..." if len(obj.descripcion) > 50 else obj.descripcion
        return "-"
    descripcion_short.short_description = "Descripción"

@admin.register(AsignacionFaena)
class AsignacionFaenaAdmin(admin.ModelAdmin):
    list_display = ['personal', 'faena', 'turno', 'fecha_inicio', 'fecha_fin', 'bloque_inicio', 'activo']
    list_filter = ['activo', 'faena', 'turno', 'fecha_inicio', 'fecha_fin']
    search_fields = ['personal__nombre', 'personal__apepat', 'faena__nombre', 'turno__nombre']
    date_hierarchy = 'fecha_inicio'
    ordering = ['personal', 'fecha_inicio']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('personal', 'faena', 'turno', 'bloque_inicio')

@admin.register(EstadoManual)
class EstadoManualAdmin(admin.ModelAdmin):
    list_display = ['personal', 'estado', 'fecha_inicio', 'fecha_fin', 'motivo', 'activo', 'creado_en']
    list_filter = ['activo', 'estado', 'fecha_inicio', 'fecha_fin', 'creado_en']
    search_fields = ['personal__nombre', 'personal__apepat', 'motivo']
    date_hierarchy = 'fecha_inicio'
    ordering = ['personal', 'fecha_inicio']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('personal', 'estado')

# ============================================================================
# PERSONALIZACIÓN DEL SITE ADMIN
# ============================================================================

admin.site.site_header = "Administración del Calendario de Planificación"
admin.site.site_title = "Calendario Admin"
admin.site.index_title = "Panel de Control del Calendario"
