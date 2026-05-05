import os
import sys
from pathlib import Path

try:
    import requests
except Exception as exc:
    raise SystemExit(f"requests no está disponible: {exc}")


BASE_URL = os.environ.get("SMOKE_BASE_URL", "http://127.0.0.1:5000")
TIMEOUT = 10


def check(name: str, condition: bool, detail: str = "") -> None:
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {name} {detail}".strip())
    if not condition:
        raise SystemExit(1)


def main() -> None:
    print(f"Running smoke tests against {BASE_URL}")

    health = requests.get(f"{BASE_URL}/healthz", timeout=TIMEOUT)
    check("healthz", health.status_code == 200, f"status={health.status_code}")

    code = "smoke_user"
    requests.post(f"{BASE_URL}/register", json={"code": code}, timeout=TIMEOUT)
    login = requests.post(f"{BASE_URL}/login", json={"code": code}, timeout=TIMEOUT)
    check("login", login.status_code == 200, f"status={login.status_code}")
    token = login.json().get("token")
    check("token", bool(token))

    headers = {"Authorization": f"Bearer {token}"}

    resumen = requests.get(f"{BASE_URL}/resumen", headers=headers, timeout=TIMEOUT)
    check("resumen", resumen.status_code in (200, 404), f"status={resumen.status_code}")

    chat = requests.post(
        f"{BASE_URL}/chat",
        headers=headers,
        json={"pregunta": "¿Hay datos cargados?"},
        timeout=TIMEOUT,
    )
    check("chat", chat.status_code in (200, 503), f"status={chat.status_code}")

    excel_path = Path(__file__).resolve().parents[1] / "uploads" / "datos_enerwire.xlsx"
    if excel_path.exists():
        with open(excel_path, "rb") as file_obj:
            upload = requests.post(
                f"{BASE_URL}/upload",
                headers=headers,
                files={"file": (excel_path.name, file_obj, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
                timeout=TIMEOUT,
            )
        check("upload", upload.status_code == 200, f"status={upload.status_code}")
    else:
        print(f"[SKIP] upload archivo no encontrado en {excel_path}")

    print("Smoke tests completados.")


if __name__ == "__main__":
    main()
