"""
F1 Tire-Adjusted Pace Analysis
2025 British Grand Prix - Wet Weather Performance

Author: Rohan Saxena
Date: July 2025

Analysis of tire-adjusted pace performance during the 2025 British Grand Prix,
normalizing for tire compound differences and degradation to identify
genuine driver performance in changing wet conditions.
"""

import fastf1
import pandas as pd
import numpy as np
import os
from datetime import timedelta

# Configuration
CACHE_DIR = './cache'
RACE_YEAR = 2025
RACE_NAME = 'British Grand Prix'
SESSION_TYPE = 'R'

# Tire performance deltas (seconds relative to intermediate baseline)
TIRE_PERFORMANCE = {
    'INTERMEDIATE': 0.0,
    'SOFT': -8.0,
    'MEDIUM': -6.0,
    'HARD': -4.0,
    'WET': 3.0
}

# Analysis parameters
DEGRADATION_RATE = 0.1  # seconds per lap for intermediates in wet conditions
MIN_LAPS_FOR_ANALYSIS = 3
OUTLIER_THRESHOLD_MIN = 80  # minimum reasonable lap time (seconds)
OUTLIER_THRESHOLD_MAX = 200  # maximum reasonable lap time (seconds)

def setup_cache():
    """Initialize FastF1 cache directory."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    fastf1.Cache.enable_cache(CACHE_DIR)

def load_session_data():
    """Load race session data from FastF1."""
    session = fastf1.get_session(RACE_YEAR, RACE_NAME, SESSION_TYPE)
    session.load()
    return session

def analyze_race_overview(session):
    """Generate basic race statistics and tire usage."""
    laps = session.laps
    
    race_info = {
        'total_laps': len(laps),
        'event_name': session.event['EventName'],
        'location': session.event['Location'],
        'date': session.event['EventDate']
    }
    
    # Tire compound analysis
    compound_usage = laps['Compound'].value_counts()
    race_info['compound_distribution'] = {
        compound: {
            'laps': count,
            'percentage': round((count / len(laps)) * 100, 1)
        }
        for compound, count in compound_usage.items()
        if pd.notna(compound)
    }
    
    return race_info, laps

def calculate_tire_adjusted_times(laps):
    """Calculate tire-adjusted lap times for valid racing laps."""
    valid_laps = laps.dropna(subset=['LapTime', 'Compound', 'TyreLife']).copy()
    valid_laps['LapTimeSeconds'] = valid_laps['LapTime'].dt.total_seconds()
    
    adjusted_data = []
    
    for _, lap in valid_laps.iterrows():
        lap_time = lap['LapTimeSeconds']
        
        # Filter outliers (pit stops, crashes, safety car periods)
        if lap_time < OUTLIER_THRESHOLD_MIN or lap_time > OUTLIER_THRESHOLD_MAX:
            continue
        
        # Calculate adjustments
        compound_adjustment = TIRE_PERFORMANCE.get(lap['Compound'], 0)
        age_penalty = lap['TyreLife'] * DEGRADATION_RATE
        total_adjustment = compound_adjustment + age_penalty
        
        # Normalize to fresh intermediate baseline
        adjusted_time = lap_time + total_adjustment
        
        adjusted_data.append({
            'Driver': lap['Driver'],
            'LapNumber': lap['LapNumber'],
            'RawTime': lap_time,
            'AdjustedTime': adjusted_time,
            'Compound': lap['Compound'],
            'TyreAge': lap['TyreLife'],
            'TotalAdjustment': total_adjustment
        })
    
    return pd.DataFrame(adjusted_data)

def define_race_segments():
    """Define race segments based on track conditions."""
    return [
        {
            'name': 'Early Wet Chaos',
            'laps': range(1, 16),
            'description': 'Formation lap tire decisions, standing water'
        },
        {
            'name': 'Heavy Rain Period',
            'laps': range(16, 35),
            'description': 'Safety car periods, maximum spray conditions'
        },
        {
            'name': 'Drying Phase',
            'laps': range(35, 50),
            'description': 'Track evolution, strategic tire transitions'
        }
    ]

def analyze_segment_performance(adjusted_df, segments, target_drivers):
    """Analyze tire-adjusted performance by race segment."""
    results = {}
    
    for segment in segments:
        segment_data = adjusted_df[
            (adjusted_df['LapNumber'].isin(segment['laps'])) &
            (adjusted_df['Driver'].isin(target_drivers))
        ]
        
        driver_performance = []
        
        for driver in target_drivers:
            driver_laps = segment_data[segment_data['Driver'] == driver]
            
            if len(driver_laps) >= MIN_LAPS_FOR_ANALYSIS:
                performance_metrics = {
                    'driver': driver,
                    'avg_adjusted_time': driver_laps['AdjustedTime'].mean(),
                    'lap_count': len(driver_laps),
                    'consistency': driver_laps['AdjustedTime'].std(),
                    'best_lap': driver_laps['AdjustedTime'].min()
                }
                driver_performance.append(performance_metrics)
        
        # Sort by average adjusted time
        driver_performance.sort(key=lambda x: x['avg_adjusted_time'])
        results[segment['name']] = driver_performance
    
    return results

def generate_performance_summary(segment_results):
    """Generate summary of performance trends across segments."""
    driver_evolution = {}
    
    for segment_name, results in segment_results.items():
        for i, driver_data in enumerate(results):
            driver = driver_data['driver']
            position = i + 1
            
            if driver not in driver_evolution:
                driver_evolution[driver] = []
            
            driver_evolution[driver].append({
                'segment': segment_name,
                'position': position,
                'gap_to_leader': driver_data['avg_adjusted_time'] - results[0]['avg_adjusted_time']
            })
    
    return driver_evolution

def print_results(race_info, segment_results, driver_evolution):
    """Output analysis results."""
    print(f"F1 Tire-Adjusted Pace Analysis")
    print(f"Event: {race_info['event_name']}")
    print(f"Date: {race_info['date'].strftime('%B %d, %Y')}")
    print(f"Total laps analyzed: {race_info['total_laps']}")
    print()
    
    print("Tire Compound Usage:")
    for compound, data in race_info['compound_distribution'].items():
        print(f"  {compound}: {data['laps']} laps ({data['percentage']}%)")
    print()
    
    print("Segment Analysis Results:")
    for segment_name, results in segment_results.items():
        print(f"\n{segment_name}:")
        
        if results:
            fastest_time = results[0]['avg_adjusted_time']
            
            for i, perf in enumerate(results):
                gap = perf['avg_adjusted_time'] - fastest_time
                gap_str = "REF" if gap < 0.05 else f"+{gap:.2f}s"
                
                print(f"  {i+1}. {perf['driver']}: {gap_str} "
                      f"({perf['lap_count']} laps)")
    
    print(f"\nPerformance Evolution:")
    for driver, evolution in driver_evolution.items():
        positions = [seg['position'] for seg in evolution]
        avg_position = sum(positions) / len(positions)
        print(f"  {driver}: Average P{avg_position:.1f}")

def main():
    """Execute complete tire-adjusted pace analysis."""
    # Setup
    setup_cache()
    
    # Load and process data
    session = load_session_data()
    race_info, laps = analyze_race_overview(session)
    adjusted_df = calculate_tire_adjusted_times(laps)
    
    # Define analysis parameters
    segments = define_race_segments()
    target_drivers = ['NOR', 'PIA', 'VER', 'HAM', 'HUL', 'STR']
    
    # Perform analysis
    segment_results = analyze_segment_performance(adjusted_df, segments, target_drivers)
    driver_evolution = generate_performance_summary(segment_results)
    
    # Output results
    print_results(race_info, segment_results, driver_evolution)
    
    # Return data for further analysis
    return {
        'session': session,
        'race_info': race_info,
        'adjusted_data': adjusted_df,
        'segment_results': segment_results,
        'driver_evolution': driver_evolution
    }

if __name__ == "__main__":
    analysis_results = main()