cat > README.md <<'EOF'
# Evaluacion2

## Descripcion del proyecto

Esta aplicacion esta desarrollada en Python y utiliza la API de
GraphHopper para calcular rutas entre un punto de origen y un destino.

El programa permite seleccionar un medio de transporte, consultar
la distancia y el tiempo estimado, e imprimir las instrucciones
paso a paso del viaje.

## Requisitos

- Python 3
- Libreria requests
- Conexion a Internet
- Una clave API valida de GraphHopper

## Instalacion

Para instalar la libreria requests, ejecuta:

```bash
python3 -m pip install requests