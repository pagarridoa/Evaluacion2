
import getpass
import requests

# Direcciones oficiales de GraphHopper
BASE_URL = "https://graphhopper.com/api/1"
GEOCODE_URL = BASE_URL + "/geocode"
ROUTE_URL = BASE_URL + "/route"

sesion = requests.Session()


def pedir_dato(mensaje):
    """Solicita un dato y permite salir con s o salir."""
    dato = input(mensaje).strip()

    if dato.lower() in ("s", "salir"):
        return None

    return dato


def consultar_api(url, parametros):
    """Consulta la API y controla los errores HTTP."""
    respuesta = sesion.get(
        url,
        params=parametros,
        timeout=30
    )

    try:
        datos = respuesta.json()
    except ValueError:
        datos = {}

    if not respuesta.ok:
        mensaje = datos.get(
            "message",
            "No se pudo completar la solicitud."
        ) if isinstance(datos, dict) else "Respuesta no valida."

        raise RuntimeError(
            f"Error HTTP {respuesta.status_code}: {mensaje}"
        )

    if not isinstance(datos, dict):
        raise RuntimeError(
            "La API devolvio una respuesta inesperada."
        )

    return datos


def geocodificar(lugar, api_key):
    """Convierte una direccion en coordenadas geograficas."""
    parametros = {
        "q": lugar,
        "limit": 1,
        "locale": "es",
        "key": api_key
    }

    datos = consultar_api(GEOCODE_URL, parametros)
    resultados = datos.get("hits", [])

    if not resultados:
        raise RuntimeError(
            f"No se encontro la ubicacion: {lugar}"
        )

    resultado = resultados[0]
    punto = resultado.get("point", {})

    if "lat" not in punto or "lng" not in punto:
        raise RuntimeError(
            f"No se encontraron coordenadas para: {lugar}"
        )

    return {
        "nombre": resultado.get("name", lugar),
        "lat": punto["lat"],
        "lng": punto["lng"]
    }


def calcular_ruta(origen, destino, transporte, api_key):
    """Calcula una ruta e imprime sus instrucciones en español."""

    punto_origen = geocodificar(origen, api_key)
    punto_destino = geocodificar(destino, api_key)

    # Se incluyen dos parametros point: origen y destino.
    parametros = [
        ("key", api_key),
        ("profile", transporte),
        ("locale", "es"),
        ("instructions", "true"),
        (
            "point",
            f"{punto_origen['lat']},{punto_origen['lng']}"
        ),
        (
            "point",
            f"{punto_destino['lat']},{punto_destino['lng']}"
        )
    ]

    datos = consultar_api(ROUTE_URL, parametros)
    rutas = datos.get("paths", [])

    if not rutas:
        raise RuntimeError(
            "La API no encontro una ruta entre esos lugares."
        )

    ruta = rutas[0]

    # GraphHopper entrega distancia en metros y tiempo en ms.
    distancia_km = ruta["distance"] / 1000
    tiempo_horas = ruta["time"] / 3600000

    print("\n==========================================")
    print("           RESULTADO DEL VIAJE")
    print("==========================================")
    print(f"Origen: {punto_origen['nombre']}")
    print(f"Destino: {punto_destino['nombre']}")
    print(f"Transporte: {transporte}")
    print(f"Distancia total: {distancia_km:.2f} km")
    print(f"Tiempo estimado: {tiempo_horas:.2f} horas")

    print("\nINSTRUCCIONES PASO A PASO")
    print("------------------------------------------")

    instrucciones = ruta.get("instructions", [])

    if not instrucciones:
        print("La API no devolvio instrucciones para el viaje.")
    else:
        for numero, instruccion in enumerate(instrucciones, start=1):
            texto = instruccion.get(
                "text",
                "Continuar por la ruta indicada"
            )

            distancia_instruccion = (
                instruccion.get("distance", 0) / 1000
            )

            print(
                f"{numero}. {texto} "
                f"({distancia_instruccion:.2f} km)"
            )

    print("==========================================\n")


def main():
    print("SISTEMA DE RUTAS - BIBLIOTECA NACIONAL")
    print("------------------------------------------")

    # Solicitar la clave sin mostrarla en pantalla.
    api_key = getpass.getpass(
        "Introduce tu clave API de GraphHopper: "
    ).strip()

    if api_key.lower() in ("s", "salir"):
        print("Programa finalizado.")
        return

    if not api_key:
        print("Error: debes introducir una clave API.")
        return

    while True:
        origen = pedir_dato(
            "\nIngrese el punto de partida "
            "(escriba s o salir para terminar): "
        )

        if origen is None:
            print("Programa finalizado. Hasta luego.")
            break

        if not origen:
            print("Debe ingresar un punto de partida.")
            continue

        destino = pedir_dato(
            "Ingrese el destino "
            "(escriba s o salir para terminar): "
        )

        if destino is None:
            print("Programa finalizado. Hasta luego.")
            break

        if not destino:
            print("Debe ingresar un destino.")
            continue

        print("\nSeleccione el medio de transporte:")
        print("1. Automovil")
        print("2. Bicicleta")
        print("3. A pie")

        opcion = pedir_dato(
            "Ingrese 1, 2 o 3 "
            "(escriba s o salir para terminar): "
        )

        if opcion is None:
            print("Programa finalizado. Hasta luego.")
            break

        transportes = {
            "1": "car",
            "2": "bike",
            "3": "foot"
        }

        if opcion not in transportes:
            print("Opcion no valida. Intente nuevamente.")
            continue

        transporte = transportes[opcion]

        try:
            calcular_ruta(
                origen,
                destino,
                transporte,
                api_key
            )

        except RuntimeError as error:
            print(f"\nNo se pudo calcular el viaje: {error}")

        except requests.RequestException:
            print(
                "\nError de conexion con GraphHopper. "
                "Revise su Internet e intentelo nuevamente."
            )


if __name__ == "__main__":
    main()
