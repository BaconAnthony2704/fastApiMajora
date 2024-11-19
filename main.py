import os
from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel
import pyodbc


SECRET_KEY = "JZ5tD05N0GIg693cKBL7nS5C3pZqYmm3"
API_KEY = "77E99C27CE7C7CA4"
# Configuración de conexión a SQL Server

DB_CONFIG = {
    "driver": "{ODBC Driver 17 for SQL Server}",
    "server": "DB_CSFR.mssql.somee.com",
    "database": "DB_CSFR",
    "username": "Gpo06UES_SQLLogin_1",
    "password": "UESSuperate2023#",
}

app = FastAPI()
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid API Key")
    return api_key  # No es necesario usarla explícitamente

# Función para conectar a la base de datos
def get_db_connection():
    return pyodbc.connect(
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']}"
    )


def get_db_connection():
    try:
        connection = pyodbc.connect(
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['username']};"
            f"PWD={DB_CONFIG['password']}"
        )
        return connection
    except pyodbc.Error as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión: {e}")
    
# Modelo para la solicitud POST de búsqueda por DUI
class DUIRequest(BaseModel):
    dui: str

class NombreRequest(BaseModel):
    nombre: str

@app.post("/buscar-por-dui")
async def buscar_por_dui(request: DUIRequest, api_key: str = Depends(verify_api_key)):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Llama al procedimiento almacenado
        cursor.execute("EXEC sp_get_padron_by_dui @DUI = ?", request.dui)
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="DUI no encontrado")

        columns = [column[0] for column in cursor.description]
        result = dict(zip(columns, row))
        return {"data": result}
    except pyodbc.Error as e:
        raise HTTPException(status_code=400, detail=f"Error al ejecutar el procedimiento almacenado: {e}")
    finally:
        connection.close()

@app.get("/padron")
async def get_all_padron():
    """
    Endpoint para obtener todo el listado usando un procedimiento almacenado.
    """
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        # Llamar al procedimiento almacenado
        cursor.execute("EXEC sp_get_all_padron")
        rows = cursor.fetchall()

        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        return {"data": results}
    except pyodbc.Error as e:
        raise HTTPException(status_code=400, detail=f"Error al ejecutar el procedimiento almacenado: {e}")
    finally:
        connection.close()

@app.post("/buscar-por-nombre")
async def buscar_por_nombre(request: NombreRequest, api_key: str = Depends(verify_api_key)):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Llama al procedimiento almacenado
        cursor.execute("EXEC SP_GetUbicacionPorNombre @nombre = ?", request.nombre)
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="DUI no encontrado")

        columns = [column[0] for column in cursor.description]
        result = dict(zip(columns, row))
        return {"data": result}
    except pyodbc.Error as e:
        raise HTTPException(status_code=400, detail=f"Error al ejecutar el procedimiento almacenado: {e}")
    finally:
        connection.close()
