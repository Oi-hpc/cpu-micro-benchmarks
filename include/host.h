#ifndef __HOST_H__
#define __HOST_H__

// Detect host ISA when build files do not pass an explicit HOST_* macro.
#if !defined(HOST_AARCH64) && !defined(HOST_AMD64) &&                         \
    !defined(HOST_LOONGARCH64) && !defined(HOST_PPC64LE)
#ifdef __x86_64__
#define HOST_AMD64
#endif
#ifdef __aarch64__
#define HOST_AARCH64
#endif
#ifdef __loongarch__
#define HOST_LOONGARCH64
#endif
#if defined(__powerpc64__)
#define HOST_PPC64LE
#endif
#endif

// armv9-a assembler support landed in GCC 11 / Clang 12. Prefer the higher
// baseline when the toolchain can assemble it, else fall back to armv8-a+sve.
#if (defined(__clang__) && __clang_major__ >= 12) ||                               \
    (defined(__GNUC__) && !defined(__clang__) && __GNUC__ >= 11)
#define SVE_ARCH "armv9-a+sve"
#else
#define SVE_ARCH "armv8-a+sve"
#endif

#endif
