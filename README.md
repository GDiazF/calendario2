# Calendario Mensual - Proyecto Django

Este es un proyecto Django que implementa un calendario mensual horizontal con las siguientes características:

## Características

- **Calendario mensual horizontal**: Muestra todos los días del mes en formato de tabla
- **Navegación por meses y años**: Botones para navegar entre diferentes períodos
- **Botón "Hoy"**: Permite volver rápidamente al mes actual
- **Lista de personal**: Panel izquierdo que muestra la lista del personal
- **Vista por usuario**: Cada fila del calendario representa una persona del personal
- **Diseño responsive**: Se adapta a diferentes tamaños de pantalla

## Estructura del Proyecto

```
calendario nuevo/
├── core/                   # Proyecto principal Django
│   ├── settings.py        # Configuración del proyecto
│   ├── urls.py           # URLs principales
│   └── ...
├── calendario/            # App del calendario
│   ├── templates/         # Templates HTML
│   │   └── calendario/
│   │       └── calendario_mensual.html
│   ├── views.py          # Vistas de la app
│   ├── urls.py           # URLs de la app
│   └── ...
├── manage.py             # Script de gestión de Django
├── requirements.txt      # Dependencias del proyecto
└── README.md            # Este archivo
```

## Instalación y Ejecución

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar migraciones (opcional, ya que no hay modelos)
```bash
python manage.py migrate
```

### 3. Ejecutar el servidor de desarrollo
```bash
python manage.py runserver
```

### 4. Acceder a la aplicación
Abre tu navegador y ve a: `http://127.0.0.1:8000/calendario/`

## Funcionalidades del Calendario

### Navegación
- **Mes Anterior/Siguiente**: Navega entre meses
- **Año Anterior/Siguiente**: Navega entre años
- **Botón "Hoy"**: Regresa al mes actual

### Vista del Calendario
- **Panel izquierdo**: Lista del personal con nombres y roles
- **Calendario principal**: Tabla horizontal con días del mes
- **Celdas interactivas**: Cada celda representa un día para una persona específica
- **Días especiales**: Los fines de semana y el día actual tienen estilos diferenciados

### Personal de Ejemplo
El template incluye 8 personas de ejemplo:
- Juan Pérez (Desarrollador)
- María García (Diseñadora)
- Carlos López (Analista)
- Ana Martínez (Gerente)
- Luis Rodríguez (Técnico)
- Sofia Torres (Asistente)
- Roberto Silva (Consultor)
- Carmen Vega (Coordinadora)

## Tecnologías Utilizadas

- **Backend**: Django 5.1.2
- **Base de datos**: SQLite3 (por defecto)
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **Estilos**: CSS personalizado con gradientes y efectos hover
- **Responsive**: Diseño adaptable a diferentes dispositivos

## Personalización

Para personalizar el calendario:

1. **Agregar/remover personal**: Modifica el array `personal` en el JavaScript del template
2. **Cambiar colores**: Modifica las variables CSS en el `<style>` del template
3. **Agregar funcionalidades**: Extiende el JavaScript para incluir más características
4. **Integrar con modelos**: Conecta el template con modelos Django para datos dinámicos

## Notas

- Este template funciona completamente sin modelos Django
- Los datos del personal están hardcodeados en el JavaScript
- El calendario se genera dinámicamente con JavaScript
- No se requiere base de datos para funcionar
