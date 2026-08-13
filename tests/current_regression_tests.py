import importlib.util
import os
import subprocess
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = []


def check(name, function):
    try:
        function()
        RESULTS.append(("PASS", name, ""))
    except Exception as error:
        RESULTS.append(("FAIL", name, type(error).__name__ + ": " + str(error)))


def load_navigator():
    path = os.path.join(ROOT, "scripts", "app", "StateNavigator.py")
    spec = importlib.util.spec_from_file_location("navigator_direct", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.StateNavigator


class State:
    def __init__(self):
        self.entered = 0
        self.exited = 0
        self.updated = 0
        self.drawn = 0
        self.inputs = []

    def enter_state(self):
        self.entered += 1

    def exit_state(self):
        self.exited += 1

    def update(self):
        self.updated += 1

    def draw(self):
        self.drawn += 1

    def handle_input(self, event, event_type=None):
        self.inputs.append((event, event_type))


def test_start_accepts_state_instance():
    manager = load_navigator()(object())
    state = State()
    manager.start(state)
    assert manager.current_state() is state
    assert state.entered == 1


def test_push_replace_pop():
    manager = load_navigator()(object())
    first = State()
    second = State()
    third = State()
    manager.start(first)
    manager.push_state(second)
    assert manager.current_state() is second
    manager.replace_state(third)
    assert manager.current_state() is third
    assert manager.pop_state() is first


def test_root_pop_is_guarded():
    manager = load_navigator()(object())
    state = State()
    manager.start(state)
    manager.pop_state()
    assert manager.current_state() is state


def test_input_none_type_forwarding():
    manager = load_navigator()(object())
    state = State()
    manager.start(state)
    manager.handle_input(1, None)
    assert state.inputs == [(1, None)]


def test_package_import_graph():
    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, "device_tests", "full_local_tests.py")],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip().splitlines()[-1])


check("StateNavigator.start accepts a state instance", test_start_accepts_state_instance)
check("StateNavigator push/replace/pop sequence", test_push_replace_pop)
check("StateNavigator root pop guard", test_root_pop_is_guarded)
check("StateNavigator forwards optional event_type", test_input_none_type_forwarding)
check("State package import graph", test_package_import_graph)


for status, name, detail in RESULTS:
    print(status + " | " + name + (" | " + detail if detail else ""))

failures = [result for result in RESULTS if result[0] == "FAIL"]
print("SUMMARY | passed=" + str(len(RESULTS) - len(failures)) + " failed=" + str(len(failures)))
sys.exit(1 if failures else 0)
