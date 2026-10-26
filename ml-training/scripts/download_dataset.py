"""
Download NSL-KDD dataset for training
"""
import urllib.request
import os
from pathlib import Path
import sys

# Dataset URLs
DATASETS = {
    'train': 'https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTrain%2B.txt',
    'test': 'https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTest%2B.txt',
}

# Column names for NSL-KDD dataset
COLUMNS = [
    'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
    'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in',
    'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
    'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login',
    'is_guest_login', 'count', 'srv_count', 'serror_rate', 'srv_serror_rate',
    'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate',
    'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
    'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
    'dst_host_srv_diff_host_rate', 'dst_host_serror_rate', 'dst_host_srv_serror_rate',
    'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'label', 'difficulty'
]


def download_file(url: str, destination: Path):
    """Download file with progress bar"""
    print(f"Downloading: {url}")
    print(f"Destination: {destination}")

    def progress_hook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write(f"\r Progress: {percent}%")
        sys.stdout.flush()

    try:
        urllib.request.urlretrieve(url, destination, progress_hook)
        print("\n✅ Download complete")
        return True
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        return False


def main():
    """Main download function"""
    print("=" * 60)
    print("NSL-KDD Dataset Downloader")
    print("=" * 60)

    # Get script directory
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'data' / 'raw'

    # Create data directory
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nData directory: {data_dir}")

    # Download datasets
    for name, url in DATASETS.items():
        filename = f"KDD{name.capitalize()}+.txt"
        destination = data_dir / filename

        if destination.exists():
            print(f"\n⚠️  {filename} already exists. Skipping download.")
            continue

        print(f"\n📥 Downloading {name} dataset...")
        success = download_file(url, destination)

        if success:
            # Add column names as header
            with open(destination, 'r') as f:
                content = f.read()

            with open(destination.with_suffix('.csv'), 'w') as f:
                f.write(','.join(COLUMNS) + '\n')
                f.write(content)

            print(f"✅ Created CSV with headers: {destination.with_suffix('.csv')}")

    print("\n" + "=" * 60)
    print("✅ Dataset download complete!")
    print("=" * 60)
    print(f"\nFiles downloaded to: {data_dir}")
    print("\nNext steps:")
    print("  1. Run: python ml-training/scripts/train_model.py")
    print("  2. This will train the Isolation Forest model")
    print("=" * 60)


if __name__ == "__main__":
    main()
