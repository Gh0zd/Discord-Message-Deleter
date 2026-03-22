import requests
import time
import sys
import curses
import curses.textpad
import threading
import random

BASE_URL = "https://discord.com/api/v10"

# ─── PARES DE COLOR ────────────────────────────────────────────────────────

def init_colors():
    curses.start_color()
    curses.use_default_colors()
    AZUL    = curses.COLOR_CYAN
    AMBAR   = curses.COLOR_YELLOW
    ROJO    = curses.COLOR_RED
    MENTA   = curses.COLOR_GREEN
    BLANCO  = curses.COLOR_WHITE
    NEGRO   = curses.COLOR_BLACK
    MAGENTA = curses.COLOR_MAGENTA

    curses.init_pair(1, AZUL,    NEGRO)
    curses.init_pair(2, AMBAR,   NEGRO)
    curses.init_pair(3, ROJO,    NEGRO)
    curses.init_pair(4, MENTA,   NEGRO)
    curses.init_pair(5, BLANCO,  NEGRO)
    curses.init_pair(6, NEGRO,   AZUL)
    curses.init_pair(7, BLANCO,  NEGRO)
    curses.init_pair(8, AMBAR,   NEGRO)
    curses.init_pair(9, MAGENTA, NEGRO)
    curses.init_pair(10, NEGRO,  ROJO)

C_AZUL    = lambda: curses.color_pair(1) | curses.A_BOLD
C_AMBAR   = lambda: curses.color_pair(2) | curses.A_BOLD
C_ROJO    = lambda: curses.color_pair(3) | curses.A_BOLD
C_MENTA   = lambda: curses.color_pair(4)
C_BLANCO  = lambda: curses.color_pair(5)
C_SEL     = lambda: curses.color_pair(6) | curses.A_BOLD
C_TENUE   = lambda: curses.color_pair(7) | curses.A_DIM
C_AVISO   = lambda: curses.color_pair(8)
C_MARCA   = lambda: curses.color_pair(9) | curses.A_BOLD
C_PELIGRO = lambda: curses.color_pair(10) | curses.A_BOLD

# ─── UTILIDADES ────────────────────────────────────────────────────────────

def safe_addstr(win, y, x, text, attr=0):
    h, w = win.getmaxyx()
    if y < 0 or y >= h or x >= w:
        return
    available = w - x
    if available <= 0:
        return
    if y == h - 1:
        available = min(available, w - x - 1)
    if available <= 0:
        return
    try:
        win.addstr(y, x, text[:available], attr)
    except curses.error:
        pass

def hline(win, y, char="─", attr=0):
    h, w = win.getmaxyx()
    if 0 <= y < h:
        safe_addstr(win, y, 0, char * w, attr)

def center_text(win, y, text, attr=0):
    h, w = win.getmaxyx()
    x = max(0, (w - len(text)) // 2)
    safe_addstr(win, y, x, text[:w], attr)

def draw_box(win, y, x, height, width, attr=0, title=""):
    h, w = win.getmaxyx()
    if y >= h or x >= w:
        return
    by = min(y + height - 1, h - 1)
    bx = min(x + width - 1, w - 1)

    safe_addstr(win, y,  x,  "╔", attr)
    safe_addstr(win, y,  bx, "╗", attr)
    safe_addstr(win, by, x,  "╚", attr)
    safe_addstr(win, by, bx, "╝", attr)

    inner_w = bx - x - 1
    if inner_w > 0:
        safe_addstr(win, y,  x + 1, "═" * inner_w, attr)
        safe_addstr(win, by, x + 1, "═" * inner_w, attr)

    for row in range(y + 1, by):
        safe_addstr(win, row, x,  "║", attr)
        safe_addstr(win, row, bx, "║", attr)

    if title and inner_w > 4:
        t = f" {title} "[:inner_w - 2]
        safe_addstr(win, y, x + 2, t, attr | curses.A_BOLD)

def clamp(val, lo, hi):
    return max(lo, min(hi, val))

# ─── LOGO ──────────────────────────────────────────────────────────────────

LOGO_LINES = [
    "██████╗ ███████╗██╗     ███████╗████████╗███████╗██████╗",
    "██╔══██╗██╔════╝██║     ██╔════╝╚══██╔══╝██╔════╝██╔══██╗",
    "██║  ██║█████╗  ██║     █████╗     ██║   █████╗  ██████╔╝",
    "██║  ██║██╔══╝  ██║     ██╔══╝     ██║   ██╔══╝  ██╔══██╗",
    "██████╔╝███████╗███████╗███████╗   ██║   ███████╗██║  ██║",
    "╚═════╝ ╚══════╝╚══════╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝",
]

LOGO_SMALL = [
    "▓█▓ DRSCOR ▓█▓",
    "ELIMINADOR//MENSAJES",
]

TAGLINE = "[v2.1 | BORRAR MIS MENSAJES ]"

# ─── CAPA API ──────────────────────────────────────────────────────────────

def get_headers(token):
    return {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

def human_delay(base=0.8, jitter=0.4):
    """Espera con variación aleatoria para evitar patrones fijos."""
    delay = base + random.uniform(-jitter, jitter)
    time.sleep(max(0.3, delay))

def get_current_user(token):
    r = requests.get(f"{BASE_URL}/users/@me", headers=get_headers(token))
    if r.status_code == 200:
        return r.json()
    return None

def fetch_messages(token, channel_id, limit=100, before=None):
    params = {"limit": limit}
    if before:
        params["before"] = before

    while True:
        r = requests.get(
            f"{BASE_URL}/channels/{channel_id}/messages",
            headers=get_headers(token),
            params=params
        )
        if r.status_code == 429:
            retry_after = float(r.headers.get("Retry-After", r.json().get("retry_after", 1.0)))
            time.sleep(retry_after + 0.1)
            continue

        remaining  = int(r.headers.get("X-RateLimit-Remaining", 1))
        reset_after = float(r.headers.get("X-RateLimit-Reset-After", 0))
        if remaining == 0:
            time.sleep(reset_after + 0.05)

        if r.status_code == 200:
            return r.json(), None
        return [], r.status_code

def get_my_messages(token, channel_id, user_id, progress_cb=None):
    all_msgs = []
    before = None
    while True:
        msgs, err = fetch_messages(token, channel_id, before=before)
        if not msgs:
            break
        my_msgs = [m for m in msgs if m["author"]["id"] == user_id]
        all_msgs.extend(my_msgs)
        if progress_cb:
            progress_cb(len(all_msgs))
        before = msgs[-1]["id"]
        human_delay(base=0.5, jitter=0.2)
        if len(msgs) < 100:
            break
    return all_msgs

def delete_message(token, channel_id, message_id):
    while True:
        r = requests.delete(
            f"{BASE_URL}/channels/{channel_id}/messages/{message_id}",
            headers=get_headers(token)
        )
        if r.status_code == 429:
            try:
                retry_after = float(r.json().get("retry_after", 1.0))
            except Exception:
                retry_after = float(r.headers.get("Retry-After", 1.0))
            time.sleep(retry_after + 0.1)
            continue

        remaining   = int(r.headers.get("X-RateLimit-Remaining", 1))
        reset_after = float(r.headers.get("X-RateLimit-Reset-After", 0))
        if remaining == 0:
            time.sleep(reset_after + 0.05)

        return r.status_code

def open_dm(token, dm_user_id):
    r = requests.post(
        f"{BASE_URL}/users/@me/channels",
        headers=get_headers(token),
        json={"recipient_id": dm_user_id}
    )
    if r.status_code == 200:
        return r.json()["id"], None
    return None, r.status_code

# ─── PANTALLA DE AVISO ─────────────────────────────────────────────────────

def disclaimer_screen(stdscr):
    """
    Muestra el aviso legal y de uso responsable al iniciar.
    El usuario debe escribir ACEPTO para continuar.
    Devuelve True si acepta, False si sale.
    """
    curses.curs_set(1)
    buf = []

    aviso_lines = [
        "",
        "  Este script elimina mensajes de TU propia cuenta de Discord.",
        "  Usar tokens de usuario con scripts automatizados puede violar",
        "  los Terminos de Servicio de Discord. Usalo bajo tu propia",
        "  responsabilidad.",
        "",
        "  Reglas de uso:",
        "    * Solo borra mensajes de tu propia cuenta.",
        "    * No lo uses con cuentas de terceros.",
        "    * El autor no se responsabiliza del uso indebido.",
        "",
        "  Por que es lento:",
        "    * Discord impone limites de peticiones (rate limits).",
        "    * Se aplican esperas aleatorias entre borrados para evitar",
        "      que tu cuenta sea bloqueada o baneada temporalmente.",
        "    * Cuantos mas mensajes tengas, mas tardara. Es normal.",
        "",
    ]

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        box_h = len(aviso_lines) + 7
        box_w = clamp(72, 50, w - 4)
        box_y = max(0, (h - box_h) // 2)
        box_x = max(0, (w - box_w) // 2)

        draw_box(stdscr, box_y, box_x, box_h, box_w, C_AMBAR(), "⚠  AVISO DE USO Y ADVERTENCIA  ⚠")

        for i, line in enumerate(aviso_lines):
            safe_addstr(stdscr, box_y + 1 + i, box_x + 1, line[:box_w - 2], C_AVISO())

        confirm_y = box_y + 1 + len(aviso_lines)
        prompt = "  Escribe 'ACEPTO' para continuar  |  'q' para salir:"
        safe_addstr(stdscr, confirm_y, box_x + 1, prompt[:box_w - 2], C_BLANCO())

        typed = "".join(buf)
        field_w = box_w - 6
        # Color del campo: rojo si lo que escribes no coincide con el prefijo de ACEPTO
        if typed and not "ACEPTO".startswith(typed.upper()):
            field_color = C_ROJO()
        else:
            field_color = C_MENTA()

        safe_addstr(stdscr, confirm_y + 1, box_x + 3,
                    typed + " " * max(0, field_w - len(typed)),
                    field_color | curses.A_REVERSE)

        safe_addstr(stdscr, confirm_y + 2, box_x + 3,
                    "Escribe exactamente: ACEPTO"[:box_w - 6], C_TENUE())

        stdscr.refresh()
        key = stdscr.getch()

        if key in (ord('q'), ord('Q'), 27):
            curses.curs_set(0)
            return False
        elif key in (curses.KEY_ENTER, 10, 13):
            if typed.upper() == "ACEPTO":
                curses.curs_set(0)
                return True
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if buf:
                buf.pop()
        elif 32 <= key <= 126:
            if len(buf) < 6:  # ACEPTO tiene 6 letras
                buf.append(chr(key))

# ─── DIÁLOGO DE ENTRADA ────────────────────────────────────────────────────

def input_dialog(stdscr, title, prompt, secret=False):
    curses.curs_set(1)
    h, w = stdscr.getmaxyx()
    box_w = clamp(60, 30, w - 4)
    box_h = 5
    box_y = (h - box_h) // 2
    box_x = (w - box_w) // 2

    overlay = curses.newwin(box_h, box_w, box_y, box_x)
    overlay.bkgd(' ', curses.color_pair(5))
    buf = []

    while True:
        overlay.erase()
        draw_box(overlay, 0, 0, box_h, box_w, C_AZUL(), title)
        safe_addstr(overlay, 2, 2, prompt[:box_w - 4], C_MENTA())

        display = ("*" * len(buf)) if secret else "".join(buf)
        field_w = box_w - 4
        display_cut = display[-field_w:] if len(display) > field_w else display
        safe_addstr(overlay, 3, 2, display_cut + " " * (field_w - len(display_cut)), C_AZUL() | curses.A_REVERSE)
        overlay.refresh()

        key = stdscr.getch()
        if key == 27:
            curses.curs_set(0)
            return None
        elif key in (curses.KEY_ENTER, 10, 13):
            curses.curs_set(0)
            return "".join(buf)
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if buf:
                buf.pop()
        elif 32 <= key <= 126:
            buf.append(chr(key))

# ─── BANNER DE NOTIFICACIÓN ────────────────────────────────────────────────

def show_banner(stdscr, message, color_fn, duration=1.8):
    h, w = stdscr.getmaxyx()
    msg = f"  {message}  "
    x = max(0, (w - len(msg)) // 2)
    safe_addstr(stdscr, h - 2, x, msg[:w], color_fn())
    stdscr.refresh()
    time.sleep(duration)

# ─── DIÁLOGO DE CONFIRMACIÓN ───────────────────────────────────────────────

def confirm_dialog(stdscr, title, lines, confirm_word="BORRAR"):
    h, w = stdscr.getmaxyx()
    box_w = clamp(62, 40, w - 4)
    box_h = len(lines) + 6
    box_y = (h - box_h) // 2
    box_x = (w - box_w) // 2

    overlay = curses.newwin(box_h, box_w, box_y, box_x)
    overlay.bkgd(' ', curses.color_pair(5))
    buf = []
    curses.curs_set(1)

    while True:
        overlay.erase()
        draw_box(overlay, 0, 0, box_h, box_w, C_ROJO(), title)

        for i, line in enumerate(lines):
            safe_addstr(overlay, 2 + i, 2, line[:box_w - 4], C_AVISO())

        prompt = f"Escribe '{confirm_word}' para confirmar:"
        safe_addstr(overlay, 2 + len(lines) + 1, 2, prompt[:box_w - 4], C_BLANCO())

        field_w = box_w - 4
        typed = "".join(buf)
        color = C_ROJO() if typed and typed != confirm_word[:len(typed)] else C_MENTA()
        safe_addstr(overlay, 2 + len(lines) + 2, 2,
                    typed + " " * (field_w - len(typed)), color | curses.A_REVERSE)

        overlay.refresh()
        key = stdscr.getch()

        if key == 27:
            curses.curs_set(0)
            return False
        elif key in (curses.KEY_ENTER, 10, 13):
            curses.curs_set(0)
            return "".join(buf) == confirm_word
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if buf:
                buf.pop()
        elif 32 <= key <= 126:
            buf.append(chr(key))

# ─── LISTA DE MENSAJES CON SCROLL ──────────────────────────────────────────

def message_list_view(stdscr, msgs, channel_info=""):
    curses.curs_set(0)
    offset = 0
    sel    = 0

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        safe_addstr(stdscr, 0, 0, f"╔{'═' * (w - 2)}╗", C_AZUL())
        title_str = f"  MENSAJES ENCONTRADOS  //  {len(msgs)} en total  //  {channel_info}"
        safe_addstr(stdscr, 1, 1, title_str[:w - 2], C_MARCA())
        safe_addstr(stdscr, 2, 0, f"╠{'═' * (w - 2)}╣", C_AZUL())

        id_w   = 20
        cont_w = w - id_w - 6
        col_hdr = f"  {'#':<4}  {'ID MENSAJE':<{id_w}}  {'CONTENIDO':<{cont_w}}"
        safe_addstr(stdscr, 3, 0, col_hdr[:w], C_TENUE() | curses.A_UNDERLINE)

        list_start = 4
        list_end   = h - 4
        list_h     = max(1, list_end - list_start)

        sel = clamp(sel, 0, len(msgs) - 1)
        if sel < offset:
            offset = sel
        elif sel >= offset + list_h:
            offset = sel - list_h + 1

        for i in range(list_h):
            idx = i + offset
            if idx >= len(msgs):
                break
            m       = msgs[idx]
            content = m.get("content", "[adjunto/embed]").replace("\n", " ")
            row_str = f"  {idx+1:<4}  {m['id']:<{id_w}}  {content[:cont_w]}"
            attr = C_SEL() if idx == sel else (C_AZUL() if idx % 2 == 0 else C_MENTA())
            safe_addstr(stdscr, list_start + i, 0, row_str[:w], attr)

        safe_addstr(stdscr, h - 4, 0, f"╠{'═' * (w - 2)}╣", C_AZUL())
        nav = " ↑↓ NAVEGAR  │  ENTER CONFIRMAR BORRADO  │  q CANCELAR "
        safe_addstr(stdscr, h - 3, 1, nav[:w - 2], C_TENUE())

        if len(msgs) > list_h:
            bar_h = max(1, list_h * list_h // len(msgs))
            bar_y = list_start + offset * (list_h - bar_h) // max(1, len(msgs) - list_h)
            for row in range(list_start, list_end):
                ch = "█" if bar_y <= row < bar_y + bar_h else "░"
                safe_addstr(stdscr, row, w - 1, ch, C_TENUE())

        safe_addstr(stdscr, h - 2, 0, f"╚{'═' * (w - 2)}╝", C_AZUL())
        stdscr.refresh()
        key = stdscr.getch()

        if key in (ord('q'), ord('Q'), 27):
            return False
        elif key in (curses.KEY_ENTER, 10, 13):
            return True
        elif key in (curses.KEY_UP, ord('k')):
            sel = max(0, sel - 1)
        elif key in (curses.KEY_DOWN, ord('j')):
            sel = min(len(msgs) - 1, sel + 1)
        elif key == curses.KEY_PPAGE:
            sel = max(0, sel - list_h)
        elif key == curses.KEY_NPAGE:
            sel = min(len(msgs) - 1, sel + list_h)
        elif key == curses.KEY_HOME:
            sel = 0
        elif key == curses.KEY_END:
            sel = len(msgs) - 1

# ─── VISTA DE PROGRESO DE BORRADO ──────────────────────────────────────────

def delete_progress_view(stdscr, token, channel_id, msgs):
    curses.curs_set(0)
    total      = len(msgs)
    deleted    = 0
    errors     = 0
    log_lines  = []
    done_event = threading.Event()

    def do_delete():
        nonlocal deleted, errors
        for m in msgs:
            content = m.get("content", "[adjunto/embed]").replace("\n", " ")[:55]
            status  = delete_message(token, channel_id, m["id"])

            if status in (200, 204):
                deleted += 1
                log_lines.append((f" ✓  {m['id']}  {content}", C_MENTA))
            else:
                errors += 1
                log_lines.append((f" ✗  {m['id']}  HTTP {status}", C_ROJO))

            human_delay(base=0.8, jitter=0.3)

        done_event.set()

    thread = threading.Thread(target=do_delete, daemon=True)
    thread.start()

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        safe_addstr(stdscr, 0, 0, f"╔{'═' * (w - 2)}╗", C_AZUL())
        center_text(stdscr, 1, "// PURGA EN PROGRESO //", C_MARCA())
        safe_addstr(stdscr, 2, 0, f"╠{'═' * (w - 2)}╣", C_AZUL())

        done_count = deleted + errors
        pct    = done_count / total if total else 1
        bar_w  = w - 20
        filled = int(bar_w * pct)
        bar    = "█" * filled + "░" * (bar_w - filled)
        safe_addstr(stdscr, 4, 2, f"PROGRESO  [{bar}] {done_count}/{total}", C_AZUL())
        safe_addstr(stdscr, 6, 4, f"✓  BORRADOS : {deleted}", C_MENTA())
        safe_addstr(stdscr, 7, 4, f"✗  ERRORES  : {errors}", C_ROJO() if errors else C_TENUE())

        # ── Nota explicativa de velocidad ──────────────────────────────────
        nota_vel = "  ⏱  Proceso lento a proposito — esperas aleatorias evitan ban por rate-limit de Discord  "
        safe_addstr(stdscr, 9, 2, nota_vel[:w - 4], C_TENUE())
        # ──────────────────────────────────────────────────────────────────

        log_area_start = 11
        log_area_h     = h - log_area_start - 4
        safe_addstr(stdscr, log_area_start - 1, 0, f"╠{'═' * (w - 2)}╣", C_AZUL())
        safe_addstr(stdscr, log_area_start - 1, 2, " REGISTRO DE OPERACIONES ", C_TENUE())

        visible_logs = log_lines[-log_area_h:]
        for i, (txt, cfn) in enumerate(visible_logs):
            safe_addstr(stdscr, log_area_start + i, 1, txt[:w - 2], cfn())

        if done_event.is_set():
            safe_addstr(stdscr, h - 3, 0, f"╠{'═' * (w - 2)}╣", C_AZUL())
            center_text(stdscr, h - 2, "PURGA COMPLETADA — pulsa cualquier tecla", C_MARCA())

        safe_addstr(stdscr, h - 1, 0, f"╚{'═' * (w - 2)}╝", C_AZUL())
        stdscr.refresh()

        if done_event.is_set():
            stdscr.getch()
            break

        stdscr.nodelay(True)
        stdscr.getch()
        stdscr.nodelay(False)
        time.sleep(0.1)

    return deleted, errors

# ─── MENÚ PRINCIPAL ────────────────────────────────────────────────────────

def draw_main_menu(stdscr, selected, token_set, user_info):
    stdscr.erase()
    h, w = stdscr.getmaxyx()

    safe_addstr(stdscr, 0, 0, f"╔{'═' * (w - 2)}╗", C_AZUL())
    safe_addstr(stdscr, h - 1, 0, f"╚{'═' * (w - 2)}╝", C_AZUL())
    for row in range(1, h - 1):
        safe_addstr(stdscr, row, 0, "║", C_AZUL())
        safe_addstr(stdscr, row, w - 1, "║", C_AZUL())

    logo = LOGO_LINES if w >= 62 else LOGO_SMALL
    logo_start = 1
    for i, line in enumerate(logo):
        center_text(stdscr, logo_start + i, line, C_MARCA())

    after_logo = logo_start + len(logo)
    center_text(stdscr, after_logo + 1, TAGLINE, C_TENUE())

    sep_y = after_logo + 2
    safe_addstr(stdscr, sep_y, 1, "╠" + "═" * (w - 2) + "╣", C_AZUL())

    token_y = sep_y + 1
    if token_set and user_info:
        uname = f"{user_info['username']}#{user_info.get('discriminator', '0')}"
        uid   = user_info['id']
        safe_addstr(stdscr, token_y, 1,
                    f"  OPERADOR :: {uname}  │  UID :: {uid}"[:w - 2], C_MENTA())
    else:
        safe_addstr(stdscr, token_y, 1, "  SIN TOKEN — autentícate primero", C_ROJO())

    menu_items = [
        ("1", "ESTABLECER TOKEN",  "Autenticarse con tu token de Discord"),
        ("2", "CANAL DE SERVIDOR", "Borrar mensajes de un canal de servidor"),
        ("3", "MENSAJE DIRECTO",   "Borrar mensajes de una conversación DM"),
        ("Q", "SALIR",             "Cerrar el programa"),
    ]

    menu_start = token_y + 2
    safe_addstr(stdscr, menu_start - 1, 1, "╠" + "═" * (w - 2) + "╣", C_AZUL())

    for i, (key, label, desc) in enumerate(menu_items):
        y = menu_start + i * 2
        if y >= h - 2:
            break
        if i == selected:
            safe_addstr(stdscr, y, 2, f" ▶ [{key}] {label:<24} {desc}", C_SEL())
        else:
            safe_addstr(stdscr, y, 2, f"   [{key}] ", C_TENUE())
            safe_addstr(stdscr, y, 11, f"{label:<24}", C_BLANCO())
            safe_addstr(stdscr, y, 36, desc, C_TENUE())

    safe_addstr(stdscr, h - 2, 1,
                "  ↑↓ NAVEGAR  │  ENTER SELECCIONAR  │  q SALIR  "[:w - 2], C_TENUE())
    stdscr.refresh()

# ─── SUPERPOSICIÓN DE BÚSQUEDA ─────────────────────────────────────────────

def searching_overlay(stdscr, token, channel_id, user_id):
    found    = [0]
    msgs_box = [None]
    done     = [False]
    spinner  = ["◐", "◓", "◑", "◒"]

    def fetch():
        def cb(n):
            found[0] = n
        msgs_box[0] = get_my_messages(token, channel_id, user_id, progress_cb=cb)
        done[0] = True

    thread = threading.Thread(target=fetch, daemon=True)
    thread.start()

    frame = 0
    while not done[0]:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        center_text(stdscr, h // 2 - 3, "// ESCANEANDO CANAL //", C_MARCA())
        spin = spinner[frame % len(spinner)]
        center_text(stdscr, h // 2 - 1, f"{spin}  MENSAJES ENCONTRADOS: {found[0]}  {spin}", C_AZUL())
        # ── Nota explicativa de por qué tarda ─────────────────────────────
        center_text(stdscr, h // 2 + 1,
                    "Leyendo de 100 en 100 con pausas — Discord limita la velocidad de lectura",
                    C_TENUE())
        center_text(stdscr, h // 2 + 2,
                    "Canales con muchos mensajes pueden tardar varios minutos. Es normal.",
                    C_TENUE())
        # ──────────────────────────────────────────────────────────────────
        stdscr.refresh()
        time.sleep(0.12)
        frame += 1

    return msgs_box[0]

# ─── PANTALLA DE RESUMEN ───────────────────────────────────────────────────

def summary_screen(stdscr, deleted, errors):
    stdscr.erase()
    h, w = stdscr.getmaxyx()
    center_text(stdscr, h // 2 - 4, "╔══════════════════════╗", C_AZUL())
    center_text(stdscr, h // 2 - 3, "║  OPERACIÓN COMPLETA  ║", C_AZUL())
    center_text(stdscr, h // 2 - 2, "╚══════════════════════╝", C_AZUL())
    center_text(stdscr, h // 2,     f"✓  BORRADOS : {deleted}", C_MENTA())
    center_text(stdscr, h // 2 + 1, f"✗  ERRORES  : {errors}", C_ROJO() if errors else C_TENUE())
    center_text(stdscr, h // 2 + 3, "[ pulsa cualquier tecla para volver ]", C_TENUE())
    stdscr.refresh()
    stdscr.getch()

# ─── FLUJOS ────────────────────────────────────────────────────────────────

def server_flow(stdscr, token, user_id):
    server_id = input_dialog(stdscr, "CANAL DE SERVIDOR", "ID del Servidor:")
    if server_id is None:
        return
    channel_id = input_dialog(stdscr, "CANAL DE SERVIDOR", "ID del Canal:")
    if channel_id is None:
        return

    msgs = searching_overlay(stdscr, token, channel_id, user_id)
    if not msgs:
        show_banner(stdscr, "  NO SE ENCONTRARON MENSAJES EN ESTE CANAL  ", C_AVISO, 2)
        return

    if not message_list_view(stdscr, msgs, f"canal:{channel_id}"):
        return

    if not confirm_dialog(stdscr, "⚠  CONFIRMAR PURGA", [
        f"  Estás a punto de borrar {len(msgs)} mensaje(s).",
        "  Esta acción NO se puede deshacer.", ""
    ]):
        show_banner(stdscr, "  OPERACIÓN CANCELADA  ", C_AVISO, 1.5)
        return

    deleted, errors = delete_progress_view(stdscr, token, channel_id, msgs)
    summary_screen(stdscr, deleted, errors)

def dm_flow(stdscr, token, user_id):
    dm_uid = input_dialog(stdscr, "MENSAJE DIRECTO", "ID del Usuario Destinatario:")
    if dm_uid is None:
        return

    channel_id, err = open_dm(token, dm_uid)
    if channel_id is None:
        show_banner(stdscr, f"  ERROR AL ABRIR DM — HTTP {err}  ", C_ROJO, 2.5)
        return

    msgs = searching_overlay(stdscr, token, channel_id, user_id)
    if not msgs:
        show_banner(stdscr, "  NO SE ENCONTRARON MENSAJES EN ESTE DM  ", C_AVISO, 2)
        return

    if not message_list_view(stdscr, msgs, f"DM:{dm_uid}"):
        return

    if not confirm_dialog(stdscr, "⚠  CONFIRMAR PURGA", [
        f"  Estás a punto de borrar {len(msgs)} mensaje(s) de DM.",
        "  Esta acción NO se puede deshacer.", ""
    ]):
        show_banner(stdscr, "  OPERACIÓN CANCELADA  ", C_AVISO, 1.5)
        return

    deleted, errors = delete_progress_view(stdscr, token, channel_id, msgs)
    summary_screen(stdscr, deleted, errors)

# ─── PUNTO DE ENTRADA ──────────────────────────────────────────────────────

def tui_main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False)
    init_colors()
    stdscr.bkgd(' ', curses.color_pair(5))

    # ── Pantalla de aviso obligatoria al inicio ────────────────────────────
    if not disclaimer_screen(stdscr):
        return
    # ──────────────────────────────────────────────────────────────────────

    token     = None
    user_info = None
    selected  = 0
    num_items = 4

    while True:
        draw_main_menu(stdscr, selected, token is not None, user_info)
        key = stdscr.getch()

        if key in (ord('q'), ord('Q')):
            break
        elif key in (curses.KEY_UP, ord('k')):
            selected = (selected - 1) % num_items
        elif key in (curses.KEY_DOWN, ord('j')):
            selected = (selected + 1) % num_items
        elif key == ord('1'):
            selected = 0
        elif key == ord('2'):
            selected = 1
        elif key == ord('3'):
            selected = 2

        if key in (curses.KEY_ENTER, 10, 13, ord('1'), ord('2'), ord('3')):
            if selected == 0:
                t = input_dialog(stdscr, "AUTENTICACIÓN", "Ingresa tu token de Discord:", secret=True)
                if t:
                    show_banner(stdscr, "  Verificando token…  ", C_TENUE, 0.3)
                    info = get_current_user(t)
                    if info:
                        token     = t
                        user_info = info
                        show_banner(stdscr, f"  AUTENTICADO — {info['username']}  ", C_MENTA, 1.5)
                    else:
                        show_banner(stdscr, "  TOKEN INVÁLIDO O SIN CONEXIÓN  ", C_ROJO, 2)

            elif selected == 1:
                if not token:
                    show_banner(stdscr, "  ESTABLECE EL TOKEN PRIMERO (opción 1)  ", C_ROJO, 1.8)
                else:
                    server_flow(stdscr, token, user_info["id"])

            elif selected == 2:
                if not token:
                    show_banner(stdscr, "  ESTABLECE EL TOKEN PRIMERO (opción 1)  ", C_ROJO, 1.8)
                else:
                    dm_flow(stdscr, token, user_info["id"])

            elif selected == 3:
                break

def main():
    curses.wrapper(tui_main)
    print("\n[DRSCOR MSG DELETER] Sesión terminada.\n")

if __name__ == "__main__":
    main()
