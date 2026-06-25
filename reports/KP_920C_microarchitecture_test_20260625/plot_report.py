#!/usr/bin/env python3
import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
PLOTS = ROOT / "plots"
PLOTS.mkdir(exist_ok=True)


def read_dict_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def read_numeric_csv_with_preamble(path):
    rows = []
    header = None
    with path.open(newline="") as f:
        for row in csv.reader(f):
            if not row:
                continue
            if header is None:
                if row[0] in ("size", "pages"):
                    header = row
                continue
            rows.append(dict(zip(header, row)))
    return rows


def to_float(value, default=math.nan):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def latency_range(value):
    parts = [to_float(part) for part in str(value).split("/") if part]
    parts = [part for part in parts if not math.isnan(part)]
    if not parts:
        return math.nan, math.nan
    return min(parts), max(parts)


def save_current(name):
    plt.tight_layout()
    plt.savefig(PLOTS / name, dpi=160)
    plt.close()


def plot_fp_peak(metrics):
    rows = read_dict_csv(RAW / "fp_peak" / "fp_peak.csv")
    names = [row["pattern"] for row in rows]
    avg = [to_float(row["avg"]) for row in rows]
    mins = [to_float(row["min"]) for row in rows]
    maxs = [to_float(row["max"]) for row in rows]

    colors = ["#777777", "#999999", "#2b6cb0", "#63b3ed", "#c05621", "#ed8936"]
    plt.figure(figsize=(9, 4.8))
    plt.bar(names, avg, color=colors[: len(names)], label="avg")
    plt.scatter(names, mins, marker="_", s=120, color="black", label="min/max")
    plt.scatter(names, maxs, marker="_", s=120, color="black")
    plt.ylabel("FLOPs/cycle")
    plt.title("FMA peak throughput")
    plt.xticks(rotation=25, ha="right")
    plt.legend()
    save_current("plot_fp_peak.png")

    by_name = {row["pattern"]: to_float(row["avg"]) for row in rows}
    metrics["fp_peak"] = by_name


def plot_instruction_latency(metrics):
    rows = read_dict_csv(RAW / "instruction_latency" / "instruction_latency.csv")
    wanted = [
        "fp_fmadd_single",
        "fp_fmadd_double",
        "asimd_fp_fmla_single",
        "asimd_fp_fadd_single",
        "asimd_fp_fmul_single",
        "asimd_fp_fadd_double",
        "asimd_fp_fmul_double",
    ]
    by_name = {row["name"]: row for row in rows}
    labels = []
    min_lat = []
    max_lat = []
    ipc = []
    for name in wanted:
        row = by_name.get(name)
        if not row:
            continue
        lo, hi = latency_range(row["latency"])
        labels.append(name.replace("_", "\n"))
        min_lat.append(lo)
        max_lat.append(hi)
        value = to_float(row.get("throughput(ipc)"))
        ipc.append(value if math.isfinite(value) else math.nan)

    fig, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
    axes[0].bar(labels, max_lat, color="#2b6cb0", label="max observed latency")
    axes[0].scatter(labels, min_lat, color="black", marker="_", s=120, label="min observed latency")
    axes[0].set_ylabel("cycles")
    axes[0].set_title("Instruction latency for FP/ASIMD ops")
    axes[0].legend()
    axes[1].bar(labels, ipc, color="#c05621")
    axes[1].set_ylabel("instructions/cycle")
    axes[1].set_title("Throughput entries present in instruction_latency.csv")
    axes[1].tick_params(axis="x", rotation=0)
    save_current("plot_instruction_latency.png")

    metrics["instruction_latency"] = {
        name: {
            "latency": by_name[name]["latency"],
            "throughput_ipc": by_name[name]["throughput(ipc)"],
        }
        for name in wanted
        if name in by_name
    }


def plot_register_file(metrics):
    rows = read_dict_csv(RAW / "register_file_size" / "register_file_size.csv")
    labels = {
        4: "scalar FP",
        5: "NEON/ASIMD",
        6: "SVE",
    }
    data = {pattern: [] for pattern in labels}
    for row in rows:
        pattern = int(row["pattern"])
        if pattern in data:
            data[pattern].append((int(row["size"]), to_float(row["min"])))
    plt.figure(figsize=(9, 5))
    for pattern, points in data.items():
        points.sort()
        if points:
            xs, ys = zip(*points)
            plt.plot(xs, ys, label=labels[pattern])
    plt.xlabel("independent filler instructions")
    plt.ylabel("time per iteration (min)")
    plt.title("Register-file / rename pressure")
    plt.legend()
    plt.grid(alpha=0.25)
    save_current("plot_register_file_size.png")
    metrics["register_file_rows"] = len(rows)


def plot_rob(metrics):
    rows = read_dict_csv(RAW / "rob_size" / "rob_size.csv")
    xs = [to_float(row["size"]) for row in rows]
    mins = [to_float(row["min"]) for row in rows]
    avgs = [to_float(row["avg"]) for row in rows]
    plt.figure(figsize=(9, 5))
    plt.plot(xs, mins, label="min")
    plt.plot(xs, avgs, label="avg", alpha=0.75)
    plt.xlabel("instruction block size")
    plt.ylabel("time")
    plt.title("ROB-size probe")
    plt.legend()
    plt.grid(alpha=0.25)
    save_current("plot_rob_size.png")
    metrics["rob_rows"] = len(rows)


def plot_scheduler(metrics):
    rows = read_dict_csv(RAW / "sched_size" / "sched_size.csv")
    labels = {
        0: "load dep",
        1: "store addr dep",
        2: "store data dep",
        5: "FP dep",
        13: "load + indep",
        14: "store addr + indep",
        15: "store data + indep",
        18: "FP + indep",
    }
    data = {pattern: [] for pattern in labels}
    for row in rows:
        pattern = int(row["pattern"])
        if pattern in data:
            data[pattern].append((int(row["size"]), to_float(row["min"])))
    plt.figure(figsize=(10, 6))
    for pattern, points in data.items():
        points.sort()
        if points:
            xs, ys = zip(*points)
            plt.plot(xs, ys, label=labels[pattern])
    plt.xlabel("scheduler filler instructions")
    plt.ylabel("time per iteration (min)")
    plt.title("Scheduler pressure probes")
    plt.legend(ncol=2, fontsize=8)
    plt.grid(alpha=0.25)
    save_current("plot_scheduler_size.png")
    metrics["sched_rows"] = len(rows)


def plot_memory(metrics):
    rows = read_numeric_csv_with_preamble(RAW / "memory_latency" / "memory_latency.csv")
    xs = [to_float(row["size"]) for row in rows]
    time = [to_float(row["time(ns)"]) for row in rows]
    cycles = [to_float(row.get("cycles")) for row in rows]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(xs, time, label="time(ns)", color="#2b6cb0")
    ax.set_xscale("log")
    ax.set_xlabel("memory block size (B)")
    ax.set_ylabel("time (ns)")
    ax.grid(alpha=0.25)
    if any(math.isfinite(v) for v in cycles):
        ax2 = ax.twinx()
        ax2.plot(xs, cycles, label="cycles", color="#c05621", alpha=0.65)
        ax2.set_ylabel("cycles")
    ax.set_title("Pointer-chasing memory latency")
    save_current("plot_memory_latency.png")
    metrics["memory_rows"] = len(rows)
    if rows:
        metrics["memory_first"] = rows[0]
        metrics["memory_last"] = rows[-1]


def plot_dtlb(metrics):
    rows = read_numeric_csv_with_preamble(RAW / "dtlb_size" / "dtlb_size.csv")
    xs = [to_float(row["pages"]) for row in rows]
    cycles = [to_float(row.get("cycles", row.get("time(ns)"))) for row in rows]
    plt.figure(figsize=(9, 5))
    plt.plot(xs, cycles, color="#2b6cb0")
    plt.xlabel("pages")
    plt.ylabel("cycles" if "cycles" in rows[0] else "time (ns)")
    plt.title("DTLB pressure probe")
    plt.grid(alpha=0.25)
    save_current("plot_dtlb_size.png")
    metrics["dtlb_rows"] = len(rows)
    if rows:
        metrics["dtlb_last"] = rows[-1]


def plot_fetch(metrics):
    rows = read_dict_csv(RAW / "fetch_bandwidth" / "fetch_bandwidth.csv")
    xs = [to_float(row["size"]) for row in rows]
    avg = [to_float(row["avg"]) for row in rows]
    mins = [to_float(row["min"]) for row in rows]
    plt.figure(figsize=(9, 5))
    plt.plot(xs, avg, label="avg IPC")
    plt.plot(xs, mins, label="min IPC", alpha=0.65)
    plt.xscale("log")
    plt.xlabel("loop body size (B)")
    plt.ylabel("instructions/cycle")
    plt.title("Fetch bandwidth / frontend stability")
    plt.legend()
    plt.grid(alpha=0.25)
    save_current("plot_fetch_bandwidth.png")
    metrics["fetch_rows"] = len(rows)


def write_metrics(metrics):
    fp = metrics.get("fp_peak", {})
    asimd_sp = fp.get("128-bit SP ASIMD", math.nan)
    asimd_dp = fp.get("128-bit DP ASIMD", math.nan)
    sve_sp = next((v for k, v in fp.items() if "SP SVE" in k), math.nan)
    sve_dp = next((v for k, v in fp.items() if "DP SVE" in k), math.nan)

    lines = [
        "# Summary Metrics",
        "",
        f"- ASIMD SP FMLA avg: {asimd_sp:.2f} FLOPs/cycle",
        f"- SVE SP FMLA avg: {sve_sp:.2f} FLOPs/cycle",
        f"- SVE/ASIMD SP ratio: {sve_sp / asimd_sp:.2f}x" if asimd_sp else "- SVE/ASIMD SP ratio: n/a",
        f"- ASIMD DP FMLA avg: {asimd_dp:.2f} FLOPs/cycle",
        f"- SVE DP FMLA avg: {sve_dp:.2f} FLOPs/cycle",
        f"- SVE/ASIMD DP ratio: {sve_dp / asimd_dp:.2f}x" if asimd_dp else "- SVE/ASIMD DP ratio: n/a",
        "",
        "## Instruction Latency",
    ]
    for name, values in metrics.get("instruction_latency", {}).items():
        lines.append(f"- {name}: latency {values['latency']} cycles, throughput {values['throughput_ipc']} instr/cycle")
    lines += [
        "",
        "## Coverage",
        f"- register_file_size rows: {metrics.get('register_file_rows', 0)}",
        f"- sched_size rows: {metrics.get('sched_rows', 0)}",
        f"- rob_size rows: {metrics.get('rob_rows', 0)}",
        f"- memory_latency rows: {metrics.get('memory_rows', 0)}",
        f"- dtlb_size rows: {metrics.get('dtlb_rows', 0)}",
        f"- fetch_bandwidth rows: {metrics.get('fetch_rows', 0)}",
    ]
    (ROOT / "summary_metrics.md").write_text("\n".join(lines) + "\n")


def main():
    metrics = {}
    plot_fp_peak(metrics)
    plot_instruction_latency(metrics)
    plot_register_file(metrics)
    plot_rob(metrics)
    plot_scheduler(metrics)
    plot_memory(metrics)
    plot_dtlb(metrics)
    plot_fetch(metrics)
    write_metrics(metrics)


if __name__ == "__main__":
    main()
