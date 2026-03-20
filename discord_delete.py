import requests
import time
import sys

BASE_URL = "https://discord.com/api/v10"

def get_headers(token):
    return {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

def get_current_user(token):
    """Obtiene el ID del usuario autenticado."""
    r = requests.get(f"{BASE_URL}/users/@me", headers=get_headers(token))
    if r.status_code == 200:
        return r.json()
    print(f"[ERROR] Token inválido o sin conexión. Código: {r.status_code}")
    sys.exit(1)

def fetch_messages(token, channel_id, limit=100, before=None):
    """Obtiene mensajes de un canal."""
    params = {"limit": limit}
    if before:
        params["before"] = before
    r = requests.get(
        f"{BASE_URL}/channels/{channel_id}/messages",
        headers=get_headers(token),
        params=params
    )
    if r.status_code == 200:
        return r.json()
    elif r.status_code == 403:
        print("[ERROR] No tienes acceso a este canal.")
        return []
    elif r.status_code == 404:
        print("[ERROR] Canal no encontrado. Verifica el ID.")
        return []
    else:
        print(f"[ERROR] Código {r.status_code}: {r.text}")
        return []

def get_my_messages(token, channel_id, user_id):
    """Obtiene TODOS los mensajes propios en un canal."""
    all_msgs = []
    before = None
    print("  Buscando mensajes", end="", flush=True)
    while True:
        msgs = fetch_messages(token, channel_id, before=before)
        if not msgs:
            break
        my_msgs = [m for m in msgs if m["author"]["id"] == user_id]
        all_msgs.extend(my_msgs)
        print(".", end="", flush=True)
        before = msgs[-1]["id"]
        time.sleep(0.5)
        if len(msgs) < 100:
            break
    print()
    return all_msgs

def delete_message(token, channel_id, message_id):
    """Borra un mensaje por su ID."""
    r = requests.delete(
        f"{BASE_URL}/channels/{channel_id}/messages/{message_id}",
        headers=get_headers(token)
    )
    return r.status_code

def open_dm(token, user_id):
    """Abre o recupera un canal DM con un usuario."""
    r = requests.post(
        f"{BASE_URL}/users/@me/channels",
        headers=get_headers(token),
        json={"recipient_id": user_id}
    )
    if r.status_code == 200:
        return r.json()["id"]
    print(f"[ERROR] No se pudo abrir el DM. Código: {r.status_code}")
    sys.exit(1)

def separador():
    print("─" * 55)

# ─────────────────────────────────────────────
#  MENÚ PRINCIPAL
# ─────────────────────────────────────────────
def main():
    print("=" * 55)
    print("   Discord Message Deleter — Solo mensajes propios")
    print("=" * 55)
    print()
    print("[AVISO] Este script solo puede borrar TUS mensajes.")
    print("        Usar tokens ajenos viola los TdS de Discord.")
    print()

    token = input("🔑 Ingresa tu token de Discord: ").strip()
    if not token:
        print("[ERROR] Token vacío.")
        sys.exit(1)

    # Verificar identidad
    user = get_current_user(token)
    user_id = user["id"]
    username = f"{user['username']}#{user.get('discriminator','0')}"
    print(f"\n✅ Autenticado como: {username} (ID: {user_id})")
    separador()

    # Elegir modo
    print("\n¿Dónde deseas borrar mensajes?")
    print("  [1] Canal de un servidor")
    print("  [2] DM (mensaje directo) con un usuario")
    modo = input("\nElige opción (1 o 2): ").strip()

    if modo == "1":
        # ── MODO SERVIDOR ──
        separador()
        print("\n📡 MODO: Canal de servidor")
        server_id = input("ID del servidor: ").strip()
        channel_id = input("ID del canal  : ").strip()

        print(f"\n🔍 Buscando tus mensajes en el canal {channel_id}...")
        msgs = get_my_messages(token, channel_id, user_id)

        separador()
        print(f"\n📊 Encontré {len(msgs)} mensaje(s) tuyo(s) en ese canal.")

        if not msgs:
            print("Nada que borrar. ¡Adiós!")
            sys.exit(0)

        print("\n¿Deseas ver los mensajes antes de borrar? (s/n): ", end="")
        ver = input().strip().lower()
        if ver == "s":
            separador()
            print(f"{'#':<4} {'ID':<20} {'Contenido'}")
            separador()
            for i, m in enumerate(msgs[:50], 1):
                contenido = m.get("content", "[sin texto / adjunto]")
                contenido = (contenido[:60] + "...") if len(contenido) > 60 else contenido
                print(f"{i:<4} {m['id']:<20} {contenido}")
            if len(msgs) > 50:
                print(f"  ... y {len(msgs) - 50} más.")
            separador()

        print(f"\n⚠️  ¿Confirmas borrar los {len(msgs)} mensajes? Esto NO se puede deshacer.")
        confirm = input("Escribe 'BORRAR' para confirmar: ").strip()
        if confirm != "BORRAR":
            print("Operación cancelada.")
            sys.exit(0)

        separador()
        print("\n🗑️  Borrando mensajes...\n")
        borrados = 0
        errores = 0
        for m in msgs:
            contenido = m.get("content", "[sin texto / adjunto]")
            contenido = (contenido[:70] + "...") if len(contenido) > 70 else contenido
            status = delete_message(token, channel_id, m["id"])
            if status in (200, 204):
                print(f"  ✅  | Borrado [{m['id']}]: {contenido}")
                borrados += 1
            elif status == 429:
                print(f"  ⏳  | Rate limit. Esperando 2s...")
                time.sleep(2)
                # Reintentar
                status2 = delete_message(token, channel_id, m["id"])
                if status2 in (200, 204):
                    print(f"  ✅  | Borrado (reintento) [{m['id']}]: {contenido}")
                    borrados += 1
                else:
                    print(f"  ❌  | Error al reintentar [{m['id']}]")
                    errores += 1
            else:
                print(f"  ❌ Error {status} [{m['id']}]: {contenido}")
                errores += 1
            time.sleep(0.8)  # Respetar rate limits

    elif modo == "2":
        # ── MODO DM ──
        separador()
        print("\n💬 MODO: Mensaje directo (DM)")
        dm_user_id = input("ID del usuario con quien tienes el DM: ").strip()

        print(f"\n🔗 Abriendo canal DM con usuario {dm_user_id}...")
        channel_id = open_dm(token, dm_user_id)
        print(f"   Canal DM ID: {channel_id}")

        print(f"\n🔍 Buscando tus mensajes en el DM...")
        msgs = get_my_messages(token, channel_id, user_id)

        separador()
        print(f"\n📊 Encontré {len(msgs)} mensaje(s) tuyo(s) en ese DM.")

        if not msgs:
            print("Nada que borrar. ¡Adiós!")
            sys.exit(0)

        print(f"\n⚠️  ¿Confirmas borrar los {len(msgs)} mensajes del DM? Esto NO se puede deshacer.")
        confirm = input("Escribe 'BORRAR' para confirmar: ").strip()
        if confirm != "BORRAR":
            print("Operación cancelada.")
            sys.exit(0)

        separador()
        print("\n🗑️  Borrando mensajes...\n")
        borrados = 0
        errores = 0
        for m in msgs:
            contenido = m.get("content", "[sin texto / adjunto]")
            contenido = (contenido[:70] + "...") if len(contenido) > 70 else contenido
            status = delete_message(token, channel_id, m["id"])
            if status in (200, 204):
                print(f"  ✅ Borrado [{m['id']}]: {contenido}")
                borrados += 1
            elif status == 429:
                print(f"  ⏳ Rate limit. Esperando 2s...")
                time.sleep(2)
                status2 = delete_message(token, channel_id, m["id"])
                if status2 in (200, 204):
                    print(f"  ✅ | Borrado (reintento) [{m['id']}]: {contenido}")
                    borrados += 1
                else:
                    print(f"  ❌ |  Error al reintentar [{m['id']}]")
                    errores += 1
            else:
                print(f"  ❌ Error {status} [{m['id']}]: {contenido}")
                errores += 1
            time.sleep(0.8)

    else:
        print("[ERROR] Opción inválida.")
        sys.exit(1)

    # ── RESUMEN ──
    separador()
    print(f"\n📋 RESUMEN")
    print(f"   ✅ Mensajes borrados : {borrados}")
    print(f"   ❌ Errores           : {errores}")
    separador()

if __name__ == "__main__":
    main()
