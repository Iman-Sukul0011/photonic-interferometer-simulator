# Mathematical Model of the Mach-Zehnder Interferometer

## 1. Directional Coupler

The optical coupler is represented by:

C = [[sqrt(1-kappa), i*sqrt(kappa)],
     [i*sqrt(kappa), sqrt(1-kappa)]]

where kappa is the power coupling coefficient.

## 2. Phase Propagation

The differential phase is:

Delta_phi = phi_1 - phi_2

For symmetric phase modulation:

phi_1 = Delta_phi/2
phi_2 = -Delta_phi/2

## 3. MZI Transfer Matrix

E_out = C2 * P * C1 * E_in

where P is the diagonal phase propagation matrix.

## 4. Voltage Modulation

Delta_phi = pi * V / V_pi

This assumes a linear phase-voltage relationship.

## 5. Spectral Response

The phase difference due to path-length mismatch is:

Delta_phi(lambda) = 2*pi*n_eff(lambda)*Delta_L/lambda

The effective index uses a first-order dispersion approximation.

## 6. Free Spectral Range

FSR approximately equals:

FSR = lambda^2 / (n_g * Delta_L)

This is the local wavelength-domain approximation.

## 7. Device Metrics

Extinction Ratio:

ER = 10*log10(P_max/P_min)

Insertion Loss:

IL = -10*log10(P_max/P_input)

## 8. Model Limitations

This is a lumped transfer-matrix model, not a full electromagnetic
simulation.

It does not include:
- Higher-order waveguide dispersion.
- Wavelength-dependent coupler response.
- Temperature-dependent refractive index.
- Fabrication tolerances.
- Polarization-dependent behaviour.
- Nonlinear optical effects.
