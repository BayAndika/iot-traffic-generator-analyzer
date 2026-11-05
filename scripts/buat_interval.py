import pandas as pd

d = pd.read_csv("metadata/anomali_log.csv")
iv = pd.DataFrame({
    "run_id": d["run"],
    "protokol": d["protokol"],
    "mulai": d["mulai"],
    "selesai": d["selesai"],
    "skenario_anomali": d["skenario"],
})
iv.to_csv("metadata/anomali_interval.csv", index=False)
print(len(iv), "baris ditulis")
