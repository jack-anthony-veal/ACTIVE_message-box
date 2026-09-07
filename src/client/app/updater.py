import os
import ujson

try:
    import uhashlib as hashlib
except ImportError:
    import hashlib

try:
    import ubinascii
except ImportError:
    import binascii as ubinascii

MAX_UPDATE_FILES = 256
MAX_UPDATE_FILE_BYTES = 262144
UPDATE_SPACE_MARGIN_BYTES = 16384
PRESERVED_PATHS = ("config/network.ini", "config/device.ini")
PRESERVED_PREFIXES = ("database/", ".update-", "firmware/")


def _join(root, relative):
    if root in ("", "."):
        return "./" + relative
    return root.rstrip("/") + "/" + relative


def _safe_path(path):
    path = str(path).replace("\\", "/").strip("/")
    parts = path.split("/")
    if not path or any(part in ("", ".", "..") for part in parts):
        raise ValueError("unsafe update path")
    if path in PRESERVED_PATHS or any(path.startswith(prefix) for prefix in PRESERVED_PREFIXES):
        raise ValueError("update targets preserved path: " + path)
    return path


def _mkdirs(path):
    path = str(path).replace("\\", "/")
    absolute = path.startswith("/")
    current = "/" if absolute else ""
    for part in path.split("/"):
        if not part or part == ".":
            continue
        if current in ("", "/"):
            current = current + part
        else:
            current = current + "/" + part
        try:
            os.mkdir(current)
        except OSError:
            pass


def _parent(path):
    normalised = str(path).replace("\\", "/")
    return normalised.rsplit("/", 1)[0] if "/" in normalised else "."


def _exists(path):
    try:
        os.stat(path)
        return True
    except OSError:
        return False


def _is_directory(path):
    try:
        return bool(os.stat(path)[0] & 0x4000)
    except OSError:
        return False


def _remove_tree(path):
    if not _exists(path):
        return
    if not _is_directory(path):
        os.remove(path)
        return
    for name in os.listdir(path):
        _remove_tree(path.rstrip("/") + "/" + name)
    os.rmdir(path)


def _digest(data):
    value = hashlib.sha256(data).digest()
    return ubinascii.hexlify(value).decode("ascii")


def _copy_file(source, destination):
    _mkdirs(_parent(destination))
    with open(source, "rb") as input_file:
        with open(destination, "wb") as output_file:
            while True:
                block = input_file.read(1024)
                if not block:
                    break
                output_file.write(block)


def _digest_file(path):
    value = hashlib.sha256()
    with open(path, "rb") as source:
        while True:
            block = source.read(1024)
            if not block:
                break
            value.update(block)
    return ubinascii.hexlify(value.digest()).decode("ascii")


def _read_json(path, fallback=None):
    try:
        with open(path, "r") as source:
            return ujson.loads(source.read())
    except Exception:
        return fallback


def _write_json(path, value):
    _mkdirs(_parent(path))
    temporary = path + ".tmp"
    with open(temporary, "w") as destination:
        destination.write(ujson.dumps(value))
    try:
        os.remove(path)
    except OSError:
        pass
    os.rename(temporary, path)


class UpdateManager:
    def __init__(self, root="."):
        self.root = root.rstrip("/") or "."
        self.stage = _join(self.root, ".update-stage")
        self.backup = _join(self.root, ".update-backup")
        self.state_file = _join(self.root, "database/update-state.json")
        self.result_file = _join(self.root, "database/update-result.json")

    def state(self):
        value = _read_json(self.state_file, {})
        return value if type(value) is dict else {}

    def queue_result(self, version, success, detail):
        _write_json(
            self.result_file,
            {"version": str(version), "success": bool(success), "detail": str(detail)},
        )

    def prepare_boot(self):
        state = self.state()
        status = state.get("status")
        if status == "pending_health":
            state["status"] = "checking"
            _write_json(self.state_file, state)
            print("UPDATE|first_boot|{}".format(state.get("version", "")))
            return "first_boot"
        if status in ("staging", "backing_up"):
            version = state.get("version", "unknown")
            _remove_tree(self.stage)
            _remove_tree(self.backup)
            state["status"] = "aborted"
            _write_json(self.state_file, state)
            self.queue_result(version, False, "update interrupted before apply")
            print("UPDATE|aborted|{}".format(version))
            return "normal"
        if status in ("checking", "applying", "installing"):
            version = state.get("version", "unknown")
            self.rollback(state)
            self.queue_result(version, False, "startup health did not complete")
            print("UPDATE|rollback|{}".format(version))
            return "rolled_back"
        return "normal"

    def mark_healthy(self):
        state = self.state()
        if state.get("status") != "checking":
            return False
        state["status"] = "healthy"
        _write_json(self.state_file, state)
        self.queue_result(state.get("version", ""), True, "startup health passed")
        print("UPDATE|healthy|{}".format(state.get("version", "")))
        return True

    def fail_first_boot(self, detail):
        state = self.state()
        if state.get("status") != "checking":
            return False
        version = state.get("version", "unknown")
        self.rollback(state)
        self.queue_result(version, False, detail)
        print("UPDATE|rollback|{}".format(version))
        return True

    def flush_result(self, api, device):
        result = _read_json(self.result_file)
        if type(result) is not dict:
            return False
        api.report_update_result(
            result.get("version", ""),
            result.get("success", False),
            result.get("detail", ""),
            device,
        )
        try:
            os.remove(self.result_file)
        except OSError:
            pass
        return True

    def _validate_manifest(self, manifest):
        if (
            type(manifest) is not dict
            or type(manifest.get("version")) is not str
            or not manifest.get("version")
        ):
            raise ValueError("invalid update version")
        files = manifest.get("files")
        if type(files) is not list or not files or len(files) > MAX_UPDATE_FILES:
            raise ValueError("invalid update file list")
        seen = set()
        total_size = 0
        clean_files = []
        for entry in files:
            if type(entry) is not dict:
                raise ValueError("invalid update file entry")
            path = _safe_path(entry.get("path", ""))
            size = entry.get("size")
            checksum = entry.get("sha256")
            if (
                path in seen
                or type(size) is not int
                or size < 0
                or size > MAX_UPDATE_FILE_BYTES
            ):
                raise ValueError("invalid update file metadata")
            if type(checksum) is not str or len(checksum) != 64:
                raise ValueError("invalid update checksum")
            seen.add(path)
            total_size += size
            clean_files.append({"path": path, "size": size, "sha256": checksum.lower()})
        raw_removals = manifest.get("remove", [])
        if type(raw_removals) is not list:
            raise ValueError("invalid update removal list")
        removals = []
        for path in raw_removals:
            path = _safe_path(path)
            if path not in seen and path not in removals:
                removals.append(path)
        return manifest["version"], clean_files, removals, total_size

    def _free_bytes(self):
        stats = os.statvfs(self.root)
        return stats[0] * stats[3]

    def install(self, manifest, api, reset_callback=None):
        version, files, removals, total_size = self._validate_manifest(manifest)
        backup_size = 0
        paths_to_backup = [entry["path"] for entry in files] + removals
        for path in paths_to_backup:
            target = _join(self.root, path)
            if _exists(target) and not _is_directory(target):
                backup_size += os.stat(target)[6]
        if self._free_bytes() < total_size + backup_size + UPDATE_SPACE_MARGIN_BYTES:
            raise OSError("not enough free space for staged update and backup")

        _remove_tree(self.stage)
        _mkdirs(self.stage)
        for entry in files:
            data = api.download_update_file(entry["path"])
            if len(data) != entry["size"] or _digest(data) != entry["sha256"]:
                raise ValueError("update verification failed: " + entry["path"])
            staged = _join(self.stage, entry["path"])
            _mkdirs(_parent(staged))
            with open(staged, "wb") as destination:
                destination.write(data)
            with open(staged, "rb") as source:
                saved = source.read()
            if len(saved) != entry["size"] or _digest(saved) != entry["sha256"]:
                raise OSError("staged file validation failed: " + entry["path"])

        targets = [entry["path"] for entry in files]
        backed_up = []
        for path in targets + removals:
            target = _join(self.root, path)
            if _exists(target) and not _is_directory(target):
                backed_up.append(path)
        state = {
            "status": "backing_up",
            "version": version,
            "files": targets,
            "remove": removals,
            "backed_up": backed_up,
        }
        _write_json(self.state_file, state)
        _remove_tree(self.backup)
        _mkdirs(self.backup)

        for path in backed_up:
            target = _join(self.root, path)
            backup = _join(self.backup, path)
            _copy_file(target, backup)
            if (
                os.stat(target)[6] != os.stat(backup)[6]
                or _digest_file(target) != _digest_file(backup)
            ):
                raise OSError("backup validation failed: " + path)

        state["status"] = "applying"
        _write_json(self.state_file, state)

        try:
            for entry in files:
                staged = _join(self.stage, entry["path"])
                target = _join(self.root, entry["path"])
                _mkdirs(_parent(target))
                incoming = target + ".update"
                try:
                    os.remove(incoming)
                except OSError:
                    pass
                os.rename(staged, incoming)
                try:
                    os.remove(target)
                except OSError:
                    pass
                os.rename(incoming, target)

            for path in removals:
                target = _join(self.root, path)
                try:
                    os.remove(target)
                except OSError:
                    pass
        except Exception as error:
            self.rollback(state)
            _remove_tree(self.stage)
            self.queue_result(version, False, "update apply failed: " + str(error))
            raise

        state["status"] = "pending_health"
        _write_json(self.state_file, state)
        _remove_tree(self.stage)
        print("UPDATE|applied|{}".format(version))
        if reset_callback is None:
            from machine import reset

            reset_callback = reset
        reset_callback()
        return True

    def rollback(self, state=None):
        state = self.state() if state is None else state
        backed_up = state.get("backed_up", [])
        for path in state.get("files", []):
            target = _join(self.root, _safe_path(path))
            if _exists(target) and not _is_directory(target):
                os.remove(target)
            incoming = target + ".update"
            if _exists(incoming) and not _is_directory(incoming):
                os.remove(incoming)
        for path in backed_up:
            path = _safe_path(path)
            backup = _join(self.backup, path)
            target = _join(self.root, path)
            if _exists(backup):
                _mkdirs(_parent(target))
                _copy_file(backup, target)
        state["status"] = "rolled_back"
        _write_json(self.state_file, state)
        return True

    def check_and_install(self, api, reset_callback=None):
        from config.version import APP_VERSION

        manifest = api.get_update_manifest()
        if type(manifest) is not dict or manifest.get("version") == APP_VERSION:
            return False
        return self.install(manifest, api, reset_callback)
