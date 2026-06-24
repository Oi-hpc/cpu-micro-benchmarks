from matplotlib import pyplot as plt
import csv

# pattern index -> human label
labels = {
    0: "32-bit ALU (int)",
    1: "64-bit ALU (int)",
    2: "flags (cmp)",
    3: "rename (mov)",
    4: "32-bit FP scalar (s)",
    5: "128-bit NEON (v)",
    6: "SVE vector (z)",
}

# pattern -> {size: avg}
data = {p: {} for p in labels}

with open('register_file_size.csv', newline='') as f:
    r = csv.DictReader(f)
    for row in r:
        p = int(row["pattern"])
        if p in labels:
            data[p][int(row["size"])] = float(row["min"])

for p in sorted(labels):
    if not data[p]:
        continue
    sizes = sorted(data[p])
    plt.plot(sizes, [data[p][s] for s in sizes], label=labels[p])

plt.ylabel('Time per iteration (min)')
plt.xlabel('Number of independent filler instructions')
plt.title('Physical register file / rename capacity')
plt.legend()
plt.tight_layout()
plt.savefig('plot_register_file_size.png')
