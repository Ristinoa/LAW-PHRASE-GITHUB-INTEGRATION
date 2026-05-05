#!/usr/bin/env python3
import re
import io
import sys
import os
from collections import defaultdict

# Load translations keyed by numeric reference (e.g. 29 -> translated text)
translation_line_re = re.compile(r'^(\d+)\s*(.*)$')

# Detect the "# game/script.rpy:NN" reference lines
reference_re = re.compile(r'#\s*(?:game|renpy)/.*\.rpy:(\d+)\b')

# Detect the translate english strings: block header
strings_block_start = re.compile(r'^\s*translate\s+english\s+strings\s*:\s*$', re.IGNORECASE)

# Detect an old "..." line (for strings block)
old_line_re = re.compile(r'^(\s*old\s*")(?P<content>.*?)(\".*)$')

# Detect a new "..." line (for strings block)
new_line_re = re.compile(r'^(\s*new\s*")(?P<content>.*?)(\".*)$')

# Generic: find first and last quote on a line (to replace only quoted content)
first_quote_re = re.compile(r'"')

# Commented source lines (e.g. '# "English..."' or '# e "English..."')
commented_source_re = re.compile(r'^\s*#\s*(?:\w+\s+)?".*"$')

# Helper to escape quotes/backslashes for safe insertion into "" in .rpy
def escape_for_rpy(s: str) -> str:
    # Escape backslash first, then double quote
    return s.replace('\\', '\\\\').replace('"', '\\"')

def load_translations(path):
    translations = defaultdict(list)
    with io.open(path, 'r', encoding='utf-8') as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.rstrip('\n')
            if not line.strip():
                continue
            m = translation_line_re.match(line)
            if not m:
                continue
            key, txt = m.groups()
            txt = txt.strip('"„“')
            translations[key].append(txt)
    return translations

def process(original_path, translations, output_path, language):
    out_lines = []
    current_ref = None
    inside_strings_block = False

    with io.open(original_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    total = len(lines)
    while i < total:
        line = lines[i]
        stripped = line.strip()

        # Replace translate english with translate {language}
        if re.match(r'^\s*translate\s+english\s+', line):
            line = line.replace('translate english', f'translate {language}')

        # Detect entering translate english strings: block
        if strings_block_start.match(line):
            inside_strings_block = True
            out_lines.append(line)
            i += 1
            continue

        if inside_strings_block:
            # If we encounter a non-indented (no-leading-space) or blank line that is not part of the block,
            # assume block ended (this mirrors your original file style).
            if stripped == "" or not line.startswith(" "):
                inside_strings_block = False
                current_ref = None
                out_lines.append(line)
                i += 1
                continue

            # Keep reference lines as-is but update current_ref
            ref_m = reference_re.search(line)
            if ref_m:
                current_ref = ref_m.group(1)
                out_lines.append(line)
                i += 1
                continue

            # If this is a new "..." line with empty content, replace with the translation
            new_m = new_line_re.match(line)
            if new_m and current_ref and translations[current_ref]:
                content = new_m.group(2)
                if content.strip() == "":
                    prefix = new_m.group(1)   # includes indentation and 'new "'
                    suffix = new_m.group(3)   # includes closing quote and anything after
                    ch = translations[current_ref].pop(0)
                    ch_escaped = escape_for_rpy(ch)
                    new_line = f'{prefix}{ch_escaped}{suffix}\n'
                    out_lines.append(new_line)
                    i += 1
                    continue

            # otherwise pass through unchanged
            out_lines.append(line)
            i += 1
            continue

        # OUTSIDE strings block:

        # If this line contains a reference comment, update current_ref
        ref_m = reference_re.search(line)
        if ref_m:
            current_ref = ref_m.group(1)
            out_lines.append(line)
            i += 1
            continue

        # If this is a commented source line (e.g. '# "English..."' or '# e "English..."'), keep it,
        # then if the next non-empty line is a quoted empty string or a speaker "" or new "" line, fill it.
        if commented_source_re.match(line):
            out_lines.append(line)
            # look ahead to next line (if any)
            if i + 1 < total:
                next_line = lines[i + 1]
                next_stripped = next_line.strip()
                # Only act if there's a current_ref and a translation exists
                if current_ref and current_ref in translations:
                    # Find the first quote and last quote positions in next_line
                    # We will only replace if content between quotes is empty (or whitespace)
                    quotes = [m.start() for m in first_quote_re.finditer(next_line)]
                    if len(quotes) >= 2:
                        q1 = quotes[0]
                        q2 = quotes[-1]
                        inner = next_line[q1+1:q2]
                        # Only replace if inner is empty (or only whitespace)
                        if inner.strip() == "":
                            # Build new line without changing indentation or anything else except inner text
                            prefix = next_line[:q1+1]   # up to and including first quote
                            suffix = next_line[q2:]     # closing quote and rest (including newline)
                            ch = translations[current_ref].pop(0) if translations[current_ref] else ''
                            ch_escaped = escape_for_rpy(ch)
                            new_next = f'{prefix}{ch_escaped}{suffix}'
                            out_lines.append(new_next)
                            i += 2
                            continue
                # else: either no translation or not an empty-quoted next line; just proceed normally
            i += 1
            continue

        # For safety: if a line itself is a quoted line (not commented) and empty and preceded by a reference (but the comment was missing),
        # we can attempt to insert as well. This handles cases like directly "" after ref.
        # If current_ref exists and this line is an empty quoted string (or e "", d "", new "")
        quotes = [m.start() for m in first_quote_re.finditer(line)]
        if current_ref and len(quotes) >= 2:
            q1 = quotes[0]
            q2 = quotes[-1]
            inner = line[q1+1:q2]
            if inner.strip() == "" and translations[current_ref]:
                prefix = line[:q1+1]
                suffix = line[q2:]
                ch = translations[current_ref].pop(0)
                ch_escaped = escape_for_rpy(ch)
                new_line = f'{prefix}{ch_escaped}{suffix}'
                out_lines.append(new_line)
                i += 1
                continue

        # Default passthrough
        out_lines.append(line)
        i += 1

    # Write output
    with io.open(output_path, 'w', encoding='utf-8') as out_f:
        out_f.writelines(out_lines)

    print(f'✓ Written output to: {output_path}')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 apply_translation.py <lang_code>")
        sys.exit(1)

    lang = sys.argv[1]
    lang_dir = f"locales/EN/{lang}"
    if not os.path.exists(lang_dir):
        print(f"Error: Language folder {lang_dir} does not exist.")
        sys.exit(1)

    lang_map = {
        "de": "german",
        "es_es": "spanish",
        "ja_jp": "japanese",
        "zh": "chinese"
    }

    if lang not in lang_map:
        print(f"Error: Unknown language code {lang}")
        sys.exit(1)

    language = lang_map[lang]
    output_dir = f"output_files/{lang}"
    os.makedirs(output_dir, exist_ok=True)

    # Process each translation file
    for file in os.listdir(lang_dir):
        if not file.endswith('.txt'):
            continue
        if 'common' in file:
            target = 'common.rpy'
        elif 'options' in file:
            target = 'options.rpy'
        elif 'screens' in file:
            target = 'screens.rpy'
        elif 'script' in file:
            target = 'script.rpy'
        else:
            continue  # skip unknown files

        trans_file = os.path.join(lang_dir, file)
        orig_file = f"input_files/{target}"
        out_file = os.path.join(output_dir, target)

        translations = load_translations(trans_file)
        if not translations:
            print(f"Warning: No translations loaded from {trans_file}")
            continue

        process(orig_file, translations, out_file, language)
