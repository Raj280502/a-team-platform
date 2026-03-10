"""Create empty CSS stubs for all missing CSS imports across generated projects."""
import re
from pathlib import Path

base = Path("app/workspace/generated_projects")
count = 0

for ext in ("*.jsx", "*.js", "*.tsx", "*.ts"):
    for source_file in base.rglob(ext):
        if "node_modules" in str(source_file):
            continue
        try:
            content = source_file.read_text(encoding="utf-8")
            for m in re.finditer(r"""import\s+['"](\./|\.\./)?(.*?\.css)['"]""", content):
                prefix = m.group(1) or "./"
                css_rel = m.group(2)
                css_path = (source_file.parent / (prefix + css_rel)).resolve()
                if not css_path.exists():
                    css_path.parent.mkdir(parents=True, exist_ok=True)
                    css_path.write_text(
                        f"/* Auto-generated stub for {css_path.name} */\n",
                        encoding="utf-8",
                    )
                    print(f"  Created: {css_path.name}")
                    count += 1
        except Exception as e:
            print(f"  Warning: {source_file.name}: {e}")

print(f"\nCreated {count} CSS stub(s)")
