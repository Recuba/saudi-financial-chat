"""
Script to normalize parquet files with consistent scale factors.

Run: python scripts/normalize_parquet.py
"""

import shutil
import pandas as pd
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_processing import CURRENCY_COLUMNS


def normalize_analytics_view(input_path: Path, output_path: Path) -> None:
    """Normalize analytics_view.parquet."""
    print(f"Processing {input_path}...")

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_parquet(input_path)

    print(f"  Original rows: {len(df)}")

    if 'scale_factor' not in df.columns:
        print("  Warning: No scale_factor column found, skipping normalization")
        return

    print(f"  Scale factor distribution:")
    print(df['scale_factor'].value_counts())

    # Normalize currency columns
    for col in CURRENCY_COLUMNS:
        if col in df.columns:
            df[col] = df[col] * df['scale_factor']

    # Set scale_factor to 1 (all now normalized)
    df['scale_factor'] = 1

    # Save
    df.to_parquet(output_path, index=False)
    print(f"  Saved to {output_path}")


def normalize_facts_numeric(input_path: Path, output_path: Path, filings_path: Path) -> None:
    """Normalize facts_numeric.parquet using filing scale factors."""
    print(f"Processing {input_path}...")

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if not filings_path.exists():
        raise FileNotFoundError(f"Filings file not found: {filings_path}")

    df = pd.read_parquet(input_path)
    filings = pd.read_parquet(filings_path)

    print(f"  Original rows: {len(df)}")

    # Merge scale_factor from filings
    df = df.merge(
        filings[['filing_id', 'scale_factor']],
        on='filing_id',
        how='left'
    )

    # Warn about missing scale factors
    nan_count = df['scale_factor'].isna().sum()
    if nan_count > 0:
        print(f"  Warning: {nan_count} rows have no scale_factor, defaulting to 1")

    # Normalize value_sar
    df['value_sar'] = df['value_sar'] * df['scale_factor'].fillna(1)

    # Drop scale_factor column
    df = df.drop(columns=['scale_factor'])

    # Save
    df.to_parquet(output_path, index=False)
    print(f"  Saved to {output_path}")


def main():
    data_dir = Path(__file__).parent.parent / "data"
    backup_dir = data_dir / "backup"
    backup_dir.mkdir(exist_ok=True)

    # Backup originals
    print("Creating backups...")
    for f in ['analytics_view.parquet', 'facts_numeric.parquet']:
        src = data_dir / f
        if src.exists():
            shutil.copy(src, backup_dir / f)
            print(f"  Backed up {f}")
        else:
            print(f"  Warning: {f} not found, skipping backup")

    # Normalize
    normalize_analytics_view(
        data_dir / "analytics_view.parquet",
        data_dir / "analytics_view.parquet"
    )

    normalize_facts_numeric(
        data_dir / "facts_numeric.parquet",
        data_dir / "facts_numeric.parquet",
        data_dir / "filings.parquet"
    )

    print("\nDone! Original files backed up to data/backup/")


if __name__ == "__main__":
    main()
