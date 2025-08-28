import pandas as pd
import numpy as np

np.random.seed(42)

num_builds = 500
pass_count = int(num_builds * 0.6)
fail_count = num_builds - pass_count

# Build IDs
build_ids = np.arange(1, num_builds + 1)

# Build Status
statuses = ["Pass"] * pass_count + ["Fail"] * fail_count
np.random.shuffle(statuses)

# Duration: Pass builds slightly faster, Fail builds variable
duration = [np.random.randint(50, 300) if s=="Pass" else np.random.randint(100, 600) for s in statuses]

# Tests Run: 1-20
tests_run = np.random.randint(1, 21, size=num_builds)

# Tests Failed: Pass: 0-1, Fail: 2-5
tests_failed = [np.random.randint(0,2) if s=="Pass" else np.random.randint(2,6) for s in statuses]

# Create DataFrame
df = pd.DataFrame({
    "Build_ID": build_ids,
    "Build_Status": statuses,
    "Duration": duration,
    "Tests_Run": tests_run,
    "Tests_Failed": tests_failed
})

# Save CSV
df.to_csv("cicd_build_500.csv", index=False)
print("✅ CSV generated with 500 builds (60% Pass, 40% Fail)")
print(df.head())
