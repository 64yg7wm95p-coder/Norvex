SCAN_STATUS = {
    "is_running": False,
    "current": 0,
    "total": 0,
    "msg": "",
    "status_type": "info"
}


def set_scan_status(
    is_running: bool,
    current: int,
    total: int,
    msg: str,
    status_type: str = "info"
):
    SCAN_STATUS.clear()

    SCAN_STATUS.update({
        "is_running": is_running,
        "current": current,
        "total": total,
        "msg": msg,
        "status_type": status_type
    })