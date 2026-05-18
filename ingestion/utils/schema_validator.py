def validate_pos_schema(df, required_columns):
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"POS CSV missing columns: {missing}")
