#!/usr/bin/env python3
"""Describe the machine a sweep ran on, in one line, using nothing but the standard library.

A score is only readable next to the hardware that produced it, and a hardware line typed by
hand goes stale the moment someone else runs a sweep. Every probe here fails soft: an unknown
part is left out rather than raised, since a table with a vague machine line is still a table.

Run it alone to see what it reports on your machine: python3 tests/hardware.py
"""

import os
import platform
import re
import subprocess
import sys

def _run(command):
    """A short-lived helper process, or None. Anything at all going wrong means None."""
    try:
        out = subprocess.run(command, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


def cpu():
    system = platform.system()
    if system == "Linux":
        try:
            for line in open("/proc/cpuinfo", encoding="utf-8", errors="replace"):
                if line.startswith("model name"):
                    return tidy(line.split(":", 1)[1])
        except OSError:
            pass
    elif system == "Darwin":
        brand = _run(["sysctl", "-n", "machdep.cpu.brand_string"])
        if brand:
            return tidy(brand)
    elif system == "Windows":
        # The environment variable holds a family string, not a model, so the registry is worth
        # the import; it is in the standard library and reading it needs no privilege.
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            with key:
                return tidy(winreg.QueryValueEx(key, "ProcessorNameString")[0])
        except (ImportError, OSError):
            pass
    return tidy(platform.processor()) or platform.machine() or None


def tidy(name):
    """Marketing noise off a processor string, keeping the model that identifies it."""
    name = re.sub(r"\((?:R|TM)\)", "", name, flags=re.I)
    name = re.sub(r"\s+@.*$", "", name)
    name = re.sub(r"\b(?:CPU|Processor|\d+-Core)\b", "", name, flags=re.I)
    return " ".join(name.split()) or None


# What gets sold. The kernel reports usable pages, which on a 64 GB machine comes to 61, and a
# table that says 61 GB invites the reader to wonder what the odd number means.
CAPACITIES = (4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256, 384, 512, 768, 1024)


def installed(gigabytes):
    """The nearest capacity a machine is actually sold with, where one is close enough."""
    fit = [c for c in CAPACITIES if c >= gigabytes and c - gigabytes <= 0.1 * c]
    return fit[0] if fit else gigabytes


def ram_gb():
    if hasattr(os, "sysconf") and "SC_PHYS_PAGES" in os.sysconf_names:
        try:
            pages = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
            return installed(pages / 1024 ** 3)
        except (OSError, ValueError):
            pass
    if platform.system() == "Windows":
        try:
            import ctypes

            class Status(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong),
                            ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong),
                            ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong),
                            ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

            status = Status()
            status.dwLength = ctypes.sizeof(Status)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                return installed(status.ullTotalPhys / 1024 ** 3)
        except (ImportError, OSError, AttributeError):
            pass
    return None


def gpu():
    """Name and memory of the first accelerator, or None. nvidia-smi ships with the driver on
    both Windows and Linux, which is what makes this portable without a dependency."""
    listing = _run(["nvidia-smi", "--query-gpu=name,memory.total",
                    "--format=csv,noheader,nounits"])
    if listing:
        name, _, mib = listing.splitlines()[0].partition(",")
        try:
            return f"{name.strip()} ({round(int(mib.strip()) / 1024)} GB)"
        except ValueError:
            return name.strip()
    if platform.system() == "Darwin":
        # Apple silicon has no separate card; the chip is already in the processor string.
        return None
    listing = _run(["rocm-smi", "--showproductname", "--csv"])
    if listing:
        for line in listing.splitlines()[1:]:
            field = line.split(",")[-1].strip()
            if field:
                return field
    return None


def describe():
    """One line naming the machine, with whatever could be found. Comma-separated rather than
    written out, so no article has to be guessed in front of a brand name. Never raises."""
    try:
        parts = [part for part in (cpu(), gpu()) if part]
        memory = ram_gb()
        if memory:
            parts.append(f"{memory} GB RAM")
        return ", ".join(parts) or "an unrecorded machine"
    except Exception:  # noqa: BLE001 — a hardware line is never worth failing a sweep over
        return "an unrecorded machine"


if __name__ == "__main__":
    print(describe())
    sys.exit(0)
