import os
import argparse
import numpy as np
import pandas as pd

def generate_mock_ieee_cis(output_dir: str, num_samples: int = 1000):
    """
    Generate synthetic IEEE-CIS Fraud Detection dataset format 
    (Transaction & Identity features) if raw files are not present.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    np.random.seed(42)
    tx_ids = np.arange(2987000, 2987000 + num_samples)
    
    # Transaction table features
    df_tx = pd.DataFrame({
        "TransactionID": tx_ids,
        "isFraud": np.random.choice([0, 1], size=num_samples, p=[0.965, 0.035]),
        "TransactionDT": np.sort(np.random.randint(86400, 86400 * 30, size=num_samples)),
        "TransactionAmt": np.round(np.random.lognormal(mean=4.0, sigma=1.0, size=num_samples), 2),
        "ProductCD": np.random.choice(["W", "H", "C", "S", "R"], size=num_samples),
        "card1": np.random.randint(1000, 18000, size=num_samples),
        "card2": np.random.randint(100, 600, size=num_samples),
        "card4": np.random.choice(["visa", "mastercard", "discover", "american express"], size=num_samples),
        "card6": np.random.choice(["debit", "credit"], size=num_samples),
        "addr1": np.random.randint(100, 500, size=num_samples),
        "dist1": np.random.exponential(scale=20, size=num_samples),
        "P_emaildomain": np.random.choice(["gmail.com", "yahoo.com", "hotmail.com", "anonymous.com"], size=num_samples),
        "C1": np.random.poisson(lam=1.5, size=num_samples),
        "C2": np.random.poisson(lam=1.2, size=num_samples),
        "V1": np.random.choice([0, 1, np.nan], size=num_samples, p=[0.8, 0.15, 0.05]),
        "V2": np.random.choice([0, 1, np.nan], size=num_samples, p=[0.8, 0.15, 0.05]),
    })

    # Identity table features (subset of transactions)
    id_sample_size = int(num_samples * 0.25)
    id_tx_ids = np.random.choice(tx_ids, size=id_sample_size, replace=False)
    df_id = pd.DataFrame({
        "TransactionID": id_tx_ids,
        "id_01": np.random.uniform(-100, 0, size=id_sample_size),
        "id_02": np.random.randint(10000, 999999, size=id_sample_size),
        "id_12": np.random.choice(["NotFound", "Found"], size=id_sample_size),
        "DeviceType": np.random.choice(["desktop", "mobile"], size=id_sample_size),
        "DeviceInfo": np.random.choice(["Windows", "iOS", "Android", "MacOS"], size=id_sample_size)
    })

    tx_path = os.path.join(output_dir, "train_transaction.csv")
    id_path = os.path.join(output_dir, "train_identity.csv")
    df_tx.to_csv(tx_path, index=False)
    df_id.to_csv(id_path, index=False)
    print(f"[+] Prepared IEEE-CIS raw datasets at: {output_dir}")

def download_from_kaggle(raw_dir: str) -> bool:
    """Attempt to download real IEEE-CIS dataset via Kaggle API if credentials exist."""
    try:
        import subprocess
        print("[*] Attempting Kaggle CLI download for ieee-fraud-detection...")
        os.makedirs(raw_dir, exist_ok=True)
        res = subprocess.run(
            ["kaggle", "competitions", "download", "-c", "ieee-fraud-detection", "-p", raw_dir],
            capture_output=True, text=True
        )
        if res.returncode == 0:
            print("[+] Successfully downloaded Kaggle dataset archive. Extracting...")
            import zipfile
            zip_path = os.path.join(raw_dir, "ieee-fraud-detection.zip")
            if os.path.exists(zip_path):
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(raw_dir)
                return True
    except Exception as e:
        print(f"[-] Kaggle CLI download skipped/unavailable: {e}")
    return False

def process_ieee_cis(raw_dir: str, processed_dir: str):
    """ETL process: merges identity & transaction features, imputes, cleans."""
    os.makedirs(processed_dir, exist_ok=True)

    tx_path = os.path.join(raw_dir, "train_transaction.csv")
    id_path = os.path.join(raw_dir, "train_identity.csv")

    if not os.path.exists(tx_path) or not os.path.exists(id_path):
        # Attempt Kaggle download first, fallback to synthetic IEEE-CIS schema
        downloaded = download_from_kaggle(raw_dir)
        if not downloaded and (not os.path.exists(tx_path) or not os.path.exists(id_path)):
            print(f"[!] Kaggle API not configured. Generating IEEE-CIS schema fallback in '{raw_dir}'...")
            generate_mock_ieee_cis(raw_dir)

    df_tx = pd.read_csv(tx_path)
    df_id = pd.read_csv(id_path)

    # Merge on TransactionID
    df = pd.merge(df_tx, df_id, on="TransactionID", how="left")

    # Missing value handling & feature preprocessing
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(-999)

    categorical_cols = df.select_dtypes(include=["object"]).columns
    df[categorical_cols] = df[categorical_cols].fillna("UNKNOWN")

    out_path = os.path.join(processed_dir, "ieee_cis_processed.parquet")
    df.to_parquet(out_path, index=False)
    print(f"[+] Successfully exported processed dataset to {out_path} ({len(df)} records)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IEEE-CIS Fraud Detection Data Prep ETL")
    parser.add_argument("--raw-dir", default="data/raw", help="Path to raw input directory")
    parser.add_argument("--processed-dir", default="data/processed", help="Path to processed output directory")
    args = parser.parse_args()

    process_ieee_cis(args.raw_dir, args.processed_dir)
