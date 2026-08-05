"""
L6 (this session): generalized critical-point law for an arbitrary smooth
routing kernel f, not just the power law f(x) = x^gamma.

    dx_i/dt = beta * ( f(x_i) / sum_j f(x_j) - x_i )

Linearizing about the uniform state x* = 1/N gives eigenvalue

    lambda = beta * ( x* f'(x*) / f(x*) - 1 )

i.e. the control parameter is the LOCAL ELASTICITY of f at the uniform
point, gamma_eff(N) = x* f'(x*) / f(x*), not gamma itself except when f is
literally a power law (for which elasticity is constant = gamma at every
x, which is exactly why L1/L3 found an N-INVARIANT critical point at
gamma=1: power laws are the unique kernel family whose elasticity doesn't
depend on x*, hence not on N).

For a general kernel, gamma_eff depends on x*=1/N, so the critical
parameter setting gamma_eff=1 generally DOES depend on N. Example here:
exponential/softmax kernel f(x) = exp(x/T) (a plausible model for
diode-OR / winner-take-most competition between energy sources sharing a
bus, where T is inverse arbitration sharpness) has elasticity x*/T =
1/(N*T), so the critical temperature is T* = 1/N -- scales inversely with
network size, not N-invariant.

This matters for Step 4 (domain mapping): a candidate energy-harnessing
domain whose native allocation law is exponential/softmax rather than a
true power law will NOT show the clean, size-independent phase transition
that makes the abstract model's claim ("one dimensionless parameter
controls the transition, independent of domain size") interesting. See
DOMAIN_MAPPING.md.
"""
import numpy as np


def measure_eigenvalue_general(f, N=20, beta=1.0, eps0=1e-5, dt=1e-3,
                                steps=6000, seed=0):
    rng = np.random.default_rng(seed)
    x_uniform = np.ones(N) / N
    direction = rng.normal(size=N)
    direction -= direction.mean()
    direction /= np.linalg.norm(direction)
    x = x_uniform + eps0 * direction
    x = np.clip(x, 1e-12, None); x /= x.sum()
    norms = []
    for _ in range(steps):
        fx = f(x)
        dx = beta * (fx / fx.sum() - x)
        x = x + dt * dx
        x = np.clip(x, 1e-12, None); x /= x.sum()
        norms.append(np.linalg.norm(x - x_uniform))
    norms = np.array(norms)
    t = np.arange(1, steps + 1) * dt
    mask = (norms > 1e-9) & (norms < 10 * eps0)
    log_n = np.log(norms[mask]); tt = t[mask]
    A = np.vstack([tt, np.ones_like(tt)]).T
    lam, _ = np.linalg.lstsq(A, log_n, rcond=None)[0]
    return lam


if __name__ == "__main__":
    beta = 1.0
    print("power-law kernel f(x)=x^gamma: critical point at gamma=1, N-invariant (regression check)")
    for N in [10, 20, 40]:
        lam = measure_eigenvalue_general(lambda x: x ** 1.0, N=N, beta=beta)
        print(f"  N={N:3d}  gamma=1.0  measured eigenvalue={lam:8.5f} (predicted 0)")

    print("\nexponential/softmax kernel f(x)=exp(x/T): critical T* = 1/N, NOT N-invariant")
    for N in [10, 20, 40]:
        Tstar = 1.0 / N
        for T in [0.7 * Tstar, Tstar, 1.3 * Tstar]:
            f = lambda x, T=T: np.exp(x / T)
            predicted = beta * ((1.0 / N) / T - 1.0)
            measured = measure_eigenvalue_general(f, N=N, beta=beta)
            print(f"  N={N:3d}  T={T:.4f} (T*={Tstar:.4f})  "
                  f"predicted={predicted:8.4f}  measured={measured:8.4f}  "
                  f"err={abs(predicted-measured):.2e}")
