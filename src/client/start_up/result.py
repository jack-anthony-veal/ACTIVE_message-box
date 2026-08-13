class TestResult:
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"

    def __init__(
        self,
        name,
        status,
        message="",
        critical=False,
        data=None
    ):
        self.name = name
        self.status = status
        self.message = message
        self.critical = critical
        self.data = data or {}

    @property
    def passed(self):
        return self.status == self.PASS

    def __repr__(self):
        return "{}: {} - {}".format(
            self.name,
            self.status,
            self.message
        )
