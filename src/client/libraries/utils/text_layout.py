def layout_text(text, max_width, measure, max_lines=None):
    if max_width <= 0:
        return []

    text = str(text)
    lines = []

    def append_line(value):
        if max_lines is not None and len(lines) >= max_lines:
            return False
        lines.append(value)
        return True

    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            if not append_line(""):
                break
            continue

        current = ""
        for word in words:
            candidate = word if not current else current + " " + word
            if measure(candidate) <= max_width:
                current = candidate
                continue

            if current:
                if not append_line(current):
                    return lines
                current = ""

            while word and measure(word) > max_width:
                split_at = 0
                for index in range(1, len(word) + 1):
                    if measure(word[:index]) <= max_width:
                        split_at = index
                    else:
                        break

                if split_at == 0:
                    split_at = 1
                if not append_line(word[:split_at]):
                    return lines
                word = word[split_at:]

            current = word

        if current and not append_line(current):
            break

    return lines
