# ╔══════════════════════════════════════════════════════════════════╗
# ║                                                                  ║
# ║   ░█▀▀░█▀█░█▀▄░█▀▀░█░█   ░█▀▄░█▀▀░█░█░█▀▀                     ║
# ║   ░█░░░█░█░█░█░█▀▀░▄▀▄   ░█░█░█▀▀░▀▄▀░▀▀█                     ║
# ║   ░▀▀▀░▀▀▀░▀▀░░▀▀▀░▀░▀   ░▀▀░░▀▀▀░░▀░░▀▀▀                     ║
# ║                                                                  ║
# ║            © 2026 CodeX Devs — All Rights Reserved              ║
# ║                                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

"""Localización de los comandos de barra (slash) y de sus equivalentes con prefijo.

Cada entrada usa como clave el nombre *actual* (en inglés) del comando y define:

* ``name``: nuevo nombre en español (solo el último tramo; en los subcomandos el
  grupo padre se conserva).
* ``description``: descripción en español con el formato ``emoji | texto``.

Al aplicar la localización se conserva el nombre antiguo como alias del comando
con prefijo, de modo que ``>ban`` sigue funcionando aunque el comando ahora sea
``>banear`` y ``/banear``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.zyrox import zyrox


# comando actual -> (nuevo nombre, descripción con emoji)
COMMANDS: dict[str, tuple[str, str]] = {
    # ── General ──────────────────────────────────────────────────────────
    "avatar": ("avatar", "🖼️ | Muestra el avatar y el banner de un usuario o servidor."),
    "servericon": ("iconoservidor", "🏠 | Muestra el icono del servidor en varios formatos."),
    "membercount": ("miembros", "👥 | Muestra el número total de miembros del servidor."),
    "poll": ("encuesta", "📊 | Crea una encuesta rápida con reacciones."),
    "urban": ("urban", "📖 | Busca el significado de una palabra en Urban Dictionary."),
    "disconnect": ("desconectar", "🔌 | Desconecta el bot del canal de voz."),
    # ── Automoderación ───────────────────────────────────────────────────
    "automod": ("automod", "🤖 | Gestiona la automoderación y sus filtros."),
    "automod enable": ("activar", "✅ | Activa la automoderación en el servidor."),
    "automod punishment": ("castigo", "⚖️ | Configura el castigo para los eventos de automod."),
    "automod ignore": ("ignorar", "🚫 | Gestiona los canales y roles exentos de automod."),
    "automod ignore channel": ("canal", "📁 | Añade un canal a la lista de exentos."),
    "automod ignore role": ("rol", "🏷️ | Añade un rol a la lista de exentos."),
    "automod ignore show": ("ver", "👁️ | Muestra los canales y roles exentos."),
    "automod ignore reset": ("restablecer", "♻️ | Restablece la lista de exentos."),
    "automod unignore": ("permitir", "✅ | Quita canales y roles de la lista de exentos."),
    "automod unignore channel": ("canal", "📁 | Quita un canal de la lista de exentos."),
    "automod unignore role": ("rol", "🏷️ | Quita un rol de la lista de exentos."),
    "automod disable": ("desactivar", "❌ | Desactiva la automoderación en el servidor."),
    "automod config": ("configuracion", "⚙️ | Muestra la configuración actual de automod."),
    "automod logging": ("registros", "📋 | Establece el canal de registros de automod."),
    # ── Bienvenidas ──────────────────────────────────────────────────────
    "greet": ("bienvenida", "👋 | Gestiona los mensajes de bienvenida del servidor."),
    "greet setup": ("configurar", "🛠️ | Configura el mensaje de bienvenida."),
    "greet reset": ("restablecer", "♻️ | Elimina la configuración de bienvenida."),
    "greet channel": ("canal", "📢 | Establece el canal de bienvenidas."),
    "greet test": ("probar", "🧪 | Envía un mensaje de bienvenida de prueba."),
    "greet config": ("configuracion", "⚙️ | Muestra la configuración de bienvenida."),
    "greet autodelete": ("autoeliminar", "⏱️ | Configura la eliminación automática del mensaje."),
    "greet edit": ("editar", "✏️ | Edita el mensaje de bienvenida actual."),
    # ── Juegos ───────────────────────────────────────────────────────────
    "chess": ("ajedrez", "♟️ | Juega al ajedrez contra otro usuario."),
    "rps": ("ppt", "✊ | Juega piedra, papel o tijera contra el bot o un usuario."),
    "tic-tac-toe": ("tresenraya", "⭕ | Juega al tres en raya contra otro usuario."),
    "wordle": ("wordle", "🟩 | Juega una partida de Wordle contra el bot."),
    "2048": ("2048", "🔢 | Juega al 2048 con el bot."),
    "memory-game": ("memoria", "🧠 | Pon a prueba tu memoria con este juego."),
    "number-slider": ("deslizador", "🔀 | Ordena los números deslizándolos."),
    "battleship": ("hundirflota", "🚢 | Juega a hundir la flota con un amigo."),
    "connectfour": ("conecta4", "🔴 | Juega al conecta 4 contra otro usuario."),
    "lights-out": ("luces", "💡 | Apaga todas las luces del tablero."),
    # ── Información y utilidades ─────────────────────────────────────────
    "banner": ("banner", "🎨 | Muestra el banner de un usuario o del servidor."),
    "banner server": ("servidor", "🏠 | Muestra el banner del servidor."),
    "banner user": ("usuario", "👤 | Muestra el banner de un usuario."),
    "serverinfo": ("infoservidor", "🏠 | Muestra información detallada del servidor."),
    "userinfo": ("infousuario", "👤 | Muestra información detallada de un usuario."),
    "roleinfo": ("inforol", "🏷️ | Muestra información detallada de un rol."),
    "list": ("lista", "📋 | Lista miembros, roles, canales y más."),
    "list boosters": ("boosters", "🚀 | Lista los boosters del servidor."),
    "list bans": ("baneados", "🔨 | Lista los usuarios baneados del servidor."),
    "list inrole": ("enrol", "🏷️ | Lista los miembros que tienen un rol."),
    "list emojis": ("emojis", "😀 | Lista los emojis del servidor con sus IDs."),
    "list roles": ("roles", "🏷️ | Lista todos los roles del servidor con sus IDs."),
    "list bots": ("bots", "🤖 | Lista todos los bots del servidor."),
    "list admins": ("admins", "🛡️ | Lista todos los administradores del servidor."),
    "list invoice": ("envoz", "🔊 | Lista los usuarios de un canal de voz."),
    "list moderators": ("moderadores", "🔨 | Lista todos los moderadores del servidor."),
    "list early": ("earlysupporter", "🌟 | Lista los miembros con la insignia Early Supporter."),
    "list activedeveloper": ("desarrolladoractivo", "💻 | Lista los miembros con la insignia de desarrollador activo."),
    "list createdat": ("creacioncuenta", "📅 | Lista las fechas de creación de las cuentas."),
    "list joinedat": ("ingreso", "📆 | Lista las fechas de ingreso al servidor."),
    "vcinfo": ("infovoz", "🔊 | Muestra información de un canal de voz."),
    "channelinfo": ("infocanal", "📁 | Muestra información de un canal."),
    "ping": ("ping", "🏓 | Comprueba la latencia del bot."),
    "report": ("reportar", "🐛 | Reporta un error al equipo de desarrollo."),
    # ── Roles personalizados ─────────────────────────────────────────────
    "setup": ("rolespersonalizados", "🛠️ | Configura los roles personalizados del servidor."),
    "setup staff": ("staff", "🛠️ | Configura el rol de Staff en el servidor."),
    "setup girl": ("girl", "🛠️ | Configura el rol de Girl en el servidor."),
    "setup vip": ("vip", "🛠️ | Configura el rol VIP en el servidor."),
    "setup guest": ("guest", "🛠️ | Configura el rol de Guest en el servidor."),
    "setup friend": ("friend", "🛠️ | Configura el rol de Friend en el servidor."),
    "setup reqrole": ("rolrequerido", "🔑 | Configura el rol requerido para usar los comandos."),
    "setup config": ("configuracion", "⚙️ | Muestra la configuración de roles personalizados."),
    "setup create": ("crear", "➕ | Crea un comando de rol personalizado."),
    "setup delete": ("eliminar", "➖ | Elimina un comando de rol personalizado."),
    "setup list": ("lista", "📋 | Lista los roles personalizados configurados."),
    "setup reset": ("restablecer", "♻️ | Restablece la configuración de roles personalizados."),
    "staff": ("staff", "🛠️ | Otorga el rol de Staff al usuario."),
    "girl": ("girl", "💖 | Otorga el rol de Girl al usuario."),
    "vip": ("vip", "⭐ | Otorga el rol VIP al usuario."),
    "guest": ("guest", "👋 | Otorga el rol de Guest al usuario."),
    "friend": ("friend", "🤝 | Otorga el rol de Friend al usuario."),
    # ── AFK y embeds ─────────────────────────────────────────────────────
    "afk": ("afk", "💤 | Establece tu estado AFK con un motivo."),
    "embed": ("embed", "🧩 | Crea y envía un embed personalizado."),
    # ── Multimedia ───────────────────────────────────────────────────────
    "media": ("media", "🖼️ | Gestiona el canal exclusivo para multimedia."),
    "media setup": ("configurar", "📁 | Configura el canal exclusivo para multimedia."),
    "media remove": ("eliminar", "🗑️ | Elimina el canal exclusivo para multimedia."),
    "media config": ("configuracion", "⚙️ | Muestra la configuración del canal de multimedia."),
    "media bypass": ("exentos", "✅ | Gestiona los usuarios exentos del canal de multimedia."),
    "media bypass add": ("agregar", "➕ | Añade un usuario a la lista de exentos."),
    "media bypass remove": ("quitar", "➖ | Quita un usuario de la lista de exentos."),
    "media bypass show": ("ver", "👁️ | Muestra la lista de usuarios exentos."),
    # ── Sorteos ──────────────────────────────────────────────────────────
    "gstart": ("sorteo-iniciar", "🎁 | Inicia un nuevo sorteo."),
    "gend": ("sorteo-finalizar", "🏁 | Finaliza un sorteo antes de tiempo."),
    "greroll": ("sorteo-reroll", "🔄 | Elige un nuevo ganador del sorteo."),
    "glist": ("sorteo-lista", "📋 | Muestra los sorteos activos."),
    # ── Utilidades varias ────────────────────────────────────────────────
    "steal": ("robar", "🎭 | Roba un emoji o sticker para el servidor."),
    "timer": ("temporizador", "⏱️ | Inicia un temporizador en el canal."),
    "nightmode": ("modonoche", "🌙 | Gestiona el modo nocturno del servidor."),
    "nightmode enable": ("activar", "🌙 | Activa el modo nocturno."),
    "nightmode disable": ("desactivar", "☀️ | Desactiva el modo nocturno."),
    "profile": ("perfil", "🪪 | Muestra el perfil y las insignias de un usuario."),
    # ── Anti-Nuke y lista blanca ─────────────────────────────────────────
    "antinuke": ("antinuke", "🛡️ | Activa o desactiva la protección Anti-Nuke."),
    "whitelist": ("listablanca", "📋 | Añade un usuario a la lista blanca de Anti-Nuke."),
    "whitelisted": ("verlistablanca", "👁️ | Muestra los usuarios en la lista blanca."),
    "whitelistreset": ("restablecerlistablanca", "♻️ | Restablece la lista blanca de Anti-Nuke."),
    "unwhitelist": ("quitarlistablanca", "➖ | Quita un usuario de la lista blanca de Anti-Nuke."),
    "extraowner": ("propietariosextra", "👑 | Añade o gestiona propietarios extra del servidor."),
    "stats": ("estadisticas", "📊 | Muestra las estadísticas y la información del bot."),
    # ── Filtros ──────────────────────────────────────────────────────────
    "filter": ("filtro", "🧽 | Gestiona los filtros de palabras del servidor."),
    "filter enable": ("activar", "✅ | Activa un filtro de palabras."),
    "filter disable": ("desactivar", "❌ | Desactiva el filtro actual."),
    # ── Tickets ──────────────────────────────────────────────────────────
    "ticket": ("ticket", "🎟️ | Gestiona el sistema de tickets del servidor."),
    "ticket setup": ("configurar", "🛠️ | Inicia la configuración del panel de tickets."),
    "ticket close": ("cerrar", "🔒 | Cierra el ticket actual."),
    "ticket lock": ("bloquear", "🔐 | Bloquea el ticket actual."),
    "ticket unlock": ("desbloquear", "🔓 | Desbloquea el ticket actual."),
    "ticket claim": ("reclamar", "✋ | Reclama el ticket actual."),
    "ticket transcript": ("transcripcion", "📄 | Genera una transcripción del ticket."),
    # ── Registros ────────────────────────────────────────────────────────
    "log": ("registros", "📝 | Gestiona los registros del servidor."),
    "log setup": ("configurar", "🛠️ | Configura los canales de registro."),
    "log status": ("estado", "📊 | Muestra la configuración de registros."),
    "log search": ("buscar", "🔍 | Busca eventos registrados con filtros."),
    "log reset": ("restablecer", "♻️ | Restablece la configuración de registros."),
    "log toggle": ("alternar", "🔁 | Activa o desactiva categorías de registro."),
    "log config": ("configuracion", "⚙️ | Abre el menú de configuración de registros."),
    "log ignore": ("ignorar", "🚫 | Gestiona canales, roles y usuarios ignorados."),
    "log test": ("probar", "🧪 | Envía mensajes de registro de prueba."),
    "log export": ("exportar", "📤 | Exporta los registros como archivo JSON."),
    # ── Roles por reacción ───────────────────────────────────────────────
    "createrr": ("crearrolreaccion", "🎭 | Crea un rol por reacción."),
    "dmrr": ("rolespormd", "📩 | Activa o desactiva los MD en los roles por reacción."),
    "hinglish": ("hinglish", "🗣️ | Traduce Hinglish informal a inglés correcto."),
    # ── Niveles ──────────────────────────────────────────────────────────
    "setlevelrole": ("establecerrolnivel", "🏷️ | Asigna un rol a un nivel específico."),
    "removelevelrole": ("quitarserolnivel", "➖ | Quita el rol asignado a un nivel."),
    "listlevelroles": ("listarrolesnivel", "📋 | Lista todos los roles de nivel."),
    "resetxp": ("reiniciarxp", "♻️ | Restablece el XP de un usuario."),
    "setxp": ("establecerxp", "✨ | Establece el XP de un usuario."),
    "setlevel": ("establecernivel", "📈 | Establece el nivel de un usuario."),
    # ── Verificación ─────────────────────────────────────────────────────
    "verification": ("verificacion", "✅ | Gestiona el sistema de verificación."),
    "verification setup": ("configurar", "🛠️ | Configura el sistema de verificación."),
    "verification status": ("estado", "📊 | Muestra el estado de la verificación."),
    "verification fix": ("reparar", "🔧 | Repara los permisos del sistema de verificación."),
    "verification disable": ("desactivar", "❌ | Desactiva el sistema de verificación."),
    "verification enable": ("activar", "✅ | Activa el sistema de verificación."),
    "verification logs": ("registros", "📋 | Muestra los registros de verificación."),
    "verification reset": ("restablecer", "♻️ | Restablece los permisos de verificación."),
    "verification verify": ("verificar", "✅ | Verifica manualmente a un usuario."),
    # ── Minecraft ────────────────────────────────────────────────────────
    "minecraft": ("minecraft", "⛏️ | Consulta el estado de un servidor de Minecraft."),
    "minecraft setup": ("configurar", "🛠️ | Configura el estado de un servidor de Minecraft."),
    "minecraft reset": ("restablecer", "♻️ | Elimina la configuración de Minecraft."),
    "minecraft status": ("estado", "📊 | Muestra el estado del servidor de Minecraft."),
    # ── Moderación ───────────────────────────────────────────────────────
    "ban": ("banear", "🔨 | Banea a un usuario del servidor."),
    "unban": ("desbanear", "🔓 | Desbanea a un usuario del servidor."),
    "mute": ("silenciar", "🔇 | Silencia a un usuario temporalmente."),
    "unmute": ("desilenciar", "🔊 | Quita el silencio a un usuario."),
    "lock": ("bloquear", "🔒 | Bloquea un canal para impedir mensajes."),
    "unlock": ("desbloquear", "🔓 | Desbloquea un canal para permitir mensajes."),
    "hide": ("ocultar", "🙈 | Oculta un canal de @everyone."),
    "unhide": ("mostrar", "👁️ | Muestra un canal a @everyone."),
    "kick": ("expulsar", "👢 | Expulsa a un miembro del servidor."),
    "warn": ("advertir", "⚠️ | Advierte a un usuario del servidor."),
    "clearwarns": ("limpiaradvertencias", "🧹 | Borra las advertencias de un usuario."),
    "unlockall": ("desbloqueartodo", "🔓 | Desbloquea todos los canales del servidor."),
    "lockall": ("bloqueartodo", "🔒 | Bloquea todos los canales del servidor."),
    "give": ("darrol", "🎭 | Otorga un rol al usuario mencionado."),
    "hideall": ("ocultartodo", "🙈 | Oculta todos los canales del servidor."),
    "unhideall": ("mostrartodo", "👁️ | Muestra todos los canales del servidor."),
    "prefix": ("prefijo", "⚙️ | Cambia el prefijo del bot en el servidor."),
    "clone": ("clonar", "🧬 | Clona un canal con su configuración."),
    "nick": ("apodo", "📝 | Cambia el apodo de un miembro."),
    "nuke": ("recrearcanal", "💥 | Elimina y recrea un canal."),
    "slowmode": ("modolento", "🐌 | Cambia el modo lento del canal."),
    "unslowmode": ("quitarmodolento", "🚀 | Desactiva el modo lento del canal."),
    "unbanall": ("desbaneartodo", "🔓 | Desbanea a todos los usuarios del servidor."),
    "audit": ("auditoria", "📜 | Muestra las acciones recientes de auditoría."),
}


def _walk_app_commands(commands):
    for command in commands:
        yield command
        children = getattr(command, "commands", None)
        if children:
            yield from _walk_app_commands(children)


def _walk_prefix_commands(commands):
    for command in commands:
        yield command
        children = getattr(command, "commands", None)
        if children:
            yield from _walk_prefix_commands(children)


def apply_localization(bot: "zyrox") -> None:
    """Aplica los nombres y descripciones en español al árbol de comandos.

    Se ejecuta una sola vez, después de cargar las extensiones y antes de
    sincronizar los comandos de barra con Discord.
    """
    app_commands = {cmd.qualified_name: cmd for cmd in _walk_app_commands(bot.tree.get_commands())}
    prefix_commands = {cmd.qualified_name: cmd for cmd in _walk_prefix_commands(bot.walk_commands())}

    for old_path, (new_name, description) in COMMANDS.items():
        old_leaf = old_path.split()[-1]

        app_command = app_commands.get(old_path)
        if app_command is not None:
            app_command.name = new_name
            app_command.description = description

            # El comando con prefijo asociado a un híbrido también debe cambiar.
            wrapped = getattr(app_command, "wrapped", None)
            if wrapped is not None and wrapped is not prefix_commands.get(old_path):
                _rename_prefix_command(wrapped, old_leaf, new_name, description)

        prefix_command = prefix_commands.get(old_path)
        if prefix_command is not None:
            _rename_prefix_command(prefix_command, old_leaf, new_name, description)

    # Al renombrar un comando, discord.py conserva las claves antiguas en
    # ``all_commands`` (tanto en el bot como en cada grupo). Reconstruimos el
    # índice para que los nuevos nombres y los alias antiguos resuelvan bien.
    _rebuild_command_index(bot)

    # El árbol de comandos de barra guarda índices internos por nombre
    # (``tree._global_commands`` y ``Group._children``). Si solo cambiamos
    # ``command.name``, Discord invoca el nombre nuevo pero el árbol sigue
    # buscando el viejo y lanza ``CommandNotFound``. Reindexamos también.
    _reindex_app_tree(bot.tree)


def _reindex_app_tree(tree) -> None:
    _reindex_mapping(getattr(tree, "_global_commands", {}))
    for mapping in getattr(tree, "_guild_commands", {}).values():
        _reindex_mapping(mapping)
    for command in getattr(tree, "_global_commands", {}).values():
        _reindex_app_group(command)
    for mapping in getattr(tree, "_guild_commands", {}).values():
        for command in mapping.values():
            _reindex_app_group(command)


def _reindex_mapping(mapping) -> None:
    commands = list(dict.fromkeys(mapping.values()))
    mapping.clear()
    for command in commands:
        mapping[command.name] = command


def _reindex_app_group(group) -> None:
    children = getattr(group, "_children", None)
    if not children:
        return
    _reindex_mapping(children)
    for child in children.values():
        _reindex_app_group(child)


def _rebuild_command_index(group) -> None:
    members = set(group.all_commands.values())
    group.all_commands.clear()
    for member in members:
        group.all_commands[member.name] = member
        for alias in member.aliases:
            group.all_commands.setdefault(alias, member)
        if hasattr(member, "all_commands"):
            _rebuild_command_index(member)


def _rename_prefix_command(command, old_leaf: str, new_name: str, description: str) -> None:
    command.name = new_name
    command.help = description
    command.description = description

    aliases = list(command.aliases)
    if old_leaf != new_name and old_leaf not in aliases:
        aliases.append(old_leaf)
    command.aliases = aliases
