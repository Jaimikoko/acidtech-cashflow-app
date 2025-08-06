#!/usr/bin/env python3
"""
Script para cargar los datos de Revenue 4717 desde el archivo CSV
Ejecuta la función upload_and_replace_transactions
"""

import sys
import os
from datetime import datetime

# Añadir directorio actual al path para imports
sys.path.append('.')

from app.routes.data_import.routes import upload_and_replace_transactions
from database import db
from app import create_app

def main():
    """Cargar datos del archivo Revenue 4717"""
    
    # Crear contexto de aplicación
    app = create_app()
    
    with app.app_context():
        print("INICIANDO CARGA DE DATOS REVENUE 4717")
        print("=" * 50)
        
        # Archivo a cargar
        csv_file_path = "Acid Tech Revenue-4717-Carga1.csv"
        
        # Verificar que existe el archivo
        if not os.path.exists(csv_file_path):
            print(f"ERROR: No se encuentra el archivo {csv_file_path}")
            return
            
        print(f"Archivo encontrado: {csv_file_path}")
        
        # Ejecutar carga
        result = upload_and_replace_transactions(
            file_path=csv_file_path,
            year=2025,
            account_name="Revenue 4717"
        )
        
        # Mostrar resultados
        print("\n" + "=" * 50)
        print("RESULTADOS DE LA CARGA:")
        print("=" * 50)
        
        if result['success']:
            print(f"EXITO - Datos cargados correctamente")
            print(f"Registros eliminados: {result['records_deleted']}")
            print(f"Registros insertados: {result['records_inserted']}")
            print(f"Errores encontrados: {len(result['errors'])}")
            print(f"Fecha/hora: {result['timestamp']}")
            
            if result['errors']:
                print("\nERRORES DETECTADOS:")
                for error in result['errors']:
                    print(f"   - {error}")
        else:
            print(f"ERROR EN CARGA: {result['error']}")
        
        print("\nLa carga ha finalizado. Revisa el dashboard de Cash Flow.")

if __name__ == "__main__":
    main()