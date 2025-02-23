import subprocess
import pandas as pd
from datetime import datetime
import numpy as np
import argparse
import io


# Function to diagnose problematic lines
def diagnose_bad_lines(file_path):
    with open(file_path, 'r') as file:
        for i, line in enumerate(file):
            try:
                pd.read_csv(io.StringIO(line), delimiter=';')
            except pd.errors.ParserError:
                print(f"Skipping line {i + 1}: {line.strip()}")

# Function to convert time strings to seconds
def convert_time_to_seconds(time_str):
    if '-' in time_str:
        d, hms = time_str.split('-')
        h, m, s = map(int, hms.split(':'))
        return int(d) * 86400 + h * 3600 + m * 60 + s
    else:
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s

# Remove this function as we no longer need to parse JobID
# def parse_job_id(job_id):
#     try:
#         return int(job_id.split('_')[0])
#     except (ValueError, AttributeError):
#         return None

# Function to convert date/time strings to datetime objects
def convert_to_datetime(date_str):
    return pd.to_datetime(date_str, format='%Y-%m-%dT%H:%M:%S')

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run get_stats.sh and analyze the output CSV file.')
parser.add_argument('--input', type=str, help='Path to an existing CSV file to analyze.')
parser.add_argument('refresh', nargs='?', default=False, help='Run get_stats.sh to get a new CSV file.')
args = parser.parse_args()

if args.refresh:
    # Run the bash script and save the output to a date-time stamped CSV file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"stats_{timestamp}.csv"
    subprocess.run(["bash", "get_stats.sh", output_file])
elif args.input:
    # Use the provided input file
    output_file = args.input
else:
    print("Error: You must provide either the 'refresh' argument or the '--input' argument.")
    exit(1)

# Diagnose problematic lines
diagnose_bad_lines(output_file)

# Specify data types for each column
dtypes = {
    'JobID': str,
    'User': str,
    'Account': str,
    'JobName': str,
    'State': str,
    'Elapsed': str,
    'CPUTime': str,
    'Nodelist': str,
    'Submit': str,
    'End': str
}

# Load the CSV file into a pandas DataFrame with semicolon delimiter and specified data types
df = pd.read_csv(output_file, delimiter=';', dtype=dtypes, on_bad_lines='warn')

# Clean and convert columns
df['Elapsed'] = df['Elapsed'].apply(convert_time_to_seconds)
df['CPUTime'] = df['CPUTime'].apply(convert_time_to_seconds)
df['Submit'] = df['Submit'].apply(convert_to_datetime)
df['End'] = df['End'].apply(convert_to_datetime)

# Handle NodeList column which might contain comma-separated multiple entries
df['NodeList'] = df['NodeList'].str.split(',')

# Analyze the data
total_jobs = len(df)
completed_jobs = len(df[df['State'] == 'COMPLETED'])
failed_jobs = len(df[df['State'] == 'FAILED'])
unique_users = df['User'].nunique()

runtime = df['Elapsed']
jobs_per_user = df['User'].value_counts()

# Calculate statistics
runtime_stats = {
    'avg_runtime': runtime.mean(),
    'median_runtime': runtime.median(),
    'max_runtime': runtime.max()
}

jobs_per_user_stats = {
    'avg_jobs_per_user': jobs_per_user.mean(),
    'median_jobs_per_user': jobs_per_user.median(),
    'max_jobs_per_user': jobs_per_user.max()
}

# Create a date-stamped output report
report_file = f"report_{timestamp}.txt"
with open(report_file, 'w') as file:
    file.write(f"Total jobs: {total_jobs}\n")
    file.write(f"Completed jobs: {completed_jobs}\n")
    file.write(f"Failed jobs: {failed_jobs}\n")
    file.write(f"Unique users: {unique_users}\n")
    file.write("Runtime statistics:\n")
    file.write(f"  Average runtime: {runtime_stats['avg_runtime']}\n")
    file.write(f"  Median runtime: {runtime_stats['median_runtime']}\n")
    file.write(f"  Max runtime: {runtime_stats['max_runtime']}\n")
    file.write("Jobs per user statistics:\n")
    file.write(f"  Average jobs per user: {jobs_per_user_stats['avg_jobs_per_user']}\n")
    file.write(f"  Median jobs per user: {jobs_per_user_stats['median_jobs_per_user']}\n")
    file.write(f"  Max jobs per user: {jobs_per_user_stats['max_jobs_per_user']}\n")

# Print the results to the console
print(f"Total jobs: {total_jobs}")
print(f"Completed jobs: {completed_jobs}")
print(f"Failed jobs: {failed_jobs}")
print(f"Unique users: {unique_users}")
print("Runtime statistics:", runtime_stats)
print("Jobs per user statistics:", jobs_per_user_stats)
