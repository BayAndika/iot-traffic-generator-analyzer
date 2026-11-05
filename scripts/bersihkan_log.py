import pandas as pd

cols = ["run", "protokol", "skenario", "mulai", "selesai", "aksi", "galat"]
d = pd.read_csv("metadata/anomali_log_mentah.csv", header=None, names=cols)

pilot = d[d["run"].str.startswith(("pilot", "uji"))]
pilot.to_csv("metadata/anomali_log_pilot.csv", index=False)
d = d[~d["run"].str.startswith(("pilot", "uji"))].copy()

# Blok S6 publish: tentukan run dari waktu mulai burst run yang sesuai
d["mulai_dt"] = pd.to_datetime(d["mulai"])
burst_s6 = d[(d["skenario"] == "burst") & (d["run"].str.startswith("S6_"))].copy()
burst_s6 = burst_s6.sort_values("mulai_dt")

# Burst S6 dibuat per protokol, jadi ambil waktu selesai burst MQTT tiap run
ref = burst_s6[burst_s6["protokol"] == "mqtt"].sort_values("mulai_dt")
ref_run = ref["run"].tolist()
ref_selesai = pd.to_datetime(ref["selesai"]).tolist()

publish_s6 = d[(d["skenario"] == "publish") & (d["run"].str.startswith("S6_"))].index
for i in publish_s6:
    waktu = d.at[i, "mulai_dt"]
    for run_nama, sel in zip(ref_run, ref_selesai):
        if 0 <= (waktu - sel).total_seconds() <= 180:
            d.at[i, "run"] = run_nama
            break

d = d.drop(columns=["mulai_dt"])
d.to_csv("metadata/anomali_log.csv", index=False)
print(d.groupby("run").size())
