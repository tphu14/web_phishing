"""
Script chuẩn bị dữ liệu: extract features từ CSV
Usage: python scripts/prepare_data.py --input data/raw/dataset.csv --output data/processed/features.csv
"""

import argparse
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.features import extract_features

def prepare_dataset(input_file, output_file, sample_size=None):
    """
    Extract features từ dataset
    
    Parameters:
    input_file: Path to raw CSV (must have 'url' and 'type' columns)
    output_file: Path to save processed CSV
    sample_size: Number of samples (None = all)
    """
    print(f"\n{'='*70}")
    print("PHISHING DETECTION - DATA PREPARATION")
    print(f"{'='*70}\n")
    
    # Read CSV
    print(f"📂 Reading: {input_file}")
    df = pd.read_csv(input_file)
    
    print(f"📊 Total URLs: {len(df):,}")
    
    # Sample if needed
    if sample_size and sample_size < len(df):
        print(f"⚡ Sampling {sample_size:,} URLs...")
        df = df.sample(n=sample_size, random_state=42)
    
    # Detect columns
    url_col = 'url' if 'url' in df.columns else 'URL'
    type_col = 'type' if 'type' in df.columns else 'Type'
    
    print(f"\n⏳ Extracting features...")
    
    features_list = []
    
    for idx, url in enumerate(df[url_col]):
        if idx % 500 == 0 and idx > 0:
            print(f"   Progress: {idx:,}/{len(df):,} ({idx/len(df)*100:.1f}%)")
        
        features = extract_features(str(url))
        features['url'] = url
        features['class'] = df[type_col].iloc[idx]
        features_list.append(features)
    
    # Create DataFrame
    result_df = pd.DataFrame(features_list)
    
    # Convert class labels
    result_df['class'] = result_df['class'].map({
        'phishing': -1,
        'legitimate': 1
    })
    
    # Reorder columns
    feature_cols = [col for col in result_df.columns if col not in ['url', 'class']]
    result_df = result_df[['url', 'class'] + feature_cols]
    
    # Save
    print(f"\n💾 Saving to: {output_file}")
    result_df.to_csv(output_file, index=False)
    
    print(f"\n{'='*70}")
    print("✅ COMPLETED!")
    print(f"{'='*70}\n")
    
    print(f"📊 Output Info:")
    print(f"   - Total samples: {len(result_df):,}")
    print(f"   - Total features: {len(feature_cols)}")
    print(f"   - Legitimate: {(result_df['class'] == 1).sum():,}")
    print(f"   - Phishing: {(result_df['class'] == -1).sum():,}")
    
    return result_df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Prepare phishing detection dataset')
    parser.add_argument('--input', required=True, help='Input CSV file')
    parser.add_argument('--output', required=True, help='Output CSV file')
    parser.add_argument('--sample', type=int, default=None, help='Sample size (optional)')
    
    args = parser.parse_args()
    
    prepare_dataset(args.input, args.output, args.sample)
