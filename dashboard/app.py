import altair as alt
import pandas as pd
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Traffic Analyzer IoT", layout="wide")
DATA = Path(__file__).resolve().parent.parent / "data"

PROTO_URUT = ["MQTT", "CoAP", "HTTP"]
PROTO_MAP = {"MQTT": "MQTT", "COAP": "CoAP", "HTTP": "HTTP"}

PARAM_TRAFFIC = {
    "packet_rate": "Packet rate (paket/detik)",
    "byte_rate": "Byte rate (byte/detik)",
    "connection_rate": "Connection rate (koneksi/detik)",
    "durasi_sesi_rata": "Durasi sesi rata-rata (detik)",
    "frekuensi_request": "Frekuensi publish/request (per detik)",
    "subscribe_observe": "Subscription/observe (per jendela)",
    "topic_resource_unik": "Topik/resource/endpoint unik (per jendela)",
    "interval_mean": "Interval rata-rata antar pesan (detik)",
    "interval_std": "Simpangan baku interval (detik)",
}
PARAM_PERF = {
    "throughput_Bps": "Throughput (byte/detik)",
    "jitter_s": "Jitter (simpangan baku interval publish, detik)",
    "interval_rata_s": "Interval rata-rata (detik)",
    "jumlah_request": "Jumlah request per run",
    "latency_rata_s": "Latency (belum dihitung)",
    "retransmisi_tcp": "Retransmisi TCP (belum dihitung)",
}
BELUM = {"latency_rata_s", "retransmisi_tcp"}


def proto_std(x):
    """Seragamkan nama protokol: MQTT, CoAP, HTTP (menerima COAP, coap, dll)."""
    kunci = str(x).strip().upper()
    return PROTO_MAP.get(kunci, str(x).strip())


@st.cache_data
def muat():
    d = pd.read_csv(DATA / "traffic_dataset.csv")
    rs = pd.read_csv(DATA / "run_summary.csv")
    d["protokol"] = d["protokol"].map(proto_std)
    rs["protokol"] = rs["protokol"].map(proto_std)
    rs["skenario"] = rs["run_id"].str.rsplit("_run", n=1).str[0]
    d["waktu"] = (pd.to_datetime(d["jendela"], unit="s", utc=True)
                  .dt.tz_convert("Asia/Jakarta").dt.strftime("%H:%M:%S"))
    return d, rs


if not (DATA / "traffic_dataset.csv").exists():
    st.error("data/traffic_dataset.csv tidak ditemukan. Jalankan dari folder proyek.")
    st.stop()

d, rs = muat()

# ---------- Sidebar ----------
st.sidebar.header("Filter")
skenario = st.sidebar.selectbox("Skenario", sorted(d["skenario"].unique()))

protokol_ada = [p for p in PROTO_URUT if p in set(d["protokol"])]
protokol = st.sidebar.multiselect("Protokol", protokol_ada, default=protokol_ada)
if not protokol:
    st.warning("Pilih minimal satu protokol di sidebar.")
    st.stop()

run_list = sorted(d.loc[d["skenario"] == skenario, "run_id"].unique())
run = st.sidebar.selectbox("Run", run_list)
ambang = st.sidebar.slider("Ambang 'terlihat' (kali baseline)", 1.5, 3.0, 2.0, 0.5)
st.sidebar.caption("Ambang 2× adalah keputusan tim, bukan standar eksternal.")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Ringkasan", "Timeline", "Normal vs anomali", "Performa", "Tentang data"])

# ---------- Tab 1: Ringkasan ----------
with tab1:
    st.subheader("Ringkasan dataset")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Baris jendela", f"{len(d):,}")
    c2.metric("Run", d["run_id"].nunique())
    c3.metric("Jendela anomali", f"{(d['label'] == 'anomali').sum():,}")
    c4.metric("Persen anomali", f"{(d['label'] == 'anomali').mean() * 100:.1f}%")
    dist = d.groupby(["skenario", "label"]).size().reset_index(name="jumlah")
    st.altair_chart(
        alt.Chart(dist).mark_bar().encode(
            x=alt.X("skenario:N", title="Skenario"),
            y=alt.Y("jumlah:Q", title="Jumlah jendela"),
            color=alt.Color("label:N", scale=alt.Scale(domain=["normal", "anomali"],
                                                       range=["#4c78a8", "#e45756"])),
            tooltip=["skenario", "label", "jumlah"],
        ), use_container_width=True)

# ---------- Tab 2: Timeline ----------
with tab2:
    st.subheader(f"Timeline: {run}")
    metrik = st.selectbox("Parameter traffic", list(PARAM_TRAFFIC), format_func=PARAM_TRAFFIC.get,
                          key="tl_metrik")
    sub = d[(d["run_id"] == run) & (d["protokol"].isin(protokol))].copy()
    sub["detik"] = sub["jendela"] - sub["jendela"].min()
    if sub.empty:
        st.info("Tidak ada data untuk pilihan ini.")
    else:
        st.altair_chart(
            alt.Chart(sub).mark_line(point=True).encode(
                x=alt.X("detik:Q", title="Detik sejak awal run"),
                y=alt.Y(f"{metrik}:Q", title=PARAM_TRAFFIC[metrik]),
                color=alt.Color("label:N", scale=alt.Scale(domain=["normal", "anomali"],
                                                           range=["#4c78a8", "#e45756"])),
                row=alt.Row("protokol:N", title=None, sort=PROTO_URUT),
                tooltip=["waktu", "protokol", "label", alt.Tooltip(f"{metrik}:Q", format=".3f")],
            ).properties(width=800, height=140),
        )
        st.caption("Titik merah = jendela anomali menurut jadwal burst (anomali_interval.csv). "
                   "Setiap protokol ditampilkan di baris sendiri.")

# ---------- Tab 3: Normal vs anomali ----------
with tab3:
    st.subheader("Perbandingan normal dan anomali (rata-rata per jendela)")
    metrik3 = st.selectbox("Parameter traffic", list(PARAM_TRAFFIC), format_func=PARAM_TRAFFIC.get,
                           key="bd_metrik")
    g = d.groupby(["skenario", "protokol", "label"])[metrik3].mean().unstack("label")
    g = g.reindex(columns=["normal", "anomali"]).reset_index()
    g["rasio"] = g["anomali"] / g["normal"].replace(0, pd.NA)

    def status(r):
        if pd.isna(r["anomali"]):
            return "tanpa jendela anomali"
        if pd.isna(r["rasio"]):
            return "baseline nol"
        return "terlihat" if (r["rasio"] >= ambang or r["rasio"] <= 1 / ambang) else "tidak terlihat"

    g["status"] = g.apply(status, axis=1)
    g = g[g["protokol"].isin(protokol)].round(3)
    st.dataframe(g, use_container_width=True, hide_index=True)
    st.download_button("Unduh tabel (CSV)", g.to_csv(index=False).encode("utf-8"),
                       file_name=f"perbandingan_{metrik3}.csv")

# ---------- Tab 4: Performa ----------
with tab4:
    st.subheader("Parameter performa per skenario (rata-rata run)")
    metrik4 = st.selectbox("Parameter performa", list(PARAM_PERF), format_func=PARAM_PERF.get,
                           key="pf_metrik")
    if metrik4 in BELUM:
        st.info(f"{PARAM_PERF[metrik4]}: belum dihitung di skrip ekstraksi. Kolom kosong, "
                "sehingga tidak ditampilkan sebagai grafik.")
    else:
        rs_f = rs[rs["protokol"].isin(protokol)]
        agg = rs_f.groupby(["skenario", "protokol"])[metrik4].agg(["mean", "std", "count"]).reset_index()
        st.altair_chart(
            alt.Chart(agg).mark_bar().encode(
                x=alt.X("skenario:N", title="Skenario"),
                y=alt.Y("mean:Q", title=PARAM_PERF[metrik4]),
                color=alt.Color("protokol:N", sort=PROTO_URUT),
                xOffset=alt.XOffset("protokol:N", sort=PROTO_URUT),
                tooltip=["skenario", "protokol", alt.Tooltip("mean:Q", format=".3f"),
                         alt.Tooltip("std:Q", format=".3f"), "count"],
            ), use_container_width=True)
        st.caption("Simpangan baku antar tiga run ditampilkan di tooltip. Jika simpangan besar, "
                   "perbedaan rata-rata belum tentu bermakna.")

# ---------- Tab 5: Tentang data ----------
with tab5:
    st.subheader("Tentang data")
    st.markdown(
        "- Data dibuat dari generator di jaringan uji, bukan data serangan nyata.\n"
        "- Dashboard bersifat offline dan tidak real-time.\n"
        "- Burst dan publish dijalankan dari laptop. ESP tetap mengirim traffic normal.\n"
        "- S4 tidak menjalankan HTTP polling (lihat catatan di setup log).\n"
        "- Latency dan retransmisi TCP belum dihitung.\n"
        "- `jitter_s` adalah simpangan baku interval publish, bukan jitter RFC 3393.\n"
        "- `byte_total` dihitung dari panjang frame, bukan payload.")
    p = DATA.parent / "docs" / "PARAMETER_FITUR.md"
    if p.exists():
        st.markdown(p.read_text(encoding="utf-8"))