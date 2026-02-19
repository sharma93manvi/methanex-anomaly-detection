"""
Training Script - Trains models and saves them for inference
Also generates test files
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.main import main
from src.model_manager import ModelManager
from utils.mock_batch_generator import MockBatchGenerator

def train_and_save_models():
    """
    Train models using the main pipeline and save them
    """
    print("="*60)
    print("MODEL TRAINING AND SAVING")
    print("="*60)
    
    # Training data file
    data_file = "Updated Challenge3 Data.csv"
    
    print(f"\nTraining data file: {data_file}")
    print(f"Full path: {Path(data_file).absolute()}")
    
    # Run main pipeline
    print("\n" + "="*60)
    print("Running main pipeline to process data and train models...")
    print("="*60)
    
    df_asset1_processed, df_asset2_processed, summary_stats = main()
    
    # Save models
    print("\n" + "="*60)
    print("Saving trained models...")
    print("="*60)
    
    model_manager = ModelManager()
    
    # Get early detection results (we need to run early detection again or get from main)
    from src.early_detection import analyze_early_detection
    
    early_detection_asset1 = analyze_early_detection(df_asset1_processed, asset='Asset 1')
    early_detection_asset2 = analyze_early_detection(df_asset2_processed, asset='Asset 2')
    
    # Save models
    model_manager.save_models(
        df_asset1_processed,
        df_asset2_processed,
        early_detection_asset1,
        early_detection_asset2
    )
    
    print("\n" + "="*60)
    print("MODEL TRAINING COMPLETE")
    print("="*60)
    print(f"\nModels saved to: {model_manager.model_dir.absolute()}")
    print("\nSummary:")
    print(f"  Asset 1: {len(df_asset1_processed)} records processed")
    print(f"  Asset 2: {len(df_asset2_processed)} records processed")
    
    return model_manager, summary_stats

def generate_test_files():
    """
    Generate test files for batch processing
    """
    print("\n" + "="*60)
    print("GENERATING TEST FILES")
    print("="*60)
    
    training_file = "Updated Challenge3 Data.csv"
    
    if not Path(training_file).exists():
        print(f"⚠ Warning: Training file {training_file} not found.")
        print("  Test files will be generated with default statistics.")
        generator = MockBatchGenerator()
    else:
        print(f"Using training file: {training_file}")
        generator = MockBatchGenerator(training_file)
    
    # Generate all test files
    generator.generate_all_test_files(duration_days=30)
    
    print("\n" + "="*60)
    print("TEST FILE GENERATION COMPLETE")
    print("="*60)

if __name__ == "__main__":
    try:
        # Step 1: Train and save models
        model_manager, summary_stats = train_and_save_models()
        
        # Step 2: Generate test files
        generate_test_files()
        
        print("\n" + "="*60)
        print("ALL TASKS COMPLETE!")
        print("="*60)
        print("\nNext steps:")
        print("  1. Models are ready for inference in the Streamlit app")
        print("  2. Test files are available in test_data/ directory")
        print("  3. Run 'streamlit run app.py' to start the application")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

