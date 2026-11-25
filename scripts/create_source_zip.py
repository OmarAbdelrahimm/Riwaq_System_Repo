"""
RUWAQ V04 Source Archiver
Packages complete clean source code including geometry construction, materials,
camera choreography, and Remotion animation logic into RUWAQ_BAB_ZUWAYLA_V04_SOURCE.zip.
"""

import os
import shutil
import zipfile

def create_source_zip():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    out_dir = os.path.join(base_dir, 'public')
    os.makedirs(out_dir, exist_ok=True)
    zip_path_public = os.path.join(out_dir, 'RUWAQ_BAB_ZUWAYLA_V04_SOURCE.zip')
    zip_path_root = os.path.join(base_dir, 'RUWAQ_BAB_ZUWAYLA_V04_SOURCE.zip')

    included_dirs = ['src', 'scripts', 'public/assets']
    included_files = [
        'package.json',
        'tsconfig.json',
        'vite.config.ts',
        'index.html',
        'metadata.json',
        'BabZuwaylaRemotion_V04.tsx',
        'BabZuwaylaRemotion.tsx',
        'V04_GEOMETRY_CHANGELOG.md',
        'V04_GEOMETRY_SOURCES.md',
    ]

    print(f"📦 Packaging complete clean V04 source code to {zip_path_public}...")
    with zipfile.ZipFile(zip_path_public, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for f in included_files:
            full_path = os.path.join(base_dir, f)
            if os.path.exists(full_path):
                zipf.write(full_path, f)
                print(f"  + {f}")

        for d in included_dirs:
            full_dir = os.path.join(base_dir, d)
            if os.path.exists(full_dir):
                for root, _, files in os.walk(full_dir):
                    for file in files:
                        if file.endswith('.zip') or file.endswith('.mp4') or file.endswith('.glb'):
                            continue
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, base_dir)
                        zipf.write(file_path, rel_path)
                        print(f"  + {rel_path}")

    shutil.copyfile(zip_path_public, zip_path_root)
    # Also write legacy name for backward compatibility
    shutil.copyfile(zip_path_public, os.path.join(out_dir, 'RUWAQ_BAB_ZUWAYLA_3D_SOURCE.zip'))

    size_kb = os.path.getsize(zip_path_public) / 1024
    print(f"✅ V04 Source package created successfully: {zip_path_public} ({size_kb:.1f} KB)")

if __name__ == '__main__':
    create_source_zip()
