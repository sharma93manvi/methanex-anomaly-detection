"""
Mock Stream Generator - Generates synthetic sensor data for real-time streaming
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from pathlib import Path


class MockStreamGenerator:
    """
    Generates realistic sensor data for streaming simulation
    """
    
    def __init__(self, training_data_file=None):
        """
        Initialize generator
        
        Args:
            training_data_file: Path to training data CSV to learn statistics
        """
        self.sensor_stats = {}
        self.base_timestamp = datetime.now()
        
        if training_data_file and Path(training_data_file).exists():
            self._learn_from_training_data(training_data_file)
        else:
            self._initialize_default_stats()
    
    def _learn_from_training_data(self, filepath):
        """Learn statistics from training data"""
        try:
            df = pd.read_csv(filepath, nrows=1000)  # Sample for speed
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            for col in numeric_cols:
                if col != 'Timestamp':
                    self.sensor_stats[col] = {
                        'mean': float(df[col].mean()),
                        'std': float(df[col].std()),
                        'min': float(df[col].min()),
                        'max': float(df[col].max())
                    }
            print(f"✓ Learned statistics for {len(self.sensor_stats)} sensors")
        except Exception as e:
            print(f"⚠ Could not learn from training data: {e}")
            self._initialize_default_stats()
    
    def _initialize_default_stats(self):
        """Initialize with default statistics for all sensors"""
        self.sensor_stats = {
            'Asset 1 HP - Disch Press Value': {'mean': 9850, 'std': 150, 'min': 9500, 'max': 10200},
            'Asset 1 HP - Pressure & Ratio Value': {'mean': 2.78, 'std': 0.05, 'min': 2.6, 'max': 2.9},
            'Asset 1 HP - Suct Press Value': {'mean': 3790, 'std': 50, 'min': 3700, 'max': 3900},
            'Asset 1T Condensate flow Value': {'mean': 23.8, 'std': 1, 'min': 22, 'max': 26},
            'Asset 1 LP - Pressure & Ratio Value': {'mean': 2.76, 'std': 0.05, 'min': 2.6, 'max': 2.9},
            'Asset 1T - Speed Value': {'mean': 10295, 'std': 50, 'min': 10100, 'max': 10400},
            'Asset 1T Extraction flow Value': {'mean': 203, 'std': 5, 'min': 195, 'max': 210},
            'Asset 1T Steam Inlet flow Value': {'mean': 231, 'std': 5, 'min': 220, 'max': 240},
            'Asset 2 Pressure & Ratio Value': {'mean': 1.19, 'std': 0.02, 'min': 1.15, 'max': 1.25},
            'Asset 2T - Speed Value': {'mean': 9216, 'std': 30, 'min': 9150, 'max': 9280},
            'Asset 2T Steam Inlet flow Value': {'mean': 25.5, 'std': 1, 'min': 23, 'max': 28},
            'Asset 1T LP - Disch Press Value': {'mean': 3900, 'std': 100, 'min': 3700, 'max': 4100},
            'Asset 1T LP - Suct Press Value': {'mean': 1557, 'std': 50, 'min': 1500, 'max': 1650},
            'Asset 2 - Disch Press Value': {'mean': 10400, 'std': 200, 'min': 10000, 'max': 10800},
            'Asset 2 - Suct Press Value': {'mean': 9629, 'std': 150, 'min': 9400, 'max': 9800},
            'target Value': {'mean': -63, 'std': 2, 'min': -70, 'max': -55},
            'Ambient Temperature Value': {'mean': 0.5, 'std': 2, 'min': -5, 'max': 5}
        }
    
    def generate_hourly_data(self, hours=24, anomaly_probability=0.05, start_time=None, demo_mode=False):
        """
        Generate hourly sensor data
        
        Args:
            hours: Number of hours to generate
            anomaly_probability: Probability of anomaly in each hour
            start_time: Start timestamp (default: now)
            demo_mode: If True, creates a progression: normal -> early warnings -> anomaly
            
        Returns:
            DataFrame with generated data
        """
        if start_time is None:
            start_time = self.base_timestamp
        
        timestamps = [start_time + timedelta(hours=i) for i in range(hours)]
        
        data = {'Timestamp': timestamps}
        
        if demo_mode:
            # Demo mode: Create progression
            # First 30%: Normal operation
            # Next 40%: Early warning signs (gradual deviations)
            # Last 30%: Anomaly period
            normal_end = int(hours * 0.3)
            warning_start = normal_end
            warning_end = int(hours * 0.7)
            anomaly_start = warning_end
        else:
            # Random anomalies
            anomaly_hours = np.random.random(hours) < anomaly_probability
        
        for sensor, stats in self.sensor_stats.items():
            values = []
            for i in range(hours):
                if demo_mode:
                    if i < normal_end:
                        # Normal operation
                        value = np.random.normal(stats['mean'], stats['std'])
                        value = np.clip(value, stats['min'], stats['max'])
                    elif i < warning_end:
                        # Early warning phase - gradual deviation
                        progress = (i - warning_start) / (warning_end - warning_start)
                        deviation_multiplier = 1.0 + progress * 2.0  # 1.0 to 3.0 std devs
                        value = stats['mean'] + np.random.uniform(deviation_multiplier - 0.3, deviation_multiplier + 0.3) * stats['std']
                        value = np.clip(value, stats['min'] * 0.9, stats['max'] * 1.1)
                    else:
                        # Anomaly phase
                        if np.random.random() < 0.5:
                            value = stats['mean'] + np.random.uniform(3.5, 5.0) * stats['std']
                        else:
                            value = stats['mean'] - np.random.uniform(3.5, 5.0) * stats['std']
                        value = np.clip(value, stats['min'] * 0.7, stats['max'] * 1.3)
                else:
                    # Random anomaly mode
                    is_anomaly = anomaly_hours[i]
                    if is_anomaly:
                        # Generate anomalous value (extreme deviation)
                        if np.random.random() < 0.5:
                            # High anomaly
                            value = stats['mean'] + np.random.uniform(3, 5) * stats['std']
                        else:
                            # Low anomaly
                            value = stats['mean'] - np.random.uniform(3, 5) * stats['std']
                        value = np.clip(value, stats['min'] * 0.8, stats['max'] * 1.2)
                    else:
                        # Generate normal value
                        value = np.random.normal(stats['mean'], stats['std'])
                        value = np.clip(value, stats['min'], stats['max'])
                
                values.append(value)
            
            data[sensor] = values
        
        df = pd.DataFrame(data)
        return df
    
    def stream_data(self, callback, interval_seconds=1.0, total_hours=24, anomaly_probability=0.05):
        """
        Stream data in real-time
        
        Args:
            callback: Function to call with each data point (df_row)
            interval_seconds: Time between data points
            total_hours: Total hours to stream
            anomaly_probability: Probability of anomaly
        """
        df = self.generate_hourly_data(total_hours, anomaly_probability)
        
        for idx, row in df.iterrows():
            callback(row)
            time.sleep(interval_seconds)
    
    def generate_single_record(self, timestamp=None, is_anomaly=False):
        """
        Generate a single record
        
        Args:
            timestamp: Timestamp for record (default: now)
            is_anomaly: Whether to generate anomalous values
            
        Returns:
            Series with sensor data
        """
        if timestamp is None:
            timestamp = self.base_timestamp
        
        data = {'Timestamp': timestamp}
        
        for sensor, stats in self.sensor_stats.items():
            if is_anomaly:
                # Anomalous value
                if np.random.random() < 0.5:
                    value = stats['mean'] + np.random.uniform(3, 5) * stats['std']
                else:
                    value = stats['mean'] - np.random.uniform(3, 5) * stats['std']
                value = np.clip(value, stats['min'] * 0.8, stats['max'] * 1.2)
            else:
                # Normal value
                value = np.random.normal(stats['mean'], stats['std'])
                value = np.clip(value, stats['min'], stats['max'])
            
            data[sensor] = value
        
        return pd.Series(data)

