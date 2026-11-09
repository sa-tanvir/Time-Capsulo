#!/usr/bin/env bash
# Checks whether this machine can be used for Time Capsulo energy measurements.
# Usage: bash check_machine.sh      (run with sudo to also check RAPL read access)
ok=0
pass() { echo "  [OK]   $1"; }
fail() { echo "  [FAIL] $1"; ok=1; }
warn() { echo "  [WARN] $1"; }

echo "== OS"
[ "$(uname -s)" = "Linux" ] && pass "Linux ($(uname -r))" || fail "Not Linux ($(uname -s)) - RAPL needs native Linux"

echo "== Virtualisation"
virt=$(systemd-detect-virt 2>/dev/null || echo unknown)
case "$virt" in
  none) pass "Bare metal (no hypervisor detected)" ;;
  wsl)  fail "WSL - energy counters not exposed; install native Linux" ;;
  unknown) warn "Could not detect (systemd-detect-virt missing)" ;;
  *)    fail "Running inside a VM/container: $virt" ;;
esac

echo "== CPU"
model=$(grep -m1 'model name' /proc/cpuinfo 2>/dev/null | cut -d: -f2- | sed 's/^ *//')
echo "  $model  ($(nproc 2>/dev/null) logical cores)"
echo "$model" | grep -qiE 'intel|amd' && pass "Intel/AMD x86 CPU" || fail "Not Intel/AMD - no RAPL"

echo "== RAPL energy counters"
if ls -d /sys/class/powercap/intel-rapl:* >/dev/null 2>&1; then
  for d in /sys/class/powercap/intel-rapl:*; do
    name=$(cat "$d/name" 2>/dev/null)
    if v=$(cat "$d/energy_uj" 2>/dev/null); then pass "$d ($name) readable: ${v} uJ"
    else warn "$d ($name) exists but not readable - needs root (run with sudo)"; fi
  done
else
  fail "No /sys/class/powercap/intel-rapl* - kernel module missing or unsupported CPU"
fi

echo "== perf energy events"
if command -v perf >/dev/null; then
  perf list 2>/dev/null | grep -q 'power/energy-pkg/' && pass "perf has power/energy-pkg/" || warn "perf present but no power/energy-pkg/ event"
else warn "perf not installed (sudo apt install linux-tools-common linux-tools-\$(uname -r))"; fi

echo "== Frequency control (needed for stable runs)"
gov=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null) && echo "  governor: $gov (want: performance, set via sudo cpupower)" || warn "No cpufreq interface"
[ -f /sys/devices/system/cpu/intel_pstate/no_turbo ] && echo "  intel no_turbo: $(cat /sys/devices/system/cpu/intel_pstate/no_turbo) (want 1)"
[ -f /sys/devices/system/cpu/cpufreq/boost ] && echo "  boost: $(cat /sys/devices/system/cpu/cpufreq/boost) (want 0)"
[ -f /sys/devices/system/cpu/smt/control ] && echo "  SMT: $(cat /sys/devices/system/cpu/smt/control)"

echo "== Sudo / Docker"
sudo -n true 2>/dev/null && pass "passwordless sudo available" || warn "No passwordless sudo - you need admin rights to set governor and read RAPL"
command -v docker >/dev/null && pass "docker installed" || warn "docker not installed (needed for per-language toolchains)"

echo "== Load (should be idle during measurement)"
uptime
echo
[ $ok -eq 0 ] && echo "RESULT: usable for energy measurement" || echo "RESULT: NOT suitable - see [FAIL] lines"
