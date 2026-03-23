
# 🗑️ DRSCOR — Discord Message Deleter
**Elimina tus propios mensajes de Discord desde una interfaz visual en terminal.**
Soporta canales de servidor, conversaciones directas (DMs) y grupos (Group DMs).

---

## 📸 Capturas

<div align="center">
  <img src="https://thumbs2.imgbox.com/39/71/x2tqBM5f_t.png" width="45%" alt="Lista de mensajes"/>
  <br/>
  <img src="https://thumbs2.imgbox.com/3b/f4/g1nJQW4z_t.png" width="45%" alt="Progreso de borrado"/>
  <img src="https://thumbs2.imgbox.com/b1/0c/grIL4YWI_t.png" width="45%" alt="Resumen final"/>
</div>

---

## ⚠️ Aviso Legal

> Este script **solo puede borrar tus propios mensajes**.
> Usar tokens ajenos viola los [Términos de Servicio de Discord](https://discord.com/terms).
> Úsalo de forma responsable y únicamente con tu propia cuenta.
> Al iniciar la aplicación se te pedirá aceptar explícitamente estas condiciones.

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
| 💬 **Servidores y DMs** | Funciona en canales de servidor y mensajes directos |
| 👥 **Grupos (Group DMs)** | Soporte para borrar mensajes en conversaciones de grupo |
| 🔄 **Reintentos automáticos** | Gestión de errores de red con backoff exponencial |
| 📝 **Log de errores** | Registro detallado en `drscor_errors.log` |

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
3. Elige el modo:
     [2] Canal de servidor
     [3] Mensaje directo (DM)
     [4] Grupo (Group DM)
4. Ingresa los IDs necesarios según el modo elegido
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

| Modo | IDs necesarios |
|---|---|
| Canal de servidor | ID del Servidor + ID del Canal |
| Mensaje directo | ID del Usuario destinatario |
| Grupo | Se selecciona de la lista automática |

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
Discord-Message-Deleter/
├── Discord-Message-Deleter.py          # Script principal
├── drscor_errors.log  # Log de errores (se genera automáticamente)
└── README.md
```

---

## 🐢 ¿Por qué es lento?

Discord impone **límites de peticiones (rate limits)** estrictos en su API. Para proteger tu cuenta de bloqueos o baneos temporales, el script aplica:

- Esperas aleatorias entre cada borrado (~0.8s ± variación)
- Pausas automáticas al alcanzar los límites de la API
- Reintentos con backoff exponencial ante errores de red

Cuantos más mensajes tengas, más tardará. **Es completamente normal.**

---

## 📄 Licencia

Proyecto de uso personal. Úsalo bajo tu propia responsabilidad y respetando los [Términos de Servicio de Discord](https://discord.com/terms).
