import os
import pandas as pd
import matplotlib.pyplot as plt

BASELINE_DURATION_FROM_END_MS = 1000

def last_second_pupil_average(df):
    last_time = df.tail(1)["TIMESTAMP"].mean()
    first_time = last_time - pd.to_timedelta(BASELINE_DURATION_FROM_END_MS, unit="ms")
    ave = df[df.TIMESTAMP >= first_time]["AVERAGE_PUPIL_SIZE"].mean()
    return ave

def make_csv_from_txt(name_root):
    txt_name = f"{name_root}.txt"
    csv_name = f"{name_root}.csv"
    os.system(f"cat {txt_name} |  grep -v 'Full Trial Period' | grep -v 'FREEHAND' > {csv_name}")


# If 101.csv is missing, run this line of code
# make_csv_from_txt("101")

participant = "101"
filename = f"./{participant}.csv"

df = pd.read_csv(filename, delimiter='\t')
df.TIMESTAMP = pd.to_timedelta(pd.to_numeric(df.TIMESTAMP), unit="ms")
df.AVERAGE_PUPIL_SIZE = pd.to_numeric(df.AVERAGE_PUPIL_SIZE, errors="coerce")

baselines = []

nan_baseline_rows = []

for task in df.RECORDING_SESSION_LABEL.unique():
    task_df = df[df.RECORDING_SESSION_LABEL == task]

    for trial in task_df.TRIAL_INDEX.unique():
        trial_df = task_df[task_df.TRIAL_INDEX == trial]

        for ip_label in ["BeginFix", "Fix1"]:
            baseline = last_second_pupil_average(trial_df[trial_df.IP_LABEL==ip_label])
            row = [task, trial, ip_label, baseline]
            if pd.isna(baseline):
                nan_baseline_rows.append(row)
            else:
              baselines.append(row)

print(f"{len(nan_baseline_rows)} baselines could not be calculated due to missing data")

baseline_df = pd.DataFrame(
        baselines,
        columns=["RECORDING_SESSION_LABEL", "TRIAL_INDEX", "IP_LABEL", "BASELINE_VALUE"])

def baseline_by(df, baseline_df, from_ip_label, to_ip_label):
    merge_df = baseline_df.copy()
    merge_df["IP_LABEL"] = merge_df["IP_LABEL"].apply(lambda x: {
        from_ip_label: to_ip_label,
        }.get(x, x))

    df = pd.merge(df, merge_df, on=["RECORDING_SESSION_LABEL", "TRIAL_INDEX", "IP_LABEL"], how="left")
    new_column = f"{from_ip_label}_{to_ip_label}_BASELINED"
    df[new_column] = df["AVERAGE_PUPIL_SIZE"] - df["BASELINE_VALUE"]
    return df.drop("BASELINE_VALUE", axis=1)

df = baseline_by(df, baseline_df, from_ip_label="BeginFix", to_ip_label="Strategy")
df = baseline_by(df, baseline_df, from_ip_label="BeginFix", to_ip_label="Stimulus")

print(df.groupby(["CueName", "Procedure"]).mean())

# TODO: Figure out resampling
#df = df.set_index("TIMESTAMP")
#resample_df = df.resample(pd.to_timedelta(10, unit="ms")).mean()

# dfa = df[df.RECORDING_SESSION_LABEL == "101a"][df.TRIAL_INDEX == 2]
# 
# dfa_begin_fix_baseline = last_second_pupil_average(dfa[dfa.IP_LABEL=="BeginFix"])
# dfa_fix1_baseline = last_second_pupil_average(dfa[dfa.IP_LABEL=="Fix1"])
# 
# baselined_strategy_df = dfa[dfa.IP_LABEL=="Strategy"]
# baselined_strategy_df["BASELINED_AVERAGE_PUPIL_SIZE"] = baselined_strategy_df["AVERAGE_PUPIL_SIZE"].sub(dfa_begin_fix_baseline)
# 
# dfa

# dfa.interpolate().plot(x="TIMESTAMP", y="AVERAGE_PUPIL_SIZE")
# df.loc[:,["TIMESTAMP", "AVERAGE_PUPIL_SIZE"]].plot(x="TIMESTAMP", y="AVERAGE_PUPIL_SIZE", kind="line")

# print(df.head())
# COLUMNS_OF_INTEREST = [
#         "TIMESTAMP",
#         "RECORDING_SESSION_LABEL",
#         "TRIAL_INDEX",
#         "IP_LABEL",
#         "AVERAGE_PUPIL_SIZE",
#         "CueName",
#         ]
# 
