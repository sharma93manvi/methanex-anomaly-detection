"""
Mock Batch Generator - Generates CSV test files for batch processing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.mock_stream_generator import MockStreamGenerator


class MockBatchGenerator:
    """
    Generates complete CSV files for batch processing testing
    """
    
    def __init__(self, training_data_file=None):
        """
        Initialize generator
        
        Args:
            training_data_file: Path to training data CSV to learn statistics
        """
        self.stream_gen = MockStreamGenerator(training_data_file)
    
    def generate_test_file(self, scenario='normal', duration_days=30, output_path=None):
        """
        Generate a test file for a specific scenario
        
        Args:
            scenario: 'normal', 'single_anomaly', 'multiple_anomalies', 
                     'early_warning', 'low_severity', 'medium_severity', 
                     'high_severity', 'critical_severity', 
                     'root_cause_pressure', 'root_cause_speed'
            duration_days: Number of days of data to generate
            output_path: Output file path (auto-generated if None)
            
        Returns:
            Path to generated file
        """
        hours = duration_days * 24
        start_time = datetime(2025, 1, 1, 0, 0, 0)
        
        if output_path is None:
            scenario_names = {
                'normal': 'normal_operation',
                'single_anomaly': 'single_anomaly',
                'multiple_anomalies': 'multiple_anomalies',
                'early_warning': 'early_warning_scenario',
                'low_severity': 'low_severity_anomaly',
                'medium_severity': 'medium_severity_anomaly',
                'high_severity': 'high_severity_anomaly',
                'critical_severity': 'critical_severity_anomaly',
                'root_cause_pressure': 'root_cause_pressure',
                'root_cause_speed': 'root_cause_speed'
            }
            filename = f"{scenario_names.get(scenario, scenario)}_{duration_days}days.csv"
            output_dir = Path("test_data")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / filename
        
        print(f"\nGenerating {scenario} scenario ({duration_days} days)...")
        
        # Generate base data
        df = self.stream_gen.generate_hourly_data(hours=hours, anomaly_probability=0.0, start_time=start_time)
        
        # Apply scenario-specific modifications
        if scenario == 'normal':
            # Ensure truly normal data - reduce variance slightly to minimize ML false positives
            # Keep data very close to mean values
            for sensor, stats in self.stream_gen.sensor_stats.items():
                if sensor in df.columns:
                    # Generate values very close to mean (reduced std)
                    df[sensor] = np.random.normal(stats['mean'], stats['std'] * 0.5, len(df))
                    df[sensor] = np.clip(df[sensor], stats['min'], stats['max'])
            pass
        
        elif scenario == 'single_anomaly':
            # Add one anomaly period (6-12 hours) in the middle
            anomaly_start = hours // 2
            anomaly_duration = np.random.randint(6, 13)
            df = self._inject_anomaly_period(df, anomaly_start, anomaly_duration, severity='medium')
        
        elif scenario == 'multiple_anomalies':
            # Add multiple anomaly periods
            num_anomalies = np.random.randint(3, 6)
            for _ in range(num_anomalies):
                start = np.random.randint(100, hours - 100)
                duration = np.random.randint(4, 10)
                severity = np.random.choice(['low', 'medium', 'high'])
                df = self._inject_anomaly_period(df, start, duration, severity=severity)
        
        elif scenario == 'early_warning':
            # Add early warning indicators before main anomaly
            anomaly_start = hours // 2
            # Early indicators 18-24 hours before
            early_start = anomaly_start - np.random.randint(18, 25)
            df = self._inject_early_warning(df, early_start, anomaly_start)
            df = self._inject_anomaly_period(df, anomaly_start, 8, severity='high')
        
        elif scenario == 'low_severity':
            anomaly_start = hours // 2
            df = self._inject_anomaly_period(df, anomaly_start, 6, severity='low')
        
        elif scenario == 'medium_severity':
            anomaly_start = hours // 2
            df = self._inject_anomaly_period(df, anomaly_start, 8, severity='medium')
        
        elif scenario == 'high_severity':
            anomaly_start = hours // 2
            df = self._inject_anomaly_period(df, anomaly_start, 10, severity='high')
        
        elif scenario == 'critical_severity':
            anomaly_start = hours // 2
            df = self._inject_anomaly_period(df, anomaly_start, 12, severity='critical')
        
        elif scenario == 'root_cause_pressure':
            # Pressure sensor is the root cause
            anomaly_start = hours // 2
            df = self._inject_anomaly_period(df, anomaly_start, 8, severity='high', 
                                            root_cause_sensor='Asset 1 HP - Disch Press Value')
        
        elif scenario == 'root_cause_speed':
            # Speed sensor is the root cause
            anomaly_start = hours // 2
            df = self._inject_anomaly_period(df, anomaly_start, 8, severity='high',
                                            root_cause_sensor='Asset 1T - Speed Value')
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        print(f"✓ Saved: {output_path}")
        
        return output_path
    
    def _inject_anomaly_period(self, df, start_idx, duration, severity='medium', root_cause_sensor=None):
        """Inject an anomaly period into the dataframe"""
        df = df.copy()
        end_idx = min(start_idx + duration, len(df))
        
        # Severity multipliers
        severity_multipliers = {
            'low': 2.0,
            'medium': 3.0,
            'high': 4.0,
            'critical': 5.5
        }
        multiplier = severity_multipliers.get(severity, 3.0)
        
        for idx in range(start_idx, end_idx):
            if idx >= len(df):
                break
            
            for sensor, stats in self.stream_gen.sensor_stats.items():
                # If root cause sensor, make it more extreme
                if root_cause_sensor and sensor == root_cause_sensor:
                    deviation_multiplier = multiplier * 1.5
                else:
                    deviation_multiplier = multiplier
                
                # Generate anomalous value
                if np.random.random() < 0.5:
                    value = stats['mean'] + np.random.uniform(deviation_multiplier, deviation_multiplier + 1) * stats['std']
                else:
                    value = stats['mean'] - np.random.uniform(deviation_multiplier, deviation_multiplier + 1) * stats['std']
                
                value = np.clip(value, stats['min'] * 0.7, stats['max'] * 1.3)
                df.at[idx, sensor] = value
        
        return df
    
    def _inject_early_warning(self, df, start_idx, anomaly_start):
        """Inject early warning indicators before anomaly"""
        df = df.copy()
        
        # Gradually increase deviations in key sensors
        key_sensors = [
            'Asset 1T - Speed Value',
            'Asset 1 HP - Disch Press Value',
            'Asset 1 HP - Pressure & Ratio Value'
        ]
        
        for i, idx in enumerate(range(start_idx, anomaly_start)):
            if idx >= len(df):
                break
            
            # Progressive deviation (increases as we approach anomaly)
            progress = (i + 1) / (anomaly_start - start_idx)
            deviation = 1.5 + progress * 1.5  # 1.5 to 3.0 std deviations
            
            for sensor in key_sensors:
                if sensor in df.columns and sensor in self.stream_gen.sensor_stats:
                    stats = self.stream_gen.sensor_stats[sensor]
                    value = stats['mean'] + np.random.uniform(deviation - 0.3, deviation + 0.3) * stats['std']
                    value = np.clip(value, stats['min'] * 0.9, stats['max'] * 1.1)
                    df.at[idx, sensor] = value
        
        return df
    
    def generate_all_test_files(self, output_dir='test_data', duration_days=30):
        """
        Generate all test files
        
        Args:
            output_dir: Output directory
            duration_days: Days of data per file
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        scenarios = [
            'normal',
            'single_anomaly',
            'multiple_anomalies',
            'early_warning',
            'low_severity',
            'medium_severity',
            'high_severity',
            'critical_severity',
            'root_cause_pressure',
            'root_cause_speed'
        ]
        
        print(f"\n=== Generating {len(scenarios)} test files ===")
        
        for scenario in scenarios:
            self.generate_test_file(scenario, duration_days, 
                                   output_path / f"{scenario}_{duration_days}days.csv")
        
        # Also generate a mixed scenarios file (90 days)
        print("\nGenerating mixed scenarios file (90 days)...")
        hours = 90 * 24
        start_time = datetime(2025, 1, 1, 0, 0, 0)
        df = self.stream_gen.generate_hourly_data(hours=hours, anomaly_probability=0.0, start_time=start_time)
        
        # Add various anomalies throughout
        anomaly_periods = [
            (100, 6, 'low'),
            (500, 8, 'medium'),
            (1000, 10, 'high'),
            (1500, 12, 'critical'),
            (2000, 6, 'low'),
        ]
        
        for start, duration, severity in anomaly_periods:
            df = self._inject_anomaly_period(df, start, duration, severity=severity)
        
        output_file = output_path / f"mixed_scenarios_90days.csv"
        df.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}")
        
        print(f"\n✓ Generated all test files in {output_dir}/")

