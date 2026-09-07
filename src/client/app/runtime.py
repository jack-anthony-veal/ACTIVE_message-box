from app.api import MessageApiClient
from app.updater import UpdateManager
from start_up.tests import emit_results, run_startup_tests


def startup(updater=None, display_factory=None, input_factory=None, api=None):
    updater = updater or UpdateManager()
    api = api or MessageApiClient()
    state = updater.state()
    recovery = (
        "first_boot"
        if state.get("status") == "checking"
        else updater.prepare_boot()
    )
    if recovery == "rolled_back":
        from machine import reset

        reset()
        return None
    results = run_startup_tests(
        updater,
        recovery,
        display_factory=display_factory,
        input_factory=input_factory,
        api=api,
    )
    healthy = emit_results(results)
    if not healthy:
        if updater.fail_first_boot("critical startup test failed"):
            from machine import reset

            reset()
        return None
    return updater, api


def confirm_healthy(updater):
    updater.mark_healthy()
    try:
        from app.ota_boot import cancel_timer

        cancel_timer()
    except Exception:
        pass
