"""Power and DSM-update control.

These operations are destructive and are DISABLED by default: unless
``SYNOLOGY_ENABLE_POWER_CONTROL=true`` the tools are not registered at all,
so the client never sees them.
"""

from __future__ import annotations

from .. import api
from ..app import check, fmt, power_tool


@power_tool()
async def reboot_nas() -> str:
    """Reboot the NAS. [control][power] Requires SYNOLOGY_ENABLE_POWER_CONTROL=true."""
    check(await api.call("SYNO.Core.System", "reboot", version=1))
    return fmt({"action": "reboot", "ok": True})


@power_tool()
async def shutdown_nas() -> str:
    """Shut down (power off) the NAS. [control][power] Requires SYNOLOGY_ENABLE_POWER_CONTROL=true."""
    check(await api.call("SYNO.Core.System", "shutdown", version=1))
    return fmt({"action": "shutdown", "ok": True})


@power_tool()
async def install_dsm_update() -> str:
    """
    Download and install an available DSM update, then reboot. [control][power]
    Requires SYNOLOGY_ENABLE_POWER_CONTROL=true. Check availability first with check_dsm_update.
    """
    check(await api.call("SYNO.Core.Upgrade", "start", version=1))
    return fmt({"action": "install_dsm_update", "started": True})
