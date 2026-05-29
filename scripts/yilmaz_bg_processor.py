#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JAGUAR LTD - CONSERVATIVE BG REMOVER v4.0 (PYTHON)
- Model: isnet-general-use (Conservatist Mod)
- foreground_threshold: 120 (protects white/shiny metal reflections)
- background_threshold: 30
- erosion_size: 0 (disabled to keep thin rods/extensions intact)
- Hard Background Constraint: Pure White (RGB >= 252) with isnet priority (Alpha <= 30)
- Auto-Detect Internal Details: Skips BG removal if white ratio < 5% in original image
- Zeka Kontrolü: 
    * If shrinkage > 50% (model not sure): skips BG removal entirely, just converts format.
    * If shrinkage > 20%: reverts to safe default background removal.
- Output: WebP (100% Quality)
"""

import os
import sys
import time
import argparse
from pathlib import Path
from PIL import Image
import numpy as np

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from rembg import remove, new_session
except ImportError:
    print("Error: rembg is not installed. Please run pip install rembg.")
    sys.exit(1)

INPUT_DIR = Path("public/images/yilmaz")
OUTPUT_DIR = Path("public/images/yilmaz/Yilmaz_Temiz_Makineler")

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

def process_image(session, input_path, output_path):
    # Load image
    img = Image.open(input_path).convert("RGBA")
    img_np = np.array(img)

    R = img_np[:, :, 0]
    G = img_np[:, :, 1]
    B = img_np[:, :, 2]

    # A. Auto-Detect Internal Details (No background / close-up)
    # Count pixels that are near-white (RGB >= 250)
    white_pixels = np.sum((R >= 250) & (G >= 250) & (B >= 250))
    total_pixels = img_np.shape[0] * img_np.shape[1]
    white_ratio = white_pixels / total_pixels

    if white_ratio < 0.05:  # Less than 5% white background
        print(f"  [i] Makine iç detay görseli tespit edildi (Beyaz arka plan oranı: %{white_ratio*100:.2f}).")
        print(f"  -> Arka plan silme uygulanmıyor, sadece WebP (%100 kalite) formatına dönüştürülüyor...")
        # Save as 100% quality WebP
        img.save(output_path, "WEBP", quality=100)
        return

    # 1. Run default background removal to get a baseline reference mask (Zeka Kontrolü)
    default_res = remove(img, session=session)
    default_np = np.array(default_res)
    area_default = np.sum(default_np[:, :, 3] > 0)

    # 2. Run custom background removal with user's exact conservative parameters
    custom_res = remove(
        img,
        session=session,
        alpha_matting=True,
        alpha_matting_foreground_threshold=120,
        alpha_matting_background_threshold=30,
        alpha_matting_erosion_size=0
    )
    custom_np = np.array(custom_res)
    A = custom_np[:, :, 3]

    # 3. Hard Background Constraint: Pure White (RGB >= 252)
    # Color constraint is put BEHIND geometric analysis:
    # If the pixel is pure white AND isnet Alpha <= 30 (confident background), we clear it.
    # Otherwise, if Alpha > 30, it is part of the machine structure, so we KEEP it (protects shiny white metal).
    is_white = (R >= 252) & (G >= 252) & (B >= 252)
    clear_condition = is_white & (A <= 30)
    custom_np[clear_condition, 3] = 0

    # 4. Zeka Kontrolü & Emin Olunmayan Alan Fallbacks
    area_custom = np.sum(custom_np[:, :, 3] > 0)

    # Fallback Case 1: Extreme shrinkage (> 50% lost) -> Model completely failed / not sure
    if area_default > 0 and area_custom < 0.5 * area_default:
        shrinkage_percent = (1 - (area_custom / area_default)) * 100
        print(f"  [!] UYARI (Emin Olunamadı): Aşırı kırpılma tespit edildi (%{shrinkage_percent:.1f} alan kaybı).")
        print(f"  -> Arka plan silme iptal edildi, orijinal görsel %100 WebP olarak kaydediliyor...")
        img.save(output_path, "WEBP", quality=100)
        return

    # Fallback Case 2: Moderate shrinkage (> 20% lost) -> Revert to safe default background removal
    elif area_default > 0 and area_custom < 0.8 * area_default:
        shrinkage_percent = (1 - (area_custom / area_default)) * 100
        print(f"  [!] UYARI (Zeka Kontrolü): Ana nesne %{shrinkage_percent:.1f} küçüldü (Kırpılma Uyarısı!).")
        print(f"  -> Güvenli varsayılan arka plan silme ayarlarına dönülüyor...")
        
        default_np_clean = default_np.copy()
        default_A = default_np_clean[:, :, 3]
        clear_default = is_white & (default_A <= 30)
        default_np_clean[clear_default, 3] = 0
        final_np = default_np_clean
    else:
        final_np = custom_np

    # Save as 100% quality WebP
    final_img = Image.fromarray(final_np)
    final_img.save(output_path, "WEBP", quality=100)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--single", type=str, help="Process a single file name")
    parser.add_argument("--limit", type=int, help="Limit number of files to process")
    args = parser.parse_args()

    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print()
    print("====================================================")
    print("   JAGUAR LTD - CONSERVATIVE BG REMOVER v4.0         ")
    print("====================================================")
    print(f"  Model: isnet-general-use")
    print(f"  Strategy: Conservatist (Muhafazakar) Mod")
    print(f"  Alpha Matting: True (fg=120, bg=30, erode=0)")
    print(f"  White Constraint: RGB >= 252 (with geometric A <= 30 check)")
    print(f"  Zeka Kontrolü: Auto-Fallback on > 20% / Skip on > 50% shrinkage")
    print(f"  Auto-CloseUp Filter: Active (< 5% white check)")
    print(f"  Output: WebP (100% Quality)")
    print("====================================================\n")

    # Initialize rembg session
    print("[i] Loading ISNet model...")
    t_model_0 = time.time()
    session = new_session("isnet-general-use")
    print(f"[+] Model loaded in {time.time() - t_model_0:.2f}s\n")

    # Scan files
    files = []
    for f in INPUT_DIR.iterdir():
        if f.is_file() and f.suffix.lower() in ALLOWED_EXTENSIONS:
            # Do not process files in the output directory
            files.append(f)

    if args.single:
        single_path = INPUT_DIR / args.single
        if not single_path.exists():
            print(f"[-] Error: File {args.single} not found.")
            sys.exit(1)
        files_to_process = [single_path]
    elif args.limit:
        files_to_process = files[:args.limit]
    else:
        files_to_process = files

    total = len(files_to_process)
    print(f"[i] Found {len(files)} images. Processing {total} images...")

    success_count = 0
    fail_count = 0
    skipped_count = 0
    failed_files = []

    t_start = time.time()

    for idx, fpath in enumerate(files_to_process):
        output_path = OUTPUT_DIR / f"{fpath.stem}.webp"
        percent = ((idx + 1) / total) * 100

        print(f"[{idx + 1}/{total}] ({percent:.1f}%) Processing: {fpath.name}...")

        # Skip if already exists in output (unless we are processing a single file)
        if output_path.exists() and not args.single:
            print(f"  -> Already exists in final output (skipped).")
            skipped_count += 1
            success_count += 1
            continue

        try:
            t0 = time.time()
            process_image(session, fpath, output_path)
            duration = time.time() - t0
            print(f"  -> Success! Processed and saved to WebP in {duration:.2f}s")
            success_count += 1
        except Exception as e:
            print(f"  -> Failed: {str(e)}")
            fail_count += 1
            failed_files.append(fpath.name)

    total_duration_min = (time.time() - t_start) / 60

    print("\n====================================================")
    print("   PROCESSING COMPLETED")
    print("====================================================")
    print(f"  Success: {success_count} (Skipped: {skipped_count})")
    print(f"  Failed:  {fail_count}")
    if failed_files:
        print(f"  Failed files: {failed_files}")
    print(f"  Total time elapsed: {total_duration_min:.2f} minutes")
    print("====================================================\n")

    if fail_count > 0 and total == 1:
        sys.exit(1)

if __name__ == "__main__":
    main()
