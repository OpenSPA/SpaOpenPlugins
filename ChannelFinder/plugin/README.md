# ChannelFinder – Plugin para Enigma2

Busca el nombre de un canal en los bouquets de TV que tú elijas.
Compatible con Dreambox, VU+, Vu+ y cualquier receptor con **Enigma2**.

---

## Estructura de archivos

```
ChannelFinder/
├── __init__.py   ← vacío (requerido por Python)
└── plugin.py     ← código principal
```

---

## Instalación

1. Copia la carpeta `ChannelFinder` completa a tu receptor mediante FTP o SCP:

```
/usr/lib/enigma2/python/Plugins/Extensions/ChannelFinder/
```

2. Reinicia Enigma2 o recarga los plugins:
   - **Menú → Configuración → Sistema → Reiniciar Enigma2**
   - O desde Telnet/SSH: `killall -1 enigma2`

---

## Uso

### Abrir el plugin
- **Menú de plugins** (`Botón azul` → Extensiones → ChannelFinder)
- **Menú de extensiones** (botón azul largo en algunos receptores)

### Flujo de búsqueda

```
┌──────────────────────────────────────────┐
│  Pantalla principal                      │
│  ─────────────────────────────────────── │
│  Nombre del canal: [______________]      │
│                                          │
│  Bouquets: (ninguno)                     │
│                                          │
│  [Salir]  [Buscar]  [Bouquets]           │
└──────────────────────────────────────────┘
         │
         │ Amarillo → Bouquets
         ▼
┌──────────────────────────────────────────┐
│  Seleccionar Bouquets                    │
│  ─────────────────────────────────────── │
│  ✔  Deportes                             │
│       Noticias                           │
│  ✔  Películas HD                         │
│       Infantil                           │
│                                          │
│  [Cancelar] [Buscar »] [Todos/Ninguno]   │
└──────────────────────────────────────────┘
         │
         │ Verde → confirmar
         ▼
┌──────────────────────────────────────────┐
│  Resultados – 3 resultados               │
│  ─────────────────────────────────────── │
│  Canal+ Series  |  Películas HD          │
│  Canal+ HD      |  Deportes              │
│  Canal+ 1       |  Películas HD          │
│                                          │
│  3 canales encontrados      [Cerrar]     │
└──────────────────────────────────────────┘
```

### Controles

| Botón        | Acción                                      |
|-------------|---------------------------------------------|
| Teclado USB  | Escribir nombre del canal                   |
| **Amarillo** | Abrir selección de bouquets                 |
| **Verde / OK** | Iniciar búsqueda                          |
| **Rojo**     | Salir / Cancelar                            |
| **Azul**     | Seleccionar / deseleccionar todos los bouquets |
| **OK** en resultados | Sintonizar el canal seleccionado   |

---

## Notas

- La búsqueda es **insensible a mayúsculas/minúsculas**.
- Puedes buscar fragmentos de nombre (p.ej. "sport" encuentra "Eurosport", "Sport 1", etc.).
- Al pulsar **OK** sobre un resultado, el receptor sintoniza ese canal.
- El plugin lee los bouquets en tiempo real; no necesita configuración previa.
- Si no aparecen bouquets, asegúrate de tener `bouquets.tv` configurado en tu receptor.

---

## Versión

| Campo       | Valor       |
|------------|-------------|
| Versión    | 1.0         |
| Enigma2    | Python 2 / Python 3 compatible |
| Licencia   | GPL v2      |
