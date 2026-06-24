"""
Actualizador de resultados del Mundial FIFA 2026
==================================================
Este script se conecta a la API de football-data.org, jala los partidos
del Mundial 2026 (fixtures + resultados) y guarda todo en resultados.json.

Se ejecuta automáticamente vía GitHub Actions (ver .github/workflows/actualizar.yml)
No necesitas correrlo a mano, pero también puedes hacerlo localmente si quieres probar:

    pip install requests
    export FOOTBALL_DATA_API_KEY="tu_api_key_aqui"
    python actualizar_resultados.py
"""

import json
import os
import sys
import time
from datetime import datetime, timezone

import requests

API_KEY = os.environ.get("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4"
COMPETITION_CODE = "WC"  # Código de competencia del Mundial en football-data.org
OUTPUT_FILE = "resultados.json"

# Traducción de estados de partido (la API los regresa en inglés)
ESTADO_TRADUCIDO = {
    "SCHEDULED": "Programado",
    "TIMED": "Programado",
    "IN_PLAY": "En vivo",
    "PAUSED": "Medio tiempo",
    "FINISHED": "Finalizado",
    "POSTPONED": "Postergado",
    "SUSPENDED": "Suspendido",
    "CANCELLED": "Cancelado",
}


def obtener_partidos():
    """Llama a la API y regresa la lista cruda de partidos del Mundial 2026."""
    if not API_KEY:
        print("ERROR: no encontré la variable de entorno FOOTBALL_DATA_API_KEY.")
        print("Si corres esto localmente: export FOOTBALL_DATA_API_KEY='tu_key'")
        sys.exit(1)

    url = f"{BASE_URL}/competitions/{COMPETITION_CODE}/matches"
    headers = {"X-Auth-Token": API_KEY}

    intentos = 0
    while intentos < 3:
        resp = requests.get(url, headers=headers, timeout=30)

        if resp.status_code == 200:
            return resp.json().get("matches", [])

        if resp.status_code == 429:
            # Nos pasamos del límite de 10/min -> esperamos 65s y reintentamos.
            print("Límite de la API alcanzado (429). Esperando 65 segundos...")
            time.sleep(65)
            intentos += 1
            continue

        # Cualquier otro error: lo mostramos y nos detenemos.
        print(f"ERROR {resp.status_code} al llamar a la API: {resp.text[:300]}")
        sys.exit(1)

    print("ERROR: se agotaron los reintentos por límite de la API.")
    sys.exit(1)


def transformar_partido(p):
    """Convierte el formato de football-data.org a algo simple para el HTML."""
    estado_raw = p.get("status", "SCHEDULED")
    marcador = p.get("score", {}).get("fullTime", {}) or {}

    return {
        "id": p.get("id"),
        "fecha_utc": p.get("utcDate"),
        "fase": p.get("stage"),
        "grupo": p.get("group"),
        "jornada": p.get("matchday"),
        "estado": ESTADO_TRADUCIDO.get(estado_raw, estado_raw),
        "estado_raw": estado_raw,
        "equipo_local": p.get("homeTeam", {}).get("name"),
        "equipo_local_bandera": p.get("homeTeam", {}).get("crest"),
        "equipo_visitante": p.get("awayTeam", {}).get("name"),
        "equipo_visitante_bandera": p.get("awayTeam", {}).get("crest"),
        "goles_local": marcador.get("home"),
        "goles_visitante": marcador.get("away"),
        "ganador": p.get("score", {}).get("winner"),
        "sede": p.get("venue"),
    }


def main():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Consultando football-data.org...")
    partidos_raw = obtener_partidos()
    print(f"Recibidos {len(partidos_raw)} partidos.")

    partidos = [transformar_partido(p) for p in partidos_raw]
    # Orden cronológico, lo más natural para mostrar en la página.
    partidos.sort(key=lambda x: x["fecha_utc"] or "")

    salida = {
        "actualizado_utc": datetime.now(timezone.utc).isoformat(),
        "torneo": "FIFA World Cup 2026",
        "fuente": "football-data.org",
        "total_partidos": len(partidos),
        "partidos": partidos,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)

    print(f"Listo. Guardado en {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
