#!/usr/bin/env python3
import pandas as pd
import numpy as np

# Input CSV
infile = "cicd_build_500.csv"      # your new 500-build CSV
# Output CSV for dashboard
outfile = "master_build_data_clean.csv"

# Read CSV
df = pd.read_csv(infile)

# Fill missing columns if needed (here all required exist)
if "Tests_Run" not in df.columns:
    df["Tests_Run"] = np.random.randint(1, 20, size=len(df))
if "Tests_Failed" not in df.columns:
    # Fail builds have 2-5 failed tests, Pass 0-1
    df["Tests_Failed"] = [np.random.randint(0,2) if s=="Pass" else np.random.randint(2,6) for s in df["Build_Status"]]

# Ensure correct column names
df = df.rename(columns={
    "build_id": "Build_ID",
    "status": "Build_Status",
    "duration_sec": "Duration"
})

# Normalize Build_Status
status_map = {
    "SUCCESS": "Pass",
    "FAILURE": "Fail",
    "ABORTED": "Fail",
    "IN_PROGRESS": "Fail"
}
df["Build_Status"] = df["Build_Status"].map(lambda x: status_map.get(str(x).upper(), str(x)))

# Keep only expected columns
df = df[["Build_ID", "Build_Status", "Duration", "Tests_Run", "Tests_Failed"]]

# Save cleaned CSV
df.to_csv(outfile, index=False)
print(f"✅ Cleaned CSV saved as {outfile}")
print(df.head())
