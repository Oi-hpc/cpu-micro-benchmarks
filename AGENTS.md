# Repository Guidelines

## Project Structure & Module Organization

`src/` contains the main C++ microbenchmarks. `*_gen.cpp` files generate assembly gadgets, `*_lib.cpp` files provide reusable benchmark implementations, and the remaining `.cpp` files build runnable binaries. `include/` holds shared timing, counter, JIT, instruction, and uarch helpers. `benchmarks/` contains standalone C/assembly case studies with their own `Makefile`s. `figures/` has Python plotting scripts that consume benchmark CSV files from the current directory. `results/` and `reports/` store benchmark outputs and paper/report material; `agner/` is reference/vendor PMU code.

## Build, Test, and Development Commands

- `make`: configures `builddir/` with Meson release settings, then builds with Ninja.
- `ninja -C builddir`: rebuilds incrementally after setup.
- `make clean`: removes compiled targets in `builddir/`.
- `make distclean`: deletes `builddir/`.
- `make android`, `make ios`, `make aarch64-linux`, `make gem5`: build supported cross or simulator targets.
- `(cd benchmarks/vfmax && make)`: builds a standalone benchmark subproject; use the same pattern under `benchmarks/`.
- `poetry install`: installs Python plotting dependencies such as Matplotlib.

## Coding Style & Naming Conventions

Use C++11 for Meson-built code and follow the existing two-space indentation, same-line braces, and `snake_case` filenames/functions. Keep benchmark names aligned across `meson.build`, `src/<name>.cpp`, optional `src/<name>_gen.cpp`, and optional `src/<name>_lib.cpp`. Prefer explicit hardware feature macros such as `HOST_AARCH64` or `NO_FJCVTZS`. Do not edit generated files under `builddir/`; update the generator or source instead.

## Testing Guidelines

There is no formal automated test suite in Meson. Treat a clean release build as baseline validation, then run the affected benchmark with reduced iterations when practical, for example `./builddir/memory_latency -w 100 -i 1000`. Perf-counter modes such as `-p` or `-f` may require platform support and permissions, so document the CPU, OS, and privileges used. For plotting changes, run the relevant `figures/plot_*.py` script and verify the generated image.

## Commit & Pull Request Guidelines

Recent commits use short imperative subjects such as `Add MIT license`, `Rename clang to clang22`, and `Improve mixed sign dotprod docs`. Keep the subject concise, and use the body for benchmark methodology or result context. Pull requests should state the target architecture, compiler version, exact build/run commands, and changed result or figure paths. Link related issues or reports when applicable.

## Security & Configuration Tips

Avoid committing local build directories or scratch CSVs unless they are intentional results. Cross-target builds depend on the checked-in `*-cross.txt` files and hardware-specific compiler flags; note any local toolchain assumptions in the PR description.
