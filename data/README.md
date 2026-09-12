# Data Pipeline & Acquisition Guide

AegisFlow uses two primary data sources for model training and evaluation:
1. **IEEE-CIS Fraud Detection Dataset (Kaggle)** — Used for supervised XGBoost / LightGBM baseline training.
2. **Synthetic Transaction Stream (AMLSim / SAML-D style)** — Generated internally by `txgen` with labeled laundering typologies (*smurfing*, *layering*, *round-tripping*).

---

## IEEE-CIS Acquisition & Processing

### Option 1: Automatic Download via Kaggle CLI (Recommended)
If you have configured your Kaggle API key (`~/.kaggle/kaggle.json`):
```bash
python ml/src/aegis_ml/training/prepare_ieee.py
```
`prepare_ieee.py` will automatically invoke the Kaggle CLI (`kaggle competitions download -c ieee-fraud-detection`), extract `train_transaction.csv` and `train_identity.csv` into `data/raw/`, preprocess features, and output `data/processed/ieee_cis_processed.parquet`.

### Option 2: Manual Download
1. Download `train_transaction.csv` and `train_identity.csv` from [Kaggle IEEE-CIS Competition](https://www.kaggle.com/c/ieee-fraud-detection/data).
2. Place both CSV files directly into `data/raw/`.
3. Run the ETL pipeline:
```bash
python ml/src/aegis_ml/training/prepare_ieee.py
```

### Option 3: Automated Synthetic Fallback (Zero Setup)
If Kaggle CLI is not configured and `data/raw/` is empty, `prepare_ieee.py` automatically generates a matching IEEE-CIS schema fallback so the entire pipeline, DVC stages, and ML model training run without errors.

---

## DVC Pipeline Integration

To run dataset processing via DVC:
```bash
dvc repro
```
This executes the `prepare_data` stage defined in `dvc.yaml` using parameters from `params.yaml`.
