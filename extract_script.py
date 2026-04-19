import re

INPUT_FILE = "script.rpy"
OUTPUT_FILE = "script_extracted.txt"

# Regex pattern to detect the reference line
ref_pattern = re.compile(r'#\s*game/script\.rpy\s*:\s*(\d+)')
# Regex pattern to extract quoted text inside commented lines
quoted_pattern = re.compile(r'"(.*?)"')

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
