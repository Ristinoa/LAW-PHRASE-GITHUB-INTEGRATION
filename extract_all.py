#!/usr/bin/env python3
"""
Combined extraction script for LAW-PHRASE-GITHUB-INTEGRATION.
Runs both extract_script.py and extract_settings.py logic and outputs to locales/EN/
"""

import re
import os

# Ensure output directory exists
OUTPUT_DIR = "locales/EN"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Regex patterns
ref_pattern = re.compile(r'#\s*(?:game|renpy)/.*\.rpy:\s*(\d+)')
quoted_pattern = re.compile(r'"(.*?)"')
old_pattern = re.compile(r'^\s*old\s+"((?:[^"\\]|\\.)*)"')
translate_start = re.compile(r'^\s*translate\s+\w+\s+strings\s*:')


def extract_from_script_rpy():
    """Extract from script.rpy (original extract_script.py logic)"""
    INPUT_FILE = "script.rpy"
    OUTPUT_FILE = os.path.join(OUTPUT_DIR, "script_extracted.txt")
    
    current_ref = None
    results = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            ref_match = ref_pattern.search(line)
            if ref_match:
                current_ref = ref_match.group(1)
                continue

            if line.strip().startswith("#") and current_ref is not None:
                quotes = quoted_pattern.findall(line)
                for q in quotes:
                    results.append(f'{current_ref} "{q}"')

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("\n".join(results))

    print(f"Extracted {len(results)} comment strings to {OUTPUT_FILE}")
    return len(results)


def extract_from_settings_files():
    """Extract from options.rpy, screens.rpy, common.rpy (original extract_settings.py logic)"""
    input_files = ["options.rpy", "screens.rpy", "common.rpy"]
    output_files = ["options_extracted.txt", "screens_extracted.txt", "common_extracted.txt"]

    total_extracted = 0

    for infile, outfile in zip(input_files, output_files):
        OUTPUT_FILE = os.path.join(OUTPUT_DIR, outfile)
        
        inside_translate = False
        current_ref = None
        results = []

        with open(infile, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()

                # Detect translate-block start (any language)
                if re.match(r'^\s*translate\s+\w+\s+strings\s*:', line):
                    inside_translate = True
                    continue

                if inside_translate:
                    # Exit block on dedented non-blank line
                    if stripped and not line.startswith((" ", "\t")):
                        inside_translate = False
                        current_ref = None
                        continue

                    # Find reference line
                    ref_match = re.search(r'#\s*(?:game|renpy)/.*\.rpy:\s*(\d+)', line)
                    if ref_match:
                        current_ref = ref_match.group(1)
                        continue

                    # Extract old string, including escaped quotes inside the string
                    old_match = re.match(r'^\s*old\s+"((?:[^"\\]|\\.)*)"', line)
                    if old_match and current_ref:
                        results.append(f'{current_ref} "{old_match.group(1)}"')
                    continue

                # Outside translate block (normal comment extraction)
                ref_match = re.search(r'#\s*(?:game|renpy)/.*\.rpy:\s*(\d+)', line)
                if ref_match:
                    current_ref = ref_match.group(1)
                    continue

                if stripped.startswith("#") and current_ref:
                    quotes = re.findall(r'"(.*?)"', line)
                    for q in quotes:
                        results.append(f'{current_ref} "{q}"')

        # Write output
        with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
            out.write("\n".join(results))

        print(f"Done! Extracted {len(results)} entries from {infile} into {OUTPUT_FILE}")
        total_extracted += len(results)

    return total_extracted


def main():
    print("=" * 50)
    print("Running combined extraction script")
    print("=" * 50)
    
    print("\n[1/2] Extracting from script.rpy...")
    script_count = extract_from_script_rpy()
    
    print("\n[2/2] Extracting from settings files (options.rpy, screens.rpy, common.rpy)...")
    settings_count = extract_from_settings_files()
    
    print("\n" + "=" * 50)
    print(f"Complete! Total extracted: {script_count + settings_count} entries")
    print(f"Output files saved to: {OUTPUT_DIR}/")
    print("=" * 50)


if __name__ == "__main__":
    main()