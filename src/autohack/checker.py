from .i18n import _


def basicChecker(output: bytes, answer: bytes) -> tuple[bool, str]:
    """
    Compare output and answer content, ignoring trailing spaces and trailing newlines.

    Args:
        output: The output content as bytes
        answer: The expected answer content as bytes

    Returns:
        tuple[bool, str]: (is_match, message)
    """

    def process_content(content: bytes) -> list[str]:
        """Process content by removing trailing spaces from each line and trailing empty lines"""
        try:
            # Decode bytes to string, handling different encodings
            text = content.decode("utf-8", errors="replace")
        except UnicodeDecodeError:
            text = content.decode("latin-1", errors="replace")

        lines = text.splitlines()

        # Remove trailing spaces from each line
        lines = [line.rstrip() for line in lines]

        # Remove trailing empty lines
        while lines and lines[-1] == "":
            lines.pop()

        return lines

    output_lines = process_content(output)
    answer_lines = process_content(answer)

    # Compare line by line
    max_lines = max(len(output_lines), len(answer_lines))

    for line_idx in range(max_lines):
        output_line = output_lines[line_idx] if line_idx < len(output_lines) else ""
        answer_line = answer_lines[line_idx] if line_idx < len(answer_lines) else ""

        if output_line != answer_line:
            # Find first differing column (1-based)
            col = 1
            min_len = min(len(output_line), len(answer_line))
            while col <= min_len and output_line[col - 1] == answer_line[col - 1]:
                col += 1

            return (
                False,
                _("Difference found at line {0}, column {1}.").format(
                    line_idx + 1, col
                ),
            )

    return (True, _("No differences found."))
