# 🗑️ Discord Message Deleter

**Elimina tus propios mensajes de Discord desde una interfaz visual en terminal.**
Soporta canales de servidor y conversaciones directas (DMs).

---

## 📸 Capturas

<div align="center">
  <img src="https://thumbs2.imgbox.com/39/71/x2tqBM5f_t.png" width="45%" alt="Lista de mensajes"/>
  <br/>
  <img src="https://thumbs2.imgbox.com/89/93/8Oo6VLN0_t.png" width="45%" alt="Progreso de borrado"/>
  <img src="https://thumbs2.imgbox.com/b1/0c/grIL4YWI_t.png" width="45%" alt="Resumen final"/>
</div>

---

## ⚠️ Aviso Legal

> Este script **solo puede borrar tus propios mensajes**.
> Usar tokens ajenos viola los [Términos de Servicio de Discord](https://discord.com/terms).
> Úsalo de forma responsable y únicamente con tu propia cuenta.

---

## ✨ Características

| | |
|---|---|
| 🖥️ **Interfaz TUI** | Interfaz visual interactiva en terminal con `curses` |
| 🔐 **Token seguro** | El token se ingresa oculto con caracteres `*` |
| 📜 **Lista navegable** | Revisa todos tus mensajes con scroll antes de borrar |
| 📊 **Progreso en vivo** | Barra de progreso y registro de operaciones en tiempo real |
| ⚡ **Rate limit inteligente** | Esperas aleatorias automáticas para evitar bloqueos de Discord |
| 🛡️ **Aviso obligatorio** | Pantalla de aceptación explícita al iniciar |
| 💬 **Servidores y DMs** | Funciona tanto en canales de servidor como en mensajes directos |

---

## 📋 Requisitos

- Python 3.7+
- Librería `requests`
- `curses` — incluido en Python estándar en Linux/macOS

```bash
pip install requests

# Solo en Windows:
pip install windows-curses
```

---

### Flujo de uso
```
1. Acepta el aviso de uso escribiendo  ACEPTO
2. Opción [1] → Ingresa tu token de Discord
3. Opción [2] Canal de servidor  /  [3] Mensaje directo
4. Ingresa los IDs del servidor y canal (o el ID del usuario en DMs)
5. Navega la lista de mensajes encontrados con ↑ ↓
6. Confirma la purga escribiendo  BORRAR
7. Observa el progreso en tiempo real y el resumen final
```

---

## 🔑 Cómo obtener tu token de Discord

> ⚠️ **Nunca compartas tu token con nadie.** Quien lo tenga tiene acceso total a tu cuenta.

1. Abre Discord en el **navegador** o la **app de escritorio**
2. Pulsa `Ctrl + Shift + I` para abrir las DevTools
3. Ve a la pestaña **Network** (Red)
4. Envía cualquier mensaje en cualquier canal
5. Filtra las peticiones por `/messages`
6. Abre la petición y busca el header `Authorization` — ese es tu token

---

## 🆔 Cómo obtener IDs en Discord

Activa el **Modo Desarrollador** en Discord:

`Ajustes de usuario → Avanzado → Modo Desarrollador ✅`

Con eso activado, haz **clic derecho** sobre cualquier servidor, canal o usuario y selecciona **"Copiar ID"**.

---

## ⌨️ Atajos de teclado

| Tecla | Acción |
|:---:|---|
| `↑` `↓` &nbsp;/&nbsp; `k` `j` | Navegar menú y lista de mensajes |
| `Enter` | Seleccionar / Confirmar |
| `PgUp` `PgDn` | Saltar páginas en la lista |
| `Home` `End` | Ir al primer / último mensaje |
| `q` `Esc` | Cancelar / Salir |

---

## 📁 Estructura del proyecto

```
Discord-Message-Deleter
├── discord_delete.py   
└── README.md
```

---

## 📄 Licencia

Proyecto de uso personal. Úsalo bajo tu propia responsabilidad y respetando los [Términos de Servicio de Discord](https://discord.com/terms).
