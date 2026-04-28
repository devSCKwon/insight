import pandas as pd
import numpy as np
import logging

# Setup basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def calculate_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the composite score for each record based on multiple criteria.

    Args:
        df: DataFrame containing the raw data.

    Returns:
        DataFrame with the added 'composite_score' column.
    """
    logging.info("Starting score calculation process.")
    
    # --- 1. Feature Engineering and Normalization ---
    
    # Calculate the score for 'score_A' (Assuming A is a numerical score)
    # We use .fillna(0) to handle potential NaN values gracefully before scaling.
    score_A = df['score_A'].fillna(0)
    
    # Calculate the score for 'score_B' (Assuming B is a numerical score)
    score_B = df['score_B'].fillna(0)
    
    # Calculate the score for 'score_C' (Assuming C is a numerical score)
    score_C = df['score_C'].fillna(0)

    # --- 2. Normalization (Min-Max Scaling) ---
    # Scaling ensures all features contribute equally to the final score.
    
    def min_max_normalize(series: pd.Series) -> pd.Series:
        """Applies Min-Max scaling: (X - Min) / (Max - Min)"""
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            logging.warning(f"Feature {series.name} has constant values. Setting normalized score to 1.0.")
            return pd.Series(1.0, index=series.index)
        return (series - min_val) / (max_val - min_val)

    logging.info("Normalizing features...")
    norm_A = min_max_normalize(score_A)
    norm_B = min_max_normalize(score_B)
    norm_C = min_max_normalize(score_C)

    # --- 3. Composite Score Calculation ---
    # The weights (0.4, 0.3, 0.3) are applied here.
    logging.info("Calculating composite score using weights (0.4, 0.3, 0.3)...")
    
    # Composite Score = (Weight_A * Norm_A) + (Weight_B * Norm_B) + (Weight_C * Norm_C)
    composite_score = (0.4 * norm_A) + (0.3 * norm_B) + (0.3 * norm_C)
    
    # --- 4. Final Output ---
    df['composite_score'] = composite_score
    logging.info("Score calculation completed successfully.")
    
    return df

def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Main function to process the input DataFrame and calculate the final score.
    """
    logging.info("--- Starting Data Processing Pipeline ---")
    
    # Check for required columns
    required_cols = ['score_A', 'score_B', 'score_C']
    if not all(col in df.columns for col in required_cols):
        logging.error(f"Input DataFrame must contain the following columns: {required_cols}")
        return df
    
    # Calculate the score
    scored_df = calculate_score(df.copy())
    
    logging.info("--- Data Processing Pipeline Finished ---")
    return scored_df

# ======================================================================================
# Example Usage and Testing
# ========================================================================================

if __name__ == "__main__":
    # 1. Create a sample DataFrame simulating real-world data
    data = {
        'user_id': range(1, 11),
        'score_A': [85, 92, 78, 65, 95, 88, 70, 99, 80, 75],
        'score_B': [70, 80, 60, 50, 90, 75, 65, 99, 72, 68],
        'score_C': [90, 85, 75, 60, 99, 82, 70, 95, 78, 72]
    }
    df_input = pd.DataFrame(data)
    
    print("="*50)
    print("ORIGINAL INPUT DATA:")
    print(df_input)
    print("="*50)

    # 2. Process the data
    df_output = process_data(df_input)

    # 3. Display Results
    print("\n" + "="*50)
    print("FINAL OUTPUT DATA WITH COMPOSITE SCORE:")
    print(df_output)
    print("="*50)
    
    # Test case with missing values (NaN)
    print("\n--- Testing with Missing Values (NaN) ---")
    data_nan = {
        'user_id': [11, 12, 13],
        'score_A': [80, np.nan, 70],
        'score_B': [70, 80, np.nan],
        'score_C': [90, 85, 75]
    }
    df_nan = pd.DataFrame(data_nan)
    df_output_nan = process_data(df_nan)
    print("\nOutput with NaN handling:")
    print(df_output_nan)