"""
Script de prueba simple para verificar la lógica de horarios por doctora
No requiere conexión a Google Sheets
Fecha: 09/03/2026
"""

from datetime import datetime

def get_available_hours_for_date(fecha_str: str, doctora: str = None):
    """
    Simula la función get_available_hours_for_date de google_sheets_client.py
    """
    try:
        # Parsear fecha
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
        dia_semana = fecha.strftime('%A')  # Monday, Tuesday, etc.
        dia_numero = fecha.weekday()  # 0=Monday, 1=Tuesday, etc.
        
        # Determinar horarios según día de la semana
        if dia_semana == 'Saturday':
            # Sábados: 8:00 - 12:00 (última cita 11:30)
            horas = []
            for hora in range(8, 12):
                horas.append(f"{hora:02d}:00")
                horas.append(f"{hora:02d}:30")
            return horas
        
        # Lunes a Viernes: 8:00 - 12:00 y 14:00 - 17:00
        horas = []
        
        # Mañana: 8:00 - 12:00 (última cita 11:30)
        for hora in range(8, 12):
            horas.append(f"{hora:02d}:00")
            horas.append(f"{hora:02d}:30")
        
        # Tarde: 14:00 - 17:00+
        # Determinar última hora según doctora y día
        ultima_hora = "17:00"  # Por defecto
        
        if doctora:
            doctora_lower = doctora.lower()
            if doctora_lower == "sandra":
                # Doctora Sandra
                if dia_numero in [0, 1, 2]:  # Lunes, Martes, Miércoles
                    # Sale a las 17:00, última cita 16:30
                    ultima_hora = "16:30"
                else:  # Jueves, Viernes
                    # Sale a las 17:30, última cita 17:00
                    ultima_hora = "17:00"
            elif doctora_lower == "zaida":
                # Doctora Zaida: sale a las 17:30, última cita 17:00
                ultima_hora = "17:00"
        
        # Agregar horarios de tarde hasta la última hora permitida
        for hora in range(14, 18):
            hora_str = f"{hora:02d}:00"
            if hora_str <= ultima_hora:
                horas.append(hora_str)
            
            hora_media_str = f"{hora:02d}:30"
            if hora_media_str <= ultima_hora:
                horas.append(hora_media_str)
        
        return horas
        
    except Exception as e:
        print(f"❌ Error obteniendo horas disponibles: {str(e)}")
        return []

def test_horarios():
    """Prueba los horarios para diferentes doctoras y días"""
    
    print("="*80)
    print("🧪 PRUEBA DE HORARIOS POR DOCTORA (SIN CONEXIÓN A GOOGLE SHEETS)")
    print("="*80)
    print()
    
    # Fechas de prueba
    fechas_prueba = [
        ("2026-03-09", "Lunes", 0),
        ("2026-03-10", "Martes", 1),
        ("2026-03-11", "Miércoles", 2),
        ("2026-03-12", "Jueves", 3),
        ("2026-03-13", "Viernes", 4),
        ("2026-03-14", "Sábado", 5),
    ]
    
    doctoras = ["Sandra", "Zaida"]
    
    for doctora in doctoras:
        print(f"\n{'='*80}")
        print(f"👩‍⚕️ DOCTORA: {doctora.upper()}")
        print(f"{'='*80}\n")
        
        for fecha_str, dia_nombre, dia_numero in fechas_prueba:
            print(f"📅 {dia_nombre} {fecha_str}")
            print("-" * 40)
            
            horas = get_available_hours_for_date(fecha_str, doctora)
            
            if not horas:
                print("   ❌ No hay horarios disponibles")
                continue
            
            # Separar mañana y tarde
            manana = [h for h in horas if int(h.split(':')[0]) < 12]
            tarde = [h for h in horas if int(h.split(':')[0]) >= 14]
            
            print(f"   🌅 Mañana ({len(manana)} horarios):")
            print(f"      {', '.join(manana)}")
            
            if tarde:
                print(f"   🌆 Tarde ({len(tarde)} horarios):")
                print(f"      {', '.join(tarde)}")
                print(f"   ⏰ Última hora: {tarde[-1]}")
            else:
                print(f"   🌆 Tarde: Sin horarios (Sábado)")
            
            # Validaciones
            errores = []
            
            # Verificar que no haya 12:00
            if "12:00" in horas:
                errores.append("No debería haber horario a las 12:00")
            
            # Verificar última hora de mañana
            if manana and manana[-1] != "11:30":
                errores.append(f"Última hora de mañana debería ser 11:30, es {manana[-1]}")
            
            # Verificar horarios de tarde según doctora y día
            if dia_numero == 5:  # Sábado
                if tarde:
                    errores.append("Sábado no debería tener horarios de tarde")
            else:
                if doctora.lower() == "sandra":
                    if dia_numero in [0, 1, 2]:  # Lunes-Miércoles
                        if tarde and tarde[-1] != "16:30":
                            errores.append(f"Sandra {dia_nombre} debería terminar a las 16:30, termina a las {tarde[-1]}")
                    else:  # Jueves-Viernes
                        if tarde and tarde[-1] != "17:00":
                            errores.append(f"Sandra {dia_nombre} debería terminar a las 17:00, termina a las {tarde[-1]}")
                
                elif doctora.lower() == "zaida":
                    if tarde and tarde[-1] != "17:00":
                        errores.append(f"Zaida debería terminar a las 17:00, termina a las {tarde[-1]}")
            
            # Mostrar resultado
            if errores:
                print(f"   ❌ ERRORES ENCONTRADOS:")
                for error in errores:
                    print(f"      - {error}")
            else:
                print(f"   ✅ CORRECTO: Todos los horarios son válidos")
            
            print()
    
    print("\n" + "="*80)
    print("✅ PRUEBA COMPLETADA")
    print("="*80)
    print()
    print("📊 RESUMEN DE HORARIOS ESPERADOS:")
    print()
    print("| Doctora | Día         | Mañana      | Tarde       | Total |")
    print("|---------|-------------|-------------|-------------|-------|")
    print("| Sandra  | Lun-Mié     | 08:00-11:30 | 14:00-16:30 | 15    |")
    print("| Sandra  | Jue-Vie     | 08:00-11:30 | 14:00-17:00 | 16    |")
    print("| Sandra  | Sábado      | 08:00-11:30 | -           | 8     |")
    print("| Zaida   | Lun-Vie     | 08:00-11:30 | 14:00-17:00 | 16    |")
    print("| Zaida   | Sábado      | 08:00-11:30 | -           | 8     |")
    print()

if __name__ == "__main__":
    test_horarios()
