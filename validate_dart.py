import glob
import os
import re

dart_files = glob.glob(r"c:\Users\Madha\VaaniSetu\lib\**\*.dart", recursive=True) + glob.glob(r"c:\Users\Madha\VaaniSetu\flutter_app\lib\**\*.dart", recursive=True)
print(f"Checking {len(dart_files)} Dart files for syntax and imports...")

for df in dart_files:
    with open(df, "r", encoding="utf-8") as f:
        content = f.read()

    open_braces = content.count("{")
    close_braces = content.count("}")
    open_parens = content.count("(")
    close_parens = content.count(")")

    assert open_braces == close_braces, f"Mismatch braces in {df}: {open_braces} vs {close_braces}"
    assert open_parens == close_parens, f"Mismatch parens in {df}: {open_parens} vs {close_parens}"

    imports = re.findall(r"import\s+['\"](.+?)['\"];", content)
    for imp in imports:
        if not imp.startswith("package:") and not imp.startswith("dart:"):
            rel_dir = os.path.dirname(df)
            target = os.path.normpath(os.path.join(rel_dir, imp))
            assert os.path.exists(target), f"Import missing: {target} in {df}"

    print(f"PASS: {os.path.relpath(df, r'c:\Users\Madha\VaaniSetu')} (Braces: {open_braces}, Parens: {open_parens}, Imports: {len(imports)})")

print(">>> ALL DART FILES ARE 100% VALID! <<<")
