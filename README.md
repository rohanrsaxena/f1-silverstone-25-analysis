# F1 Tire-Adjusted Pace Analysis

Analysis of tire-adjusted pace performance during the 2025 British Grand Prix, normalizing for tire compound differences and degradation to identify genuine driver performance in changing wet conditions.

## Overview

Traditional F1 lap time analysis can be misleading when drivers are using different tire compounds or managing varying levels of tire degradation. This analysis normalizes performance by adjusting for tire compound deltas and age-related degradation to reveal true driver pace.

## Key Findings

- **Lance Stroll** demonstrated exceptional pace in early wet conditions when tire-adjusted
- **Oscar Piastri** dominated during the heaviest rain period with safety car deployments
- **Lewis Hamilton** excelled in the crucial drying transition phase
- Equipment normalization revealed performance patterns invisible in traditional analysis

## Methodology

### Data Source
- **FastF1 Python library** for official F1 telemetry data
- 2025 British Grand Prix race session
- 734 valid racing laps analyzed

### Tire Adjustments
- **Compound normalization**: Adjusted to intermediate tire baseline
- **Degradation modeling**: 0.1 seconds per lap penalty for tire age
- **Outlier filtering**: Removed pit stops, crashes, and safety car periods

### Race Segmentation
1. **Early Wet Chaos** (Laps 1-15): Formation lap decisions, standing water
2. **Heavy Rain Period** (Laps 16-34): Safety cars, maximum spray conditions  
3. **Drying Phase** (Laps 35-49): Track evolution, strategic transitions

## Installation

```bash
pip install fastf1 pandas numpy matplotlib
```

## Usage

```python
python f1_tire_analysis.py
```

The script will:
1. Download race data using FastF1
2. Apply tire compound and degradation adjustments
3. Segment the race by track conditions
4. Output performance analysis by segment

## Technical Details

### Tire Performance Deltas (relative to intermediate baseline)
- **Intermediate**: 0.0s (baseline)
- **Soft**: -8.0s (faster in dry)
- **Medium**: -6.0s (faster in dry)
- **Hard**: -4.0s (faster in dry)
- **Wet**: +3.0s (slower than intermediate)

### Analysis Parameters
- **Degradation rate**: 0.1s per lap for intermediates in wet conditions
- **Minimum laps**: 3 laps required for segment analysis
- **Outlier thresholds**: 80-200 seconds for valid lap times

## Results

Race conditions: 73.6% of laps run on intermediate tires, with rainfall detected throughout and humidity reaching 88%.

### Segment Leaders (Tire-Adjusted)
- **Early Wet Chaos**: Lance Stroll
- **Heavy Rain Period**: Oscar Piastri  
- **Drying Phase**: Lewis Hamilton

## Data Structure

The analysis outputs structured data including:
- Race overview and tire usage statistics
- Tire-adjusted lap times with compound and age corrections
- Segment-by-segment performance rankings
- Driver performance evolution across conditions

## Files

- `f1_tire_analysis.py`: Main analysis script
- `README.md`: Documentation
- `cache/`: FastF1 data cache directory (created automatically)

## Requirements

- Python 3.8+
- FastF1 3.6.0+
- pandas
- numpy
- matplotlib (optional, for visualizations)

## Author

Rohan Saxena  
July 2025

Analysis methodology developed for technical deep-dive into F1 performance metrics under variable conditions.
