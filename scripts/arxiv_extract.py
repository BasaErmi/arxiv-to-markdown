#!/usr/bin/env python3
"""
Extract arxiv HTML paper: download text content and images.

Usage:
    python3 arxiv_extract.py <arxiv_url> <output_dir> [--images-dir <dir>]

Example:
    python3 arxiv_extract.py https://arxiv.org/html/2503.02247v5 ./output --images-dir ./output/assets

Output:
    - raw_content.txt   : Plain text extracted by trafilatura
    - images_map.json   : Mapping of image filenames to figure captions
    - Downloaded images  : Saved to images-dir
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error


def check_dependencies():
    """Check and report missing dependencies."""
    missing = []
    try:
        import trafilatura
    except ImportError:
        missing.append("trafilatura")
    try:
        import lxml.html.clean
    except ImportError:
        try:
            import lxml_html_clean
        except ImportError:
            missing.append("lxml_html_clean")
    return missing


def fetch_html(url):
    """Fetch HTML content from URL."""
    # Normalize URL: remove fragment
    url = url.split("#")[0]
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_text(url):
    """Extract article text using trafilatura."""
    import trafilatura
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return None
    text = trafilatura.extract(downloaded, favor_recall=True, include_tables=True)
    return text


def extract_images_and_captions(html, base_url):
    """Parse HTML to find images and their figure captions."""
    figures = re.findall(r"<figure[^>]*>(.*?)</figure>", html, re.DOTALL)
    images_map = {}
    for fig in figures:
        img_match = re.search(r'<img[^>]*src=["\']([^"\']+)["\']', fig)
        caption_match = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", fig, re.DOTALL)
        if img_match:
            src = img_match.group(1)
            # Skip base64 data URIs
            if src.startswith("data:"):
                continue
            # Build caption text (strip HTML tags)
            caption = ""
            if caption_match:
                caption = re.sub(r"<[^>]+>", "", caption_match.group(1)).strip()
                # Collapse whitespace
                caption = re.sub(r"\s+", " ", caption)
            images_map[src] = caption
    return images_map


def download_image(url, save_path):
    """Download a single image."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        with open(save_path, "wb") as f:
            f.write(data)
        return len(data)
    except Exception as e:
        print(f"  FAILED to download {url}: {e}", file=sys.stderr)
        return 0


def main():
    parser = argparse.ArgumentParser(description="Extract arxiv HTML paper content and images")
    parser.add_argument("url", help="arxiv HTML URL (e.g. https://arxiv.org/html/2503.02247v5)")
    parser.add_argument("output_dir", help="Output directory for extracted content")
    parser.add_argument("--images-dir", help="Directory to save images (default: <output_dir>/assets)")
    args = parser.parse_args()

    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}", file=sys.stderr)
        print("Install with: pip3 install " + " ".join(missing), file=sys.stderr)
        sys.exit(1)

    url = args.url.split("#")[0]  # Remove fragment
    output_dir = args.output_dir
    images_dir = args.images_dir or os.path.join(output_dir, "assets")

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    # Step 1: Extract text
    print("Extracting text content...")
    text = extract_text(url)
    if not text:
        print("ERROR: Failed to extract text content.", file=sys.stderr)
        sys.exit(1)

    text_path = os.path.join(output_dir, "raw_content.txt")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"  Saved raw text: {text_path} ({len(text)} chars)")

    # Step 2: Fetch HTML and extract images
    print("Fetching HTML for image extraction...")
    html = fetch_html(url)

    images_map = extract_images_and_captions(html, url)
    print(f"  Found {len(images_map)} figures")

    # Step 3: Download images
    downloaded = {}
    for src, caption in images_map.items():
        # Build full URL
        if src.startswith("http"):
            img_url = src
        else:
            img_url = url.rstrip("/") + "/" + src

        filename = os.path.basename(src)
        save_path = os.path.join(images_dir, filename)

        print(f"  Downloading {filename}...")
        size = download_image(img_url, save_path)
        if size > 0:
            downloaded[filename] = {
                "caption": caption,
                "size_bytes": size,
                "local_path": save_path,
            }
            print(f"    OK ({size:,} bytes)")

    # Step 4: Save images map
    map_path = os.path.join(output_dir, "images_map.json")
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(downloaded, f, ensure_ascii=False, indent=2)
    print(f"\nSaved images map: {map_path}")

    # Summary
    print(f"\n--- Summary ---")
    print(f"Text:   {text_path} ({len(text):,} chars)")
    print(f"Images: {len(downloaded)} downloaded to {images_dir}")
    print(f"Map:    {map_path}")


if __name__ == "__main__":
    main()
