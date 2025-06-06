#!/bin/bash
# Get the current time in HHMM format
current_time=$(date +%H%M)

# Convert times to HHMM format for comparison
night_start=10#0250  # 9:50 PM
night_end=10#0310    # 10:10 PM
early_start=10#0740  # 2:40 AM
early_end=10#0800    # 3:00 AM

# Check if the time is outside the ranges
if ! { [[ $current_time -ge $night_start && $current_time -le $night_end ]] || \
       [[ $current_time -ge $early_start && $current_time -le $early_end ]]; }; then
    echo "Running script..."
    /usr/share/applications/miniconda3/envs/ddomlabbackend/bin/python $(dirname $0)/main.py
else
    echo "Time is within the restricted ranges. Script will not run."
fi