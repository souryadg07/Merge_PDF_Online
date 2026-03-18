"""
merge_pdfs.py — Lossless PDF merger using pypdf

Simply run with no arguments to auto-detect PDFs in the current folder:
    python3 merge_pdfs.py

Or pass files/folders explicitly:
    python3 merge_pdfs.py file1.pdf file2.pdf -o merged.pdf
    python3 merge_pdfs.py /path/to/folder/ -o out.pdf
"""

import argparse
import sys
import time
from pathlib import Path
from typing import List

try:
    from pypdf import PdfWriter, PdfReader
except ImportError:
    print("pypdf not found. Install it with:  pip install pypdf")
    sys.exit(1)


def collect_pdfs_from_cwd() -> List[Path]:
    """Find all PDFs in the current working directory, sorted alphabetically."""
    return sorted(Path(".").glob("*.pdf"))


def collect_pdfs(inputs: List[str]) -> List[Path]:
    """Resolve input arguments to a list of PDF paths."""
    paths = []
    for item in inputs:
        p = Path(item)
        if p.is_dir():
            found = sorted(p.glob("*.pdf"))
            if not found:
                print(f"  [!] No PDFs found in directory: {p}")
            paths.extend(found)
        else:
            if not p.exists():
                print(f"  [!] File not found, skipping: {p}")
            elif p.suffix.lower() != ".pdf":
                print(f"  [!] Not a PDF, skipping: {p}")
            else:
                paths.append(p)
    return paths


def ask_order(pdf_paths: List[Path]) -> List[Path]:
    """
    Show the detected PDFs and let the user specify a custom merge order.
    Returns the reordered list.
    """
    print("\nPDFs found in current directory:\n")
    for i, p in enumerate(pdf_paths, 1):
        try:
            reader = PdfReader(str(p), strict=False)
            pages = len(reader.pages)
        except Exception:
            pages = "?"
        print(f"  [{i}]  {p.name}  ({pages} pages)")

    print()
    print("Enter the merge order as space-separated numbers (e.g.  3 1 2)")
    print("Press ENTER to keep the current order shown above.")
    print()

    while True:
        raw = input("  Order: ").strip()

        # Empty → keep current order
        if not raw:
            print("  -> Using current order.")
            return pdf_paths

        try:
            indices = [int(x) for x in raw.split()]
        except ValueError:
            print("  [!] Please enter numbers only, separated by spaces.")
            continue

        # Validate range
        invalid = [n for n in indices if n < 1 or n > len(pdf_paths)]
        if invalid:
            print(f"  [!] Invalid number(s): {invalid}. Choose between 1 and {len(pdf_paths)}.")
            continue

        # Warn if some files are omitted
        if len(set(indices)) < len(pdf_paths):
            omitted = [pdf_paths[i - 1].name for i in range(1, len(pdf_paths) + 1) if i not in indices]
            print(f"  [!] Warning: these files will be omitted from the merge: {omitted}")
            confirm = input("  Continue anyway? [y/N]: ").strip().lower()
            if confirm != "y":
                continue

        reordered = [pdf_paths[i - 1] for i in indices]

        print("\n  Merge order confirmed:")
        for step, p in enumerate(reordered, 1):
            print(f"    {step}. {p.name}")
        print()
        return reordered


def ask_output_name() -> Path:
    """Ask the user for an output filename."""
    raw = input("  Output filename [merged.pdf]: ").strip()
    name = raw if raw else "merged.pdf"
    if not name.lower().endswith(".pdf"):
        name += ".pdf"
    return Path(name)


def merge_pdfs(pdf_paths: List[Path], output_path: Path) -> None:
    """
    Merge PDFs with zero quality loss.

    pypdf copies page objects directly — no re-rendering, no re-compression —
    so images, fonts, and vector graphics are preserved at full fidelity.
    """
    if not pdf_paths:
        print("No valid PDF files to merge.")
        sys.exit(1)

    writer = PdfWriter()
    total_pages = 0

    print(f"Merging {len(pdf_paths)} file(s)  ->  {output_path}\n")

    for pdf_path in pdf_paths:
        try:
            reader = PdfReader(str(pdf_path), strict=False)
            n = len(reader.pages)
            writer.append_pages_from_reader(reader)
            total_pages += n
            print(f"  +  {pdf_path.name}  ({n} page{'s' if n != 1 else ''})")
        except Exception as exc:
            print(f"  x  {pdf_path.name}  — skipped ({exc})")

    # Preserve metadata from the first file
    try:
        first_reader = PdfReader(str(pdf_paths[0]), strict=False)
        if first_reader.metadata:
            writer.add_metadata(first_reader.metadata)
    except Exception:
        pass

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        writer.write(f)

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"\n  Done — {total_pages} pages, {size_mb:.2f} MB  ->  {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lossless PDF merger. Run with no arguments for interactive mode."
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="PDF files or directories (optional — defaults to current directory)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output file path (skips the filename prompt)",
    )
    parser.add_argument(
        "--no-reorder",
        action="store_true",
        help="Skip the reorder prompt and merge in the detected order",
    )

    args = parser.parse_args()

    # Collect PDFs
    if args.inputs:
        pdf_paths = collect_pdfs(args.inputs)
    else:
        pdf_paths = collect_pdfs_from_cwd()

    if not pdf_paths:
        print("No PDF files found. Nothing to merge.")
        sys.exit(1)

    # Ask for order
    if not args.no_reorder:
        pdf_paths = ask_order(pdf_paths)
    else:
        print(f"\nFound {len(pdf_paths)} PDF(s) — merging in detected order.")

    # Ask for output name
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = ask_output_name()

    print()
    start = time.perf_counter()
    merge_pdfs(pdf_paths, output_path)
    elapsed = time.perf_counter() - start
    print(f"  Time: {elapsed:.2f}s\n")


if __name__ == "__main__":
    main()