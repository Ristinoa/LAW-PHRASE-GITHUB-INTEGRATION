#!/usr/bin/env python3
import io
import os
import re

REFERENCE_RE = re.compile(r'^\s*#\s*[^:]+:(\d+)\s*$')
COMMENT_SOURCE_RE = re.compile(r'^\s*#\s*(?:\w+\s+)?(?P<quote>["\'])(?P<text>.*?)(?P=quote)\s*$')
OLD_STRING_RE = re.compile(r'^\s*old\s+(?P<quote>["\'])(?P<text>.*?)(?P=quote)\s*$')


def normalize_text(text: str) -> str:
    return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').strip()


def extract_strings_from_file(path):
    entries = []
    current_ref = None

    with io.open(path, 'r', encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.rstrip('\n')

            ref_match = REFERENCE_RE.match(line)
            if ref_match:
                current_ref = ref_match.group(1)
                continue

            if current_ref is None:
                continue

            old_match = OLD_STRING_RE.match(line)
            if old_match:
                text = old_match.group('text')
                entries.append((current_ref, text))
                current_ref = None
                continue

            comment_match = COMMENT_SOURCE_RE.match(line)
            if comment_match:
                text = comment_match.group('text')
                entries.append((current_ref, text))
                current_ref = None
                continue

            # Keep the current reference active while we skip block structure lines
            # such as translate directives or blank padding lines.
            continue

    return entries


def write_reference_sheet(entries, output_path):
    with io.open(output_path, 'w', encoding='utf-8') as out_f:
        for ref, text in entries:
            safe_text = normalize_text(text)
            out_f.write(f'{ref} "{safe_text}"\n')


def main():
    input_dir = os.path.join('input_files')
    output_dir = os.path.join('locales', 'EN')
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.isdir(input_dir):
        raise SystemExit(f'Error: Input directory not found: {input_dir}')

    for file_name in sorted(os.listdir(input_dir)):
        if not file_name.endswith('.rpy'):
            continue

        input_path = os.path.join(input_dir, file_name)
        entries = extract_strings_from_file(input_path)
        if not entries:
            print(f'Warning: No strings extracted from {input_path}')

        base_name, _ = os.path.splitext(file_name)
        output_name = f'{base_name}_Sacrifice.txt'
        output_path = os.path.join(output_dir, output_name)
        write_reference_sheet(entries, output_path)
        print(f'Written {output_path} ({len(entries)} entries)')


if __name__ == '__main__':
    main()
