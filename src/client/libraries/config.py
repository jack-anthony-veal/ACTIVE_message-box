class Config:
    def __init__(self):
        pass
    @staticmethod
    def parse(value):
        """Convert an INI string into a basic Python value."""
        value = value.strip()
        lower_value = value.lower()

        if lower_value == "true":
            return True

        if lower_value == "false":
            return False

        if lower_value in ("none", "null"):
            return None

        try:
            return int(value)
        except ValueError:
            pass

        try:
            return float(value)
        except ValueError:
            return value

    @staticmethod
    def format(value):
        """Convert a Python value into an INI-safe string."""
        if value is True:
            return "true"

        if value is False:
            return "false"

        if value is None:
            return "none"

        return str(value)

    @staticmethod
    def read(filename):
        c = Config()
        """
        Read an INI file into a nested dictionary.

        Example:
        {
            "wifi": {
                "ssid": "My WiFi",
                "password": "secret"
            },
            "server": {
                "port": 8080
            }
        }
        """
        config = {}
        current_section = None

        with open(filename, "r") as file:
            for raw_line in file:
                line = raw_line.strip()

                # Ignore empty lines and comments
                if not line or line.startswith("#") or line.startswith(";"):
                    continue

                # Section header
                if line.startswith("[") and line.endswith("]"):
                    current_section = line[1:-1].strip()

                    if current_section not in config:
                        config[current_section] = {}

                    continue

                # Key/value pair
                if "=" not in line:
                    continue

                key, value = line.split("=", 1)

                key = key.strip()
                value = c.parse(value)

                if current_section is None:
                    config[key] = value
                else:
                    config[current_section][key] = value

        return config

    @staticmethod
    def write(filename, config):
        c = Config()
        """
        Write a nested dictionary to an INI file.

        Top-level normal values are written before sections.
        Top-level dictionaries become INI sections.
        """
        with open(filename, "w") as file:
            # Write global values first
            for key, value in config.items():
                if not isinstance(value, dict):
                    file.write("{} = {}\n".format(
                        key,
                        self.format(value)
                    ))

            # Add a blank line between global values and sections
            has_global_values = any(
                not isinstance(value, dict)
                for value in config.values()
            )

            has_sections = any(
                isinstance(value, dict)
                for value in config.values()
            )

            if has_global_values and has_sections:
                file.write("\n")

            # Write sections
            first_section = True

            for section, values in config.items():
                if not isinstance(values, dict):
                    continue

                if not first_section:
                    file.write("\n")

                first_section = False

                file.write("[{}]\n".format(section))

                for key, value in values.items():
                    file.write("{} = {}\n".format(
                        key,
                        c.format(value)
                    ))
