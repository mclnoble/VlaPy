import numpy as np
from vlapy.core import field, vlasov


def initialize(nx, nv, vmax=6.0):
    """
    Initializes a Maxwell-Boltzmann distribution

    TODO: temperature and density pertubations

    :param nx:
    :param nv:
    :param vmax:
    :return:
    """

    f = np.zeros([nx, nv], dtype=np.float16)
    dv = 2.0 * vmax / nv
    vax = np.linspace(-vmax + dv / 2.0, vmax - dv / 2.0, nv)

    for ix in range(nx):
        f[ix,] = np.exp(-(vax ** 2.0) / 2.0)

    # normalize
    f = f / np.sum(f[0,]) / dv

    return f


def full_leapfrog_ps_step(f, x, kx, v, kv, dv, t, dt, e, driver_function):
    """
    Takes a step forward in time for f and e

    Uses leapfrog scheme
    1 - spatial advection for 0.5 dt

    2a - field solve
    2b - velocity advection for dt

    3 - spatial advection for 0.5 dt

    :param f:
    :param x:
    :param kx:
    :param v:
    :param kv:
    :param dv:
    :param t:
    :param dt:
    :param e:
    :param driver_function:
    :return:
    """
    f = vlasov.update_velocity_adv_spectral(f, kv, e, 0.5 * dt)
    f = vlasov.update_spatial_adv_spectral(f, kx, v, dt)
    e = field.get_total_electric_field(driver_function(x, t + dt), f=f, dv=dv, kx=kx)
    f = vlasov.update_velocity_adv_spectral(f, kv, e, 0.5 * dt)

    return e, f


def full_PEFRL_ps_step(f, x, kx, v, kv, dv, t, dt, e, driver_function):
    """
    Takes a step forward in time for f and e using the
    Performance-Extended Forest-Ruth-Like algorithm

    This is a 4th order symplectic integrator.
    http://physics.ucsc.edu/~peter/242/leapfrog.pdf

    :param f:

    :param x:
    :param kx:
    :param dx:

    :param v:
    :param kv:
    :param dv:

    :param t:
    :param dt:

    :param e:

    :param driver_function:
    :return:
    """
    xsi = 0.1786178958448091
    lambd = -0.2123418310626054
    chi = -0.6626458266981849e-1

    dt1 = xsi * dt
    dt2 = chi * dt
    dt3 = (1.0 - 2.0 * (chi + xsi)) * dt
    dt4 = dt2
    dt5 = dt1

    # x1
    f = vlasov.update_spatial_adv_spectral(f, kx, v, dt1)
    e = field.get_total_electric_field(driver_function(x, t + dt1), f=f, dv=dv, kx=kx)

    # v1
    f = vlasov.update_velocity_adv_spectral(f, kv, e, 0.5 * (1.0 - 2.0 * lambd) * dt)

    # x2
    f = vlasov.update_spatial_adv_spectral(f, kx, v, dt2)
    e = field.get_total_electric_field(
        driver_function(x, t + dt1 + dt2), f=f, dv=dv, kx=kx
    )

    # v2
    f = vlasov.update_velocity_adv_spectral(f, kv, e, lambd * dt)

    # x3
    f = vlasov.update_spatial_adv_spectral(f, kx, v, dt3)
    e = field.get_total_electric_field(
        driver_function(x, t + dt1 + dt2 + dt3), f=f, dv=dv, kx=kx
    )

    # v3
    f = vlasov.update_velocity_adv_spectral(f, kv, e, lambd * dt)

    # x4
    f = vlasov.update_spatial_adv_spectral(f, kx, v, dt4)
    e = field.get_total_electric_field(
        driver_function(x, t + dt1 + dt2 + dt3 + dt4), f=f, dv=dv, kx=kx
    )

    # v4
    f = vlasov.update_velocity_adv_spectral(f, kv, e, 0.5 * (1.0 - 2.0 * lambd) * dt)

    # x5
    f = vlasov.update_spatial_adv_spectral(f, kx, v, dt5)
    e = field.get_total_electric_field(
        driver_function(x, t + dt1 + dt2 + dt3 + dt4 + dt5), f=f, dv=dv, kx=kx
    )

    return e, f
