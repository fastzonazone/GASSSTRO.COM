#!/bin/bash
# Cleanup script for temporary files older than 24 hours

TEMP_DIR="exports/temp"
MAX_AGE_HOURS=24

echo "Cleaning temp files older than ${MAX_AGE_HOURS} hours in ${TEMP_DIR}..."

find "${TEMP_DIR}" -type f -mmin +$((MAX_AGE_HOURS * 60)) -delete

echo "Cleanup complete."
