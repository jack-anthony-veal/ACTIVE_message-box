from app.updater import UpdateManager


_manager = None
_timer = None
recovery_status = "normal"


def begin():
    global _manager, _timer, recovery_status
    _manager = UpdateManager()
    recovery_status = _manager.prepare_boot()
    if recovery_status == "rolled_back":
        from machine import reset

        reset()
        return recovery_status
    if recovery_status == "first_boot":
        try:
            from machine import Timer, reset

            _timer = Timer(-1)
            _timer.init(
                period=30000,
                mode=Timer.ONE_SHOT,
                callback=lambda timer: reset(),
            )
        except (ImportError, AttributeError, OSError):
            _timer = None
    return recovery_status


def cancel_timer():
    global _timer
    if _timer is not None:
        try:
            _timer.deinit()
        except Exception:
            pass
        _timer = None
