"""
Step 0/1 harness: coupled (C_i, gamma) dynamics.

    dC_i/dt = alpha*F * C_i^gamma / sum_j C_j^gamma - beta*C_i
    dgamma/dt = kappa * (gamma_target(sigma_F) - gamma)

Step 1 here: kappa=0 (gamma fixed) must reproduce the L1 eigenvalue curve
beta*(gamma-1) to ~3e-4, same protocol as the prior session's sim1.py.
"""
import numpy as np

def measure_eigenvalue(gamma, N=20, beta=1.0, alpha=1.0, F=1.0,
                        eps0=1e-5, T=None, dt=1e-3, steps=6000):
    """Perturb the uniform fixed point, measure exponential growth/decay
    rate of the perturbation under the (kappa=0) dynamics."""
    rng = np.random.default_rng(0)
    x_uniform = np.ones(N) / N
    direction = rng.normal(size=N)
    direction -= direction.mean()          # stay on the simplex tangent
    direction /= np.linalg.norm(direction)

    x = x_uniform + eps0 * direction
    x = np.clip(x, 1e-12, None)
    x /= x.sum()

    norms = []
    for _ in range(steps):
        xg = x ** gamma
        dx = beta * (xg / xg.sum() - x)
        x = x + dt * dx
        x = np.clip(x, 1e-12, None)
        x /= x.sum()
        norms.append(np.linalg.norm(x - x_uniform))

    norms = np.array(norms)
    t = np.arange(1, steps + 1) * dt
    # fit log|eps(t)| = log(eps0) + lambda*t over the early (linear) regime
    # before nonlinear saturation/clipping distorts it
    mask = (norms > 1e-9) & (norms < 10 * eps0)
    if mask.sum() < 10:
        mask = norms > 1e-10
    log_n = np.log(norms[mask])
    tt = t[mask]
    A = np.vstack([tt, np.ones_like(tt)]).T
    lam, _ = np.linalg.lstsq(A, log_n, rcond=None)[0]
    return lam


if __name__ == "__main__":
    beta = 1.0
    gammas = np.linspace(0.4, 1.8, 15)
    print(f"{'gamma':>6} {'predicted':>12} {'measured':>12} {'abs err':>10}")
    max_err = 0.0
    for g in gammas:
        predicted = beta * (g - 1.0)
        measured = measure_eigenvalue(g, beta=beta)
        err = abs(predicted - measured)
        max_err = max(max_err, err)
        print(f"{g:6.3f} {predicted:12.5f} {measured:12.5f} {err:10.2e}")
    print(f"\nmax abs error over sweep: {max_err:.2e}")
