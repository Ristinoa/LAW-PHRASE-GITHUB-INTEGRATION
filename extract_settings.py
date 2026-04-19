import re

# Patterns
ref_pattern = re.compile(r'#\s*game/script\.rpy:(\d+)')
quoted_pattern = re.compile(r'"(.*?)"')
old_pattern = re.compile(r'^\s*old\s+"(.*?)"')
translate_start = re.compile(r'^\s*translate\s+german\s+strings\s*:')

def extract(INPUT_FILE, OUTPUT_FILE):
    inside_translate = False
    current_ref = None
    results = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
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

    print(f"Done! Extracted {len(results)} entries from {INPUT_FILE} into {OUTPUT_FILE}")


def main():
    input_files = ["options.rpy", "screens.rpy", "common.rpy"]
    output_files = ["options_extracted.txt", "screens_extracted.txt", "common_extracted.txt"]

    for infile, outfile in zip(input_files, output_files):
        extract(infile, outfile)

if __name__ == "__main__":
    main()
