# 🗑️ Discord Message Deleter

Herramienta de línea de comandos para eliminar **tus propios mensajes** de Discord, tanto en canales de servidor como en conversaciones directas (DMs).
----------
 <a href="https://imgbox.com/nBrhOZ4J" target="_blank"><img src="https://thumbs2.imgbox.com/85/81/nBrhOZ4J_t.png" alt="image host"/></a>
----------

## ⚠️ Aviso Legal

> Este script **solo puede borrar tus propios mensajes**. Usar tokens de otras personas viola los [Términos de Servicio de Discord](https://discord.com/terms). Úsalo de forma responsable y solo con tu propio token.

----------

## ✨ Características

-   Elimina todos tus mensajes de un **canal de servidor**
-   Elimina todos tus mensajes de un **DM** con otro usuario
-   Vista previa de mensajes antes de borrar
-   Manejo automático de **rate limits**
-   Resumen final con mensajes borrados y errores

----------

## 📋 Requisitos

-   Python 3.7+
-   Librería `requests`

```bash
pip install requests

```

----------

## 🚀 Uso

```bash
python discord_deleter.py

```

El script te guiará paso a paso:

1.  **Ingresa tu token de Discord**
2.  **Elige el modo:**
    -   `[1]` Canal de servidor → ingresa el ID del servidor y del canal
    -   `[2]` DM → ingresa el ID del usuario
3.  **Revisa los mensajes encontrados** (opcional, muestra hasta 50)
4.  **Confirma** escribiendo `BORRAR` para proceder

----------

## 🔑 Cómo obtener tu token de Discord

> ⚠️ **Nunca compartas tu token con nadie.** Quien lo tenga puede acceder a tu cuenta.

1.  Abre Discord en el navegador o la app de escritorio
2.  Presiona `Ctrl + Shift + I` para abrir las DevTools
3.  Ve a la pestaña **Network** (Red)
4.  Envía cualquier mensaje
5.  Filtra por `/messages` y busca el header `Authorization` en la petición

----------

## 🆔 Cómo obtener IDs en Discord

Activa el **Modo Desarrollador** en Discord: `Ajustes → Avanzado → Modo Desarrollador`

Luego haz clic derecho en cualquier servidor, canal o usuario para copiar su ID.

----------

## 📊 Ejemplo de ejecución

```
=======================================================
   Discord Message Deleter — Solo mensajes propios
=======================================================

[AVISO] Este script solo puede borrar TUS mensajes.

🔑 Ingresa tu token de Discord: ••••••••••••••

✅ Autenticado como: usuario#1234 (ID: 123456789)

¿Dónde deseas borrar mensajes?
  [1] Canal de un servidor
  [2] DM (mensaje directo) con un usuario

Elige opción (1 o 2): 1

ID del servidor: 987654321
ID del canal  : 111222333

🔍 Buscando tus mensajes en el canal 111222333...
  Buscando mensajes....

📊 Encontré 42 mensaje(s) tuyo(s) en ese canal.

⚠️  ¿Confirmas borrar los 42 mensajes? Esto NO se puede deshacer.
Escribe 'BORRAR' para confirmar: BORRAR

🗑️  Borrando mensajes...

  ✅  | Borrado [id]: Hola a todos!
  ✅  | Borrado [id]: ¿Alguien vio el partido?
  ...

📋 RESUMEN
   ✅ Mensajes borrados : 42
   ❌ Errores           : 0

```

----------



## 📁 Estructura del proyecto

```
discord-deleter/
└── discord_deleter.py   # Script principal
└── README.md            # Este archivo

```

----------

## 📄 Licencia

Este proyecto es de uso personal. Úsalo bajo tu propia responsabilidad y respetando los Términos de Servicio de Discord.
