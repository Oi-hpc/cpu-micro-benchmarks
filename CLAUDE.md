# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

CPU microarchitecture benchmark suite (aarch64-first, also x86_64, loongarch64, ppc64le). Measures μarch dimensions — ROB size, branch predictor structures (BTB/GHR/PHR/PHT/RAS), instruction/cache latencies, TLB, fetch/issue widths, register file, scheduler, etc. Code and results back the paper *Dissecting Conditional Branch Predictors of Apple Firestorm and Qualcomm Oryon* (see `reports/`).

## Build & run

Build is Meson + Ninja. There is no automated test suite — a clean release build *is* the baseline.

- `make` — `meson setup builddir --buildtype=release && ninja -C builddir`
- `ninja -C builddir` — incremental rebuild
- `make clean` / `make distclean`
- Cross targets: `make android`, `make ios`, `make aarch64-linux`, `make gem5` (each writes its own `builddir-*` dir via the matching `*-cross.txt`)
- Run a binary: `./builddir/<name>` (e.g. `./builddir/rob_size`). Most accept flags to reduce runtime, e.g. `./builddir/memory_latency -w 100 -i 1000`. Perf-counter modes (`-p`, `-f`) need platform PMU support + privileges.
- Standalone C/asm case studies live under `benchmarks/<name>/` with their own `Makefile`: `(cd benchmarks/vfmax && make && ./benchmark)`.

Plotting: `figures/plot_<name>.py` consumes a `<name>.csv` from the CWD and writes a PNG. `poetry install` for matplotlib deps.

## Architecture

**Build model (read `meson.build` before editing the benchmark list).** Benchmarks fall into three roles, encoded by convention in `src/`:
- `<name>.cpp` — the runnable binary (writes results to `<name>.csv`).
- `<name>_gen.cpp` — an assembly-gadget generator. Built *native* and run at configure time; its stdout is a `.S` file (`<name>_gadget.S`) that the real binary links against. This is how benchmark loops get emitted as precise, compiler-proof assembly.
- `<name>_lib.cpp` — optional reusable benchmark implementation linked as a static lib.

The `progs` array in `meson.build` is `[name, needs_nasm, build_as_lib, has_generator]`. **To add a benchmark you must add a row here** with the right flags — there is one source of truth. For x86_64 gadgets that need nasm, set the flag so they're assembled with `--limit-rep`. Generated artifacts go under `builddir/`; never hand-edit them — fix the generator.

**μarch detection.** When not cross-compiling, `meson.build` compiles and runs `src/detect_uarch.cpp` (linked against `src/uarch.cpp`) at configure time; its `-D...` stdout is appended to `cpp_args` for the real build. So `include/uarch.h`'s `enum uarch` → macro mapping drives what feature macros a benchmark sees. Cross builds set the host via the checked-in `*-cross.txt` files and options (`-DHOST_AARCH64`, `-DNO_FJCVTZS`, `-march=armv8.4-a`, etc.).

**Shared infra (`include/`).** `utils.h/.cpp` — timing (`get_time_or_cycles`, prioritizes cycle counter via `setup_time_or_cycles`), `bind_to_core`, pointer-chasing buffer generation (`generate_random_pointer_chasing`, lmbench-style), PMU counters and top-down analysis. `jit.h` — runtime mmap'd code emission. `instrs.h`/`counters.h`/`counters_mapping.h` — instruction encoders and PMU event mappings. `uarch.h` — the `enum uarch` (Apple/Qualcomm/Arm/HiSilicon/Intel/AMD/IBM/Loongson cores).

**Calling conventions** (relevant for hand-written/generated asm) are documented in `NOTES.md`. `AGENTS.md` documents the broader project conventions.

## Conventions

- C++11, two-space indent, same-line braces, `snake_case` for files/functions.
- Keep a benchmark name aligned across `meson.build`, `src/<name>.cpp`, and optional `_gen`/`_lib` siblings.
- Prefer explicit hardware macros (`HOST_AARCH64`, `NO_FJCVTZS`, `APPLE_SILICON`) over runtime branching in gadget code.
- Many `*_gen.cpp` files have bilingual (English + Chinese) explanatory comments — preserve both when editing.
- `rob_size.csv` is checked in as a sample result; treat it as output, not source.
