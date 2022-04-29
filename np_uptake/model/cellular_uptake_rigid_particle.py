import argparse
import pickle
import time
from functools import lru_cache
from math import exp, pi, sqrt, tan

import numpy as np
import scipy.integrate
import scipy.signal

import np_uptake.figures.utils as fiu
import np_uptake.model.system_definition as sysdef


class EnergyComputation:
    def compute_bending_energy_zone_3(self, f, particle, s_list_region3):
        """
        Args:
            f: wrapping degree
            particle: Parameters class
        Returns:
            float - the variation of the bending energy in the region 3 (bending of the membrane)
            between the state at wrapping f and the initial state: E(f) - E(0)
        """
        dpsi3_list_region3 = particle.get_squared_dpsi_region3(f)
        energy = scipy.integrate.simps(dpsi3_list_region3, s_list_region3[0:-1])
        adimensionalized_energy = 0.25 * particle.effective_radius * energy
        return adimensionalized_energy

    def compute_bending_energy_zone_2r(self, f, particle, mechanics, wrapping, membrane):
        """
        Args:
            f: wrapping degree
            particle: Parameters class
        Returns:
            float - the variation of the bending energy in the region 2d (free membrane)
            between the state at wrapping f and the initial state: E(f) - E(0)
        """
        a = particle.get_alpha_angle(f)
        t = tan(0.25 * a)
        t2 = t ** 2
        b = sqrt(mechanics.sigma_bar / 2)
        energy = (
            -8
            * b
            / particle.effective_radius
            * t2
            * ((1 / (t2 + exp(2 * b * membrane.l2 / particle.effective_radius))) - (1 / (t2 + 1)))
        )
        adimensionalized_energy = 0.25 * particle.effective_radius * energy
        return adimensionalized_energy

    @lru_cache(maxsize=10)
    def compute_bending_energy_zone_2l(self, f, particle, mechanics, wrapping, membrane):
        adimensionalized_energy_2r = self.compute_bending_energy_zone_2r(f, particle, mechanics, wrapping, membrane)
        adimensionalized_energy_2l = adimensionalized_energy_2r
        return adimensionalized_energy_2l

    @lru_cache(maxsize=10)
    def sum_adimensional_bending_energy_contributions(
        self,
        adimensional_bending_energy_2r,
        adimensional_bending_energy_2l,
        adimensional_bending_energy_3,
    ):
        total_adimensional_bending_energy = (
            adimensional_bending_energy_2r + adimensional_bending_energy_2l + adimensional_bending_energy_3
        )
        return total_adimensional_bending_energy

    @lru_cache(maxsize=10)
    def compute_adimensional_adhesion_energy(self, f, particle, mechanics, wrapping, l3):
        adimensional_adhesion_energy = -mechanics.gamma_bar(f, wrapping) * l3 * 0.25 / particle.effective_radius
        return adimensional_adhesion_energy

    def compute_adimensional_tension_energy(self, f, particle, mechanics, wrapping, membrane, l3, r_2r, r_2l):
        adimensional_tension_energy = (
            mechanics.sigma_bar * (l3 + 2 * membrane.l2 - (r_2r[-1] - r_2l[-1])) * 0.25 / particle.effective_radius
        )
        return adimensional_tension_energy

    @lru_cache(maxsize=10)
    def sum_adimensional_energy_contributions(
        self, total_adimensional_bending_energy, adimensional_adhesion_energy, adimensional_tension_energy
    ):
        total_adimensional_energy = (
            total_adimensional_bending_energy + adimensional_adhesion_energy + adimensional_tension_energy
        )
        return total_adimensional_energy

    @lru_cache(maxsize=10)
    def compute_total_adimensional_energy_for_a_given_wrapping_degree(self, f, particle, mechanics, wrapping, membrane):
        _, _, _, _, s_list_region3, l3, _, _ = particle.define_particle_geometry_variables(f)
        r_2r, _, r_2l, _ = membrane.compute_r2r_r2l_z2r_z2l_from_analytic_expression(f, particle, mechanics, wrapping)
        adimensional_bending_energy_2r = self.compute_bending_energy_zone_2r(f, particle, mechanics, wrapping, membrane)

        adimensional_bending_energy_2l = self.compute_bending_energy_zone_2l(f, particle, mechanics, wrapping, membrane)

        adimensional_bending_energy_3 = self.compute_bending_energy_zone_3(f, particle, s_list_region3)

        total_adimensional_bending_energy = self.sum_adimensional_bending_energy_contributions(
            adimensional_bending_energy_2r, adimensional_bending_energy_2l, adimensional_bending_energy_3
        )
        adimensional_adhesion_energy = self.compute_adimensional_adhesion_energy(f, particle, mechanics, wrapping, l3)
        adimensional_tension_energy = self.compute_adimensional_tension_energy(
            f, particle, mechanics, wrapping, membrane, l3, r_2r, r_2l
        )

        total_adimensional_energy = self.sum_adimensional_energy_contributions(
            total_adimensional_bending_energy, adimensional_adhesion_energy, adimensional_tension_energy
        )

        return total_adimensional_energy

    def compute_total_adimensional_energy_during_wrapping(self, particle, mechanics, wrapping, membrane):

        adimensional_total_energy_variation_list = np.zeros_like(wrapping.wrapping_list)
        energy_variation_computation_time_list = np.zeros_like(adimensional_total_energy_variation_list)

        for i in range(len(wrapping.wrapping_list)):
            f = wrapping.wrapping_list[i]
            start = time.process_time()
            total_adimensional_energy = self.compute_total_adimensional_energy_for_a_given_wrapping_degree(
                f, particle, mechanics, wrapping, membrane
            )

            end = time.process_time()
            energy_variation_computation_time = end - start
            adimensional_total_energy_variation_list[i] = total_adimensional_energy
            energy_variation_computation_time_list[i] = energy_variation_computation_time
        return adimensional_total_energy_variation_list, energy_variation_computation_time_list


def plot_energy(
    particle, mechanics, membrane, wrapping, energy_computation, createfigure, fonts, xticks, xticklabels, savefigure
):
    """
    Plots the evolution of the adimensional variation of energy_computation during wrapping

    Parameters:
        ----------
        particle: class
            model.system_definition.ParticleGeometry class
        mechanics: class
            model.system_definition.MechanicalProperties_Adaptation class
        membrane: class
            model.system_definition.MembraneGeometry class
        wrapping: class
            model.system_definition.Wrapping class
        createfigure: class
            figures.utils.CreateFigure class
        fonts: class
            figures.utils.Fonts class
        xticks: class
            figures.utils.XTicks class
        xticklabels: class
            figures.utils.XTickLabels class
        savefigure: class
            figures.utils.SaveFigure class

    Returns:
        -------
        None
    """

    energy_list, _ = energy_computation.compute_total_adimensional_energy_during_wrapping(
        particle, mechanics, wrapping, membrane
    )
    fig = createfigure.square_figure_7(pixels=360)
    ax = fig.gca()
    ax.plot(
        wrapping.wrapping_list,
        energy_list,
        "-k",
        label=r"$\overline{r} = $"
        + str(np.round(particle.r_bar, 2))
        + r" ; $\overline{\gamma}_0 = $"
        + str(mechanics.gamma_bar_0)
        + r" ; $\overline{\sigma} = $"
        + str(mechanics.sigma_bar),
        linewidth=4,
    )
    ax.set_xticks(xticks.energy_plots())
    ax.set_xticklabels(
        xticklabels.energy_plots(),
        font=fonts.serif(),
        fontsize=fonts.axis_legend_size(),
    )
    ax.set_yticks([-15, -10, -5, 0, 5])
    ax.set_yticklabels(
        ["-15", "-10", "-5", "0", "5"],
        font=fonts.serif(),
        fontsize=fonts.axis_legend_size(),
    )
    ax.legend(prop=fonts.serif(), loc="lower left", framealpha=0.9)
    ax.set_xlabel(r"$f$ [ - ]", font=fonts.serif(), fontsize=fonts.axis_label_size())
    ax.set_ylabel(r"$\overline{\Delta E}$ [ - ]", font=fonts.serif(), fontsize=fonts.axis_label_size())

    savefigure.save_as_png(fig, "DeltaE_vs_f")


def identify_wrapping_phase(particle, mechanics, membrane, wrapping, energy_computation):
    pickle.dumps(energy_computation.compute_total_adimensional_energy_during_wrapping)
    pickle.dumps(membrane.compute_r2r_r2l_z2r_z2l_from_analytic_expression)
    energy_list, time_list = energy_computation.compute_total_adimensional_energy_during_wrapping(
        particle, mechanics, wrapping, membrane
    )
    min_energy_index_list = scipy.signal.argrelmin(energy_list)
    min_energy_index_list = min_energy_index_list[0]
    # check if the minimum is reached for wrapping.wrapping_list[-1]
    if energy_list[-1] < energy_list[-2]:
        min_energy_index_list = np.concatenate((min_energy_index_list, np.array([-1])), axis=None)

    # check if the minimum is reached for wrapping.wrapping_list[0]
    if energy_list[0] < energy_list[1]:
        min_energy_index_list = np.concatenate((np.array(wrapping.wrapping_list[0]), min_energy_index_list), axis=None)
    if len(min_energy_index_list) == 0:
        min_energy_index_list = [0]
    min_energy_list = [energy_list[int(k)] for k in min_energy_index_list]
    f_min_energy_list = [wrapping.wrapping_list[int(k)] for k in min_energy_index_list]
    # managing possible scipy.signal.argrelextrema outuput types
    if type(min_energy_list[0]) == np.ndarray:
        min_energy_list = min_energy_list[0]
        f_min_energy_list = f_min_energy_list[0]

    """
    Identifies the wrapping phase following the process introduced in [1]

    Parameters:
        ----------
        particle: class
            model.system_definition.ParticleGeometry object
        mechanics: class
            model.system_definition.MechanicalProperties_Adaptation object
        membrane: class
            model.system_definition.MembraneGeometry object

    Returns:
        -------
        wrapping_phase_number: float
            phase number (1, 2 or 3)
        wrapping_phase: str
            the wrapping phase as an intelligible string
    """

    f_eq = f_min_energy_list[0]
    wrapping_phase_number = 0
    wrapping_phase = "0"

    if f_eq < 0.2:  # check if wrapping phase is phase 1, according to [1]
        wrapping_phase_number = 1
        wrapping_phase = "no wrapping"
    else:
        r2r, _, r2l, _ = membrane.compute_r2r_r2l_z2r_z2l_from_analytic_expression(f_eq, particle, mechanics, wrapping)
        intersection_membrane = min(r2r) - max(r2l)
        wrapping_phase_number = 3 if intersection_membrane < 0 else 2
        wrapping_phase = "full wrapping" if intersection_membrane < 0 else "partial wrapping"
    return (f_eq, wrapping_phase_number, wrapping_phase, energy_list, time_list)


def parse_arguments():
    """
    Parses arguments to run the code in terminal

    Parameters:
        ----------
        None

    Returns:
        -------
        args: class
            #TODO complete here
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-g0",
        "--gamma_bar_0",
        required=False,
        default=10.0,
        type=float,
        help="initial adimensional lineic adhesion bt membrane and NP. Default value = 10.",
    )
    parser.add_argument(
        "-gr",
        "--gamma_bar_r",
        required=False,
        default=1.0,
        type=float,
        help="ratio of adimensional lineic adhesion bt membrane and NP. Default value = 1.",
    )
    parser.add_argument(
        "-gfs",
        "--gamma_bar_fs",
        required=False,
        default=0.0,
        type=float,
        help="adimensional lineic adhesion between the membrane and the particle, inflexion point. Default value = 0.",
    )
    parser.add_argument(
        "-glambda",
        "--gamma_bar_lambda",
        required=False,
        default=10.0,
        type=float,
        help="adimensional lineic adhesion between the membrane and the particle, smoothness. Default value = 10.",
    )
    parser.add_argument(
        "-s0",
        "--sigma_bar_0",
        required=False,
        default=2.0,
        type=float,
        help="adimensional membrane tension, value before wrapping. Default value = 2.",
    )
    parser.add_argument(
        "-sr",
        "--sigma_bar_r",
        required=False,
        default=1.0,
        type=float,
        help="adimensional membrane tension, ratio between final and initial value. Default value = 1.",
    )
    parser.add_argument(
        "-sfs",
        "--sigma_bar_fs",
        required=False,
        default=0.0,
        type=float,
        help="adimensional membrane tension, inflexion point. Default value = 0.",
    )
    parser.add_argument(
        "-slambda",
        "--sigma_bar_lambda",
        required=False,
        default=-10.0,
        type=float,
        help="adimensional membrane tension, smoothness. Default value = -10.",
    )
    parser.add_argument(
        "-r", "--r_bar", required=False, default=1.0, type=float, help="particle aspect ratio. Default value = 1."
    )
    parser.add_argument(
        "-p",
        "--particle_perimeter",
        required=False,
        default=2 * pi,
        type=float,
        help="particle perimeter. Default value = 2pi.",
    )

    args = parser.parse_args()
    return args


def profiler(particle, mechanics, membrane, wrapping, energy_computation):
    import cProfile
    import pstats

    with cProfile.Profile() as pr:
        energy_computation.compute_total_adimensional_energy_during_wrapping(particle, mechanics, wrapping, membrane)

    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()
    stats.dump_stats(filename="needs_profiling_prof")


if __name__ == "__main__":
    args = parse_arguments()
    createfigure = fiu.CreateFigure()
    fonts = fiu.Fonts()
    savefigure = fiu.SaveFigure()
    xticks = fiu.XTicks()
    xticklabels = fiu.XTickLabels()
    particle = sysdef.ParticleGeometry(r_bar=1.94, particle_perimeter=2 * pi, sampling_points_circle=300)

    mechanics = sysdef.MechanicalProperties_Adaptation(
        testcase="test-classimplementation",
        gamma_bar_r=args.gamma_bar_r,
        gamma_bar_fs=args.gamma_bar_fs,
        gamma_bar_lambda=args.gamma_bar_lambda,
        gamma_bar_0=args.gamma_bar_0,
        sigma_bar=args.sigma_bar_0,
    )

    membrane = sysdef.MembraneGeometry(particle, sampling_points_membrane=100)

    wrapping = sysdef.Wrapping(wrapping_list=np.arange(0.03, 0.97, 0.003125))

    energy_computation = EnergyComputation()

    plot_energy(
        particle,
        mechanics,
        membrane,
        wrapping,
        energy_computation,
        createfigure,
        fonts,
        xticks,
        xticklabels,
        savefigure,
    )
    f_eq, wrapping_phase_number, wrapping_phase, energy_list, time_list = identify_wrapping_phase(
        particle, mechanics, membrane, wrapping, energy_computation
    )
    print("wrapping degree at equilibrium = ", np.round(f_eq, 2))
    print("wrapping phase at equilibrium: ", wrapping_phase)
