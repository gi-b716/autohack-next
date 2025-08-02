#!/usr/bin/env python3
"""
Simple msgfmt implementation to compile .po files to .mo files.
"""
import struct
import array
from pathlib import Path


def make(po_file, mo_file):
    """
    Compile a .po file to .mo file.
    """
    with open(po_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    messages = {}
    msgid = ""
    msgstr = ""
    in_msgid = False
    in_msgstr = False

    for line in lines:
        line = line.strip()

        if line.startswith("msgid "):
            if msgid and msgstr:
                messages[msgid] = msgstr
            msgid = line[6:].strip('"')
            msgstr = ""
            in_msgid = True
            in_msgstr = False

        elif line.startswith("msgstr "):
            msgstr = line[7:].strip('"')
            in_msgid = False
            in_msgstr = True

        elif line.startswith('"') and (in_msgid or in_msgstr):
            content = line.strip('"')
            if in_msgid and msgid is not None:
                msgid += content
            elif in_msgstr and msgstr is not None:
                msgstr += content

        elif line == "" or line.startswith("#"):
            if msgid and msgstr:
                messages[msgid] = msgstr
            msgid = ""
            msgstr = ""
            in_msgid = False
            in_msgstr = False

    # Add the last message
    if msgid and msgstr:
        messages[msgid] = msgstr

    # Remove empty header and empty messages
    messages = {
        k: v
        for k, v in messages.items()
        if k and v and not k.startswith("Project-Id-Version")
    }

    if not messages:
        # Create a minimal .mo file
        with open(mo_file, "wb") as f:
            # Magic number (little endian)
            f.write(struct.pack("<L", 0x950412DE))
            # Version
            f.write(struct.pack("<L", 0))
            # Number of strings
            f.write(struct.pack("<L", 0))
            # Offset of key table
            f.write(struct.pack("<L", 28))
            # Offset of value table
            f.write(struct.pack("<L", 28))
            # Size of hash table
            f.write(struct.pack("<L", 0))
            # Offset of hash table
            f.write(struct.pack("<L", 28))
        return

    # Prepare data
    keys = sorted(messages.keys())
    values = [messages[k] for k in keys]

    # Encode strings as UTF-8
    kencoded = [k.encode("utf-8") for k in keys]
    vencoded = [v.encode("utf-8") for v in values]

    # Calculate offsets
    keyoffsets = []
    valueoffsets = []
    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart

    # Calculate key positions
    offset = keystart
    for k in kencoded:
        keyoffsets.append(offset)
        offset += len(k)

    # Calculate value positions
    valuestart = offset
    offset = valuestart
    for v in vencoded:
        valueoffsets.append(offset)
        offset += len(v)

    # Write .mo file
    with open(mo_file, "wb") as f:
        # Magic number (little endian)
        f.write(struct.pack("<L", 0x950412DE))
        # Version
        f.write(struct.pack("<L", 0))
        # Number of strings
        f.write(struct.pack("<L", len(keys)))
        # Offset of key table
        f.write(struct.pack("<L", 28))
        # Offset of value table
        f.write(struct.pack("<L", 28 + len(keys) * 8))
        # Size of hash table
        f.write(struct.pack("<L", 0))
        # Offset of hash table
        f.write(struct.pack("<L", 28 + len(keys) * 16))

        # Write key descriptors
        for i, k in enumerate(kencoded):
            f.write(struct.pack("<L", len(k)))
            f.write(struct.pack("<L", keyoffsets[i]))

        # Write value descriptors
        for i, v in enumerate(vencoded):
            f.write(struct.pack("<L", len(v)))
            f.write(struct.pack("<L", valueoffsets[i]))

        # Write keys
        for k in kencoded:
            f.write(k)

        # Write values
        for v in vencoded:
            f.write(v)


def compile_translations():
    """Compile all .po files to .mo files."""
    locale_dir = Path(__file__).parent / "locale"

    for po_file in locale_dir.rglob("*.po"):
        mo_file = po_file.with_suffix(".mo")

        print(f"Compiling {po_file} -> {mo_file}")

        try:
            make(str(po_file), str(mo_file))
            print(f"  ✓ Success")
        except Exception as e:
            print(f"  ✗ Error: {e}")


if __name__ == "__main__":
    compile_translations()
