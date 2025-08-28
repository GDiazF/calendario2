from django.shortcuts import render
from datetime import datetime

# Create your views here.

def calendario_mensual(request):
    """Vista para mostrar el calendario mensual"""
    # Obtener fecha actual
    now = datetime.now()
    current_month = now.strftime('%B')  # Nombre del mes en inglés
    current_year = now.year
    
    # Convertir nombre del mes a español
    month_names = {
        'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
        'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
        'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
        'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
    }
    
    context = {
        'current_month': month_names.get(current_month, current_month),
        'current_year': current_year,
    }
    
    return render(request, 'calendario/calendario_mensual.html', context)
