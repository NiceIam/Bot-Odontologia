"""
Script de prueba para verificar los horarios por doctora
Fecha: 09/03/2026
"""

from datetime import datetime
from google_sheets_client import get_sheets_client

def test_horarios_por_doctora():
    """Prueba los horarios generados para cada doctora y día"""
    
    print("🧪 PRUEBA DE HORARIOS POR DOCTORA")
    print("="*80)
    
    try:
        sheets_client = get_sheets_client()
        print("✅ Cliente de Google Sheets inicializado\n")
    except Exception as e:
        print(f"❌ Error inicializando cliente: {e}")
        return
    
    # Fechas de prueba (formato YYYY-MM-DD)
    fechas_prueba = [
        ("2026-03-10", "Lunes"),
        ("2026-03-11", "Martes"),
        ("2026-03-12", "Miércoles"),
        ("2026-03-13", "Jueves"),
        ("2026-03-14", "Viernes"),
        ("2026-03-15", "Sábado"),
    ]
    
    doctoras = ["Sandra", "Zaida"]
    
    for doctora in doctoras:
        print(f"\n{'='*80}")
        print(f"DOCTORA: {doctora.upper()}")
        print(f"{'='*80}\n")
        
        for fecha_str, dia_nombre in fechas_prueba:
            print(f"📅 {dia_nombre} {fecha_str}")
            print("-" * 40)
            
            try:
                horas = sheets_client.get_available_hours_for_date(fecha_str, doctora)
                
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
                fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
                dia_numero = fecha_obj.weekday()
                
                if dia_numero == 5:  # Sábado
                    if not tarde:
                        print("   ✅ Correcto: Sábado sin horarios de tarde")
                    else:
                        print("   ❌ Error: Sábado no debería tener horarios de tarde")
                else:
                    if doctora.lower() == "sandra":
                        if dia_numero in [0, 1, 2]:  # Lunes-Miércoles
                            if tarde and tarde[-1] == "16:30":
                                print(f"   ✅ Correcto: Sandra {dia_nombre} última hora 16:30")
                            else:
                                print(f"   ❌ Error: Sandra {dia_nombre} debería terminar a las 16:30")
                        else:  # Jueves-Viernes
                            if tarde and tarde[-1] == "17:00":
                                print(f"   ✅ Correcto: Sandra {dia_nombre} última hora 17:00")
                            else:
                                print(f"   ❌ Error: Sandra {dia_nombre} debería terminar a las 17:00")
                    
                    elif doctora.lower() == "zaida":
                        if tarde and tarde[-1] == "17:00":
                            print(f"   ✅ Correcto: Zaida última hora 17:00")
                        else:
                            print(f"   ❌ Error: Zaida debería terminar a las 17:00")
                
                # Verificar que no haya 12:00
                if "12:00" in horas:
                    print("   ❌ Error: No debería haber horario a las 12:00 (hora de almuerzo)")
                else:
                    print("   ✅ Correcto: No hay horario a las 12:00")
                
                # Verificar que la última de la mañana sea 11:30
                if manana and manana[-1] == "11:30":
                    print("   ✅ Correcto: Última hora de mañana es 11:30")
                else:
                    print("   ❌ Error: Última hora de mañana debería ser 11:30")
                
            except Exception as e:
                print(f"   ❌ Error obteniendo horarios: {e}")
            
            print()
    
    print("\n" + "="*80)
    print("✅ PRUEBA COMPLETADA")
    print("="*80)

def test_citas_existentes():
    """Muestra las citas existentes en el sistema"""
    
    print("\n\n🔍 CITAS EXISTENTES EN EL SISTEMA")
    print("="*80)
    
    try:
        sheets_client = get_sheets_client()
        citas = sheets_client.get_all_appointments()
        
        if not citas:
            print("❌ No hay citas en el sistema")
            return
        
        print(f"\nTotal de citas: {len(citas)}\n")
        
        # Agrupar por doctora
        por_doctora = {}
        for cita in citas:
            doctora = cita.get('doctora', 'Sin asignar')
            if doctora not in por_doctora:
                por_doctora[doctora] = []
            por_doctora[doctora].append(cita)
        
        for doctora, citas_doctora in por_doctora.items():
            print(f"\n👩‍⚕️ DOCTORA {doctora.upper()}: {len(citas_doctora)} citas")
            print("-" * 40)
            
            for i, cita in enumerate(citas_doctora[:5], 1):  # Mostrar solo las primeras 5
                print(f"{i}. Cédula: {cita['id']}")
                print(f"   Nombre: {cita['nombre']}")
                print(f"   Servicio: {cita['servicio']}")
                print(f"   Fecha: {cita['fecha']} - Hora: {cita['hora']}")
                print(f"   Estado: {cita['estado']}")
                print()
            
            if len(citas_doctora) > 5:
                print(f"   ... y {len(citas_doctora) - 5} citas más\n")
        
        print("\n💡 Usa una de estas cédulas para probar el flujo de reagendar")
        
    except Exception as e:
        print(f"❌ Error obteniendo citas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("PRUEBAS DEL SISTEMA DE HORARIOS POR DOCTORA")
    print("="*80 + "\n")
    
    # Prueba 1: Horarios por doctora
    test_horarios_por_doctora()
    
    # Prueba 2: Citas existentes
    test_citas_existentes()
    
    print("\n\n✅ Todas las pruebas completadas")
    print("\nPara probar el flujo completo de reagendar, ejecuta:")
    print("  python test_reagendar_flow.py")
