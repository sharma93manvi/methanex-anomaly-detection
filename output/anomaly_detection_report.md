# Anomaly Detection Report
## Summary Statistics

### Asset 1

- **Total Records**: 8761
- **Anomalies Detected**:
  - Statistical: 5
  - Ml: 439
  - Combined: 440
- **Anomaly Percentage**: 5.02%
- **Anomaly Periods**: 5
- **Top Early Warning Sensor**: anomaly_percentile_Asset_1T___Speed_Value
- **Average Lead Time**: 14.3 hours

### Asset 2

- **Total Records**: 8761
- **Anomalies Detected**:
  - Statistical: 15
  - Ml: 439
  - Combined: 440
- **Anomaly Percentage**: 5.02%
- **Anomaly Periods**: 7
- **Top Early Warning Sensor**: anomaly_percentile_Asset_2_Pressure_&_Ratio_Value
- **Average Lead Time**: 17.7 hours

## Early Warning Sensor Rankings

### Asset 1

| sensor                                                 |   periods_detected |   avg_lead_time_hours |   min_lead_time_hours |   max_lead_time_hours |   total_flags |
|:-------------------------------------------------------|-------------------:|----------------------:|----------------------:|----------------------:|--------------:|
| anomaly_percentile_Asset_1T___Speed_Value              |                  3 |              14.3333  |                     9 |                    18 |            16 |
| anomaly_percentile_Asset_1_HP___Pressure_&_Ratio_Value |                  1 |              10       |                    10 |                    10 |             4 |
| anomaly_residual                                       |                  4 |              -0.75    |                   -10 |                    10 |             6 |
| anomaly_zscore_Asset_1_HP___Disch_Press_Value          |                  4 |              -0.75    |                   -10 |                    10 |             7 |
| anomaly_zscore_residual                                |                  4 |              -0.75    |                   -10 |                    10 |             6 |
| anomaly_envelope_Asset_1_HP___Disch_Press_Value        |                  4 |              -0.75    |                   -10 |                    10 |             7 |
| anomaly_envelope_residual                              |                  4 |              -0.75    |                   -10 |                    10 |             6 |
| anomaly_zscore_Asset_1T___Speed_Value                  |                  3 |              -2.33333 |                   -29 |                    13 |            14 |
| anomaly_envelope_Asset_1T___Speed_Value                |                  3 |              -2.33333 |                   -29 |                    13 |            14 |
| anomaly_zscore_Asset_1_HP___Pressure_&_Ratio_Value     |                  2 |              -4       |                   -14 |                     6 |             6 |

### Asset 2

| sensor                                            |   periods_detected |   avg_lead_time_hours |   min_lead_time_hours |   max_lead_time_hours |   total_flags |
|:--------------------------------------------------|-------------------:|----------------------:|----------------------:|----------------------:|--------------:|
| anomaly_percentile_Asset_2_Pressure_&_Ratio_Value |                  3 |              17.6667  |                    -2 |                    28 |            36 |
| anomaly_percentile_Asset_2___Disch_Press_Value    |                  3 |               8.33333 |                    -7 |                    26 |            38 |
| anomaly_zscore_Asset_2_Pressure_&_Ratio_Value     |                  4 |               8.25    |                   -29 |                    28 |             7 |
| anomaly_envelope_Asset_2_Pressure_&_Ratio_Value   |                  4 |               8.25    |                   -29 |                    28 |             7 |
| anomaly_score_isolation_forest                    |                  1 |               7       |                     7 |                     7 |            43 |
| anomaly_residual                                  |                  6 |               5.83333 |                   -13 |                    28 |            12 |
| anomaly_zscore_Asset_2___Disch_Press_Value        |                  6 |               5.83333 |                   -13 |                    28 |            12 |
| anomaly_envelope_Asset_2___Disch_Press_Value      |                  6 |               5.83333 |                   -13 |                    28 |            12 |
| anomaly_zscore_Asset_2T___Speed_Value             |                  4 |               3.5     |                   -13 |                    21 |             9 |
| anomaly_envelope_Asset_2T___Speed_Value           |                  4 |               3.5     |                   -13 |                    21 |             9 |

