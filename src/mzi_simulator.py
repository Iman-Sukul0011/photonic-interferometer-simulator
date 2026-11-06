
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# =========================================================
# PHOTONIC INTERFEROMETER SIMULATOR
# Mach-Zehnder Interferometer (MZI)
# =========================================================

OUTPUT = Path("results")
OUTPUT.mkdir(exist_ok=True)


# ---------------------------------------------------------
# 1. DIRECTIONAL COUPLER
# ---------------------------------------------------------

def directional_coupler(kappa=0.5):

    if not 0 <= kappa <= 1:
        raise ValueError("Coupling coefficient must be 0 to 1")

    t = np.sqrt(1 - kappa)
    k = np.sqrt(kappa)

    return np.array([
        [t, 1j * k],
        [1j * k, t]
    ], dtype=complex)


# ---------------------------------------------------------
# 2. MACH-ZEHNDER INTERFEROMETER ENGINE
# ---------------------------------------------------------

def simulate_mzi(
    phase_difference,
    input_power=1.0,
    kappa1=0.5,
    kappa2=0.5,
    loss_arm1_db=0.0,
    loss_arm2_db=0.0
):

    C1 = directional_coupler(kappa1)
    C2 = directional_coupler(kappa2)

    phase = np.asarray(phase_difference)

    E_in = np.array([np.sqrt(input_power), 0], dtype=complex)

    E_split = C1 @ E_in

    phi1 = phase / 2
    phi2 = -phase / 2

    E1 = E_split[0] * np.exp(1j * phi1)
    E2 = E_split[1] * np.exp(1j * phi2)

    # Convert power loss in dB to field attenuation
    E1 *= 10 ** (-loss_arm1_db / 20)
    E2 *= 10 ** (-loss_arm2_db / 20)

    E_out1 = C2[0, 0] * E1 + C2[0, 1] * E2
    E_out2 = C2[1, 0] * E1 + C2[1, 1] * E2

    return np.stack(
        [np.abs(E_out1)**2, np.abs(E_out2)**2],
        axis=-1
    )


# ---------------------------------------------------------
# 3. VOLTAGE CONTROLLED PHASE SHIFTER
# ---------------------------------------------------------

def voltage_to_phase(voltage, v_pi, bias_phase=0.0):

    if v_pi <= 0:
        raise ValueError("V_pi must be positive")

    return np.pi * np.asarray(voltage) / v_pi + bias_phase


# ---------------------------------------------------------
# 4. WAVELENGTH DEPENDENT PHASE
# ---------------------------------------------------------

def wavelength_to_phase(
    wavelength,
    n_eff,
    n_group,
    delta_L,
    lambda_ref=1550e-9
):

    wavelength = np.asarray(wavelength)

    # First-order approximation to effective index dispersion
    n_eff_lambda = (
        n_eff
        + (n_eff - n_group)
        * (wavelength - lambda_ref) / lambda_ref
    )

    return 2 * np.pi * n_eff_lambda * delta_L / wavelength


# ---------------------------------------------------------
# 5. FREE SPECTRAL RANGE
# ---------------------------------------------------------

def calculate_fsr(wavelength, n_group, delta_L):

    if n_group <= 0 or delta_L <= 0:
        raise ValueError("Group index and path difference must be positive")

    return wavelength**2 / (n_group * delta_L)


# ---------------------------------------------------------
# 6. DEVICE PERFORMANCE METRICS
# ---------------------------------------------------------

def calculate_metrics(power, input_power=1.0):

    maximum = np.max(power)
    minimum = np.min(power)

    extinction_ratio = (
        np.inf if minimum <= 1e-15
        else 10 * np.log10(maximum / minimum)
    )

    insertion_loss = (
        np.inf if maximum <= 0
        else -10 * np.log10(maximum / input_power)
    )

    return {
        "Maximum transmission": maximum / input_power,
        "Minimum transmission": minimum / input_power,
        "Extinction ratio (dB)": extinction_ratio,
        "Insertion loss (dB)": insertion_loss
    }


# =========================================================
# 7. EXPERIMENT A: PHASE RESPONSE
# =========================================================

phase = np.linspace(0, 2*np.pi, 1000)

power = simulate_mzi(phase)

P1 = power[:, 0]
P2 = power[:, 1]

plt.figure(figsize=(9, 5))
plt.plot(phase/np.pi, P1, label="Output 1")
plt.plot(phase/np.pi, P2, label="Output 2")

plt.xlabel("Differential phase (π radians)")
plt.ylabel("Normalized optical power")
plt.title("MZI Phase Response")
plt.grid()
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT / "phase_response.png", dpi=300)


# =========================================================
# 8. EXPERIMENT B: VOLTAGE RESPONSE
# =========================================================

V_PI = 5.0

voltage = np.linspace(0, 2*V_PI, 500)

voltage_phase = voltage_to_phase(voltage, V_PI)

voltage_power = simulate_mzi(voltage_phase)

plt.figure(figsize=(9, 5))
plt.plot(voltage/V_PI, voltage_power[:, 0], label="Output 1")
plt.plot(voltage/V_PI, voltage_power[:, 1], label="Output 2")

plt.xlabel("Applied voltage / Vπ")
plt.ylabel("Normalized optical power")
plt.title("Voltage-Controlled MZI Response")
plt.grid()
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT / "voltage_response.png", dpi=300)


# =========================================================
# 9. EXPERIMENT C: SPECTRAL RESPONSE
# =========================================================

lambda_ref = 1550e-9
n_eff = 2.4
n_group = 4.2
delta_L = 20e-6

wavelength = np.linspace(1500e-9, 1600e-9, 2000)

spectral_phase = wavelength_to_phase(
    wavelength,
    n_eff,
    n_group,
    delta_L,
    lambda_ref
)

spectral_power = simulate_mzi(spectral_phase)

plt.figure(figsize=(9, 5))

plt.plot(wavelength*1e9, spectral_power[:, 0])

plt.xlabel("Wavelength (nm)")
plt.ylabel("Normalized transmission")
plt.title("MZI Spectral Response")
plt.grid()
plt.tight_layout()
plt.savefig(OUTPUT / "spectral_response.png", dpi=300)

# Save spectral data
np.savetxt(
    OUTPUT / "spectral_data.csv",
    np.column_stack((wavelength*1e9, spectral_power)),
    delimiter=",",
    header="Wavelength_nm,Output1,Output2",
    comments=""
)


# =========================================================
# 10. EXPERIMENT D: COUPLER IMPERFECTIONS
# =========================================================

coupling_ratios = [0.4, 0.45, 0.5, 0.55, 0.6]

plt.figure(figsize=(9, 5))

for kappa in coupling_ratios:

    result = simulate_mzi(
        phase,
        kappa1=kappa,
        kappa2=kappa
    )

    plt.plot(
        phase/np.pi,
        result[:, 0],
        label=f"kappa = {kappa}"
    )

plt.xlabel("Differential phase (π radians)")
plt.ylabel("Normalized transmission")
plt.title("Effect of Coupler Imbalance")
plt.grid()
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT / "coupler_sensitivity.png", dpi=300)


# =========================================================
# 11. EXPERIMENT E: PROPAGATION LOSS
# =========================================================

lossy_power = simulate_mzi(
    phase,
    loss_arm1_db=1.0,
    loss_arm2_db=3.0
)

plt.figure(figsize=(9, 5))

plt.plot(phase/np.pi, P1, label="Ideal MZI")
plt.plot(
    phase/np.pi,
    lossy_power[:, 0],
    label="Lossy MZI"
)

plt.xlabel("Differential phase (π radians)")
plt.ylabel("Output power")
plt.title("Effect of Propagation Loss")
plt.grid()
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT / "loss_analysis.png", dpi=300)


# =========================================================
# 12. PERFORMANCE REPORT
# =========================================================

ideal_metrics = calculate_metrics(P1)

lossy_metrics = calculate_metrics(lossy_power[:, 0])

fsr = calculate_fsr(
    lambda_ref,
    n_group,
    delta_L
)

report = []

report.append("MACH-ZEHNDER INTERFEROMETER SIMULATION")
report.append("=" * 50)

report.append("\nIDEAL DEVICE")
for key, value in ideal_metrics.items():
    report.append(f"{key}: {value:.6f}")

report.append("\nLOSSY DEVICE")
for key, value in lossy_metrics.items():
    report.append(f"{key}: {value:.6f}")

report.append(f"\nTheoretical FSR: {fsr*1e9:.4f} nm")

report.append("\nMODEL PARAMETERS")
report.append(f"Effective index: {n_eff}")
report.append(f"Group index: {n_group}")
report.append(f"Path difference: {delta_L*1e6} um")
report.append(f"Reference wavelength: {lambda_ref*1e9} nm")
report.append(f"Voltage Vpi: {V_PI} V")

# Numerical validation
analytical = (1 - np.cos(phase))/2

validation_error = np.max(np.abs(P1 - analytical))
energy_error = np.max(np.abs(P1 + P2 - 1.0))

report.append("\nNUMERICAL VALIDATION")
report.append(f"Analytical error: {validation_error:.3e}")
report.append(f"Energy conservation error: {energy_error:.3e}")

assert validation_error < 1e-10
assert energy_error < 1e-10

report.append("\nAll ideal MZI tests passed.")

report_text = "\n".join(report)

print(report_text)

with open(OUTPUT / "performance_report.txt", "w") as file:
    file.write(report_text)

print("\nAll simulation outputs saved in results/")

plt.show()

