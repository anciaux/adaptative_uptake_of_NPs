import openturns as ot
import openturns.viewer as viewer

ot.Log.Show(ot.Log.NONE)


import np_uptake.metamodel_implementation.utils as miu
from np_uptake.figures.utils import CreateFigure, Fonts, SaveFigure
from np_uptake.metamodel_implementation.metamodel_validation import MetamodelPostTreatment


class Distribution:
    def __init__(self):
        """
        Constructs all the necessary attributes for the Distribution object.

        Parameters:
            ----------
            None

        Returns:
            -------
            None
        """

        self.gamma_bar_r_min = 1
        self.gamma_bar_r_max = 6
        self.gamma_bar_fs_min = -0.45
        self.gamma_bar_fs_max = 0.45
        self.gamma_bar_lambda_min = 49.99
        self.gamma_bar_lambda_max = 50.01

    def uniform(self):
        """
        creates a uniform distribution of the 3 input parameters

        Parameters:
            ----------
            None

        Returns:
            -------
            distribution: ot class
                uniform distribution of the 3 input parameters, computed wth Openturns.
                gamma_bar_lambda and sigma_bar_lambda could have been computed as constant values
                but we chose to generate them as uniform distribution with close bounds to match
                the architecture of the openturns library

        """
        distribution = ot.ComposedDistribution(
            [
                ot.Uniform(self.gamma_bar_r_min, self.gamma_bar_r_max),
                ot.Uniform(self.gamma_bar_fs_min, self.gamma_bar_fs_max),
                ot.Uniform(self.gamma_bar_lambda_min, self.gamma_bar_lambda_max),
            ]
        )
        return distribution


# Saltelli#
def compute_sensitivity_algo_Saltelli(distribution, metamodel, sensitivity_experiment_size):
    """
    computes the sensitivity algorithms computed after the Saltelli method

    Parameters:
        ----------
        distribution: class
            class that defines the distribution of the input parameters whose influence is tested
            in the sensitivity analysis
        metamodel: ot class
            metamodel (Kriging) computed in the metamodel_creation.py script and stored in a .pkl
            file
        sensitivity_experiment_size: float (int)
            amount of estimations of the metamodel to evaluate the sensitivity

    Returns:
        -------
        sensitivityAnalysis: ot class
            sensitivity algorithm computed with the openturns class

    """
    uniform_distribution = distribution.uniform()
    myExperiment = ot.LowDiscrepancyExperiment(
        ot.SobolSequence(), uniform_distribution, sensitivity_experiment_size, True
    )
    sensitivityAnalysis = ot.SaltelliSensitivityAlgorithm(myExperiment, metamodel, True)
    return sensitivityAnalysis


def compute_and_export_sensitivity_algo_Saltelli(
    type_of_metamodel,
    training_amount,
    distribution,
    sensitivity_experiment_size,
    type_of_Sobol_sensitivity_implementation="Saltelli",
):
    """
    computes the sensitivity algorithms computed after the Saltelli method and exports it to a .pkl
    file

    Parameters:
        ----------
        type_of_metamodel: str
            type of metamodel that has been computed. Possible value: "Kriging"
        training_amount: float
            proportion (between 0 and 1) of the initial data used for training (the remaining data
            are used for testing)
        distribution: class
            class that defines the distribution of the input parameters whose influence is tested
            in the sensitivity analysis
        sensitivity_experiment_size: float (int)
            amount of estimations of the metamodel to evaluate the sensitivity
        type_of_Sobol_sensitivity_implementation: str
            type of Sobol algorithm. Used only to generate the name of the .pkl file in which the
            sensitivity algorithm is stored.

    Returns:
        -------
        None

    """
    complete_pkl_filename_metamodel = miu.create_pkl_name(type_of_metamodel, training_amount)
    _, results_from_algo = miu.extract_metamodel_and_data_from_pkl(complete_pkl_filename_metamodel)
    metamodel = metamodelposttreatment.get_metamodel_from_results_algo(results_from_algo)
    sensitivity_algo_Saltelli = compute_sensitivity_algo_Saltelli(distribution, metamodel, sensitivity_experiment_size)
    complete_pkl_filename_sensitivy_algo = miu.create_pkl_name_sensitivityalgo(
        type_of_metamodel, training_amount, sensitivity_experiment_size, type_of_Sobol_sensitivity_implementation
    )
    miu.export_sensitivity_algo_to_pkl(sensitivity_algo_Saltelli, complete_pkl_filename_sensitivy_algo)


# Jansen#
def compute_sensitivity_algo_Jansen(distribution, metamodel, sensitivity_experiment_size):
    """
    computes the sensitivity algorithms computed after the Jansen method

    Parameters:
        ----------
        distribution: class
            class that defines the distribution of the input parameters whose influence is tested
            in the sensitivity analysis
        metamodel: ot class
            metamodel (Kriging) computed in the metamodel_creation.py script and stored in a .pkl
            file
        sensitivity_experiment_size: float (int)
            amount of estimations of the metamodel to evaluate the sensitivity

    Returns:
        -------
        sensitivityAnalysis: ot class
            sensitivity algorithm computed with the openturns class

    """
    uniform_distribution = distribution.uniform()
    myExperiment = ot.LowDiscrepancyExperiment(
        ot.SobolSequence(), uniform_distribution, sensitivity_experiment_size, True
    )
    sensitivityAnalysis = ot.JansenSensitivityAlgorithm(myExperiment, metamodel, True)
    return sensitivityAnalysis


def compute_and_export_sensitivity_algo_Jansen(
    type_of_metamodel,
    training_amount,
    distribution,
    sensitivity_experiment_size,
    type_of_Sobol_sensitivity_implementation="Jansen",
):
    """
    computes the sensitivity algorithms computed after the Jansen method and exports it to a .pkl
    file

    Parameters:
        ----------
        type_of_metamodel: str
            type of metamodel that has been computed. Possible value: "Kriging"
        training_amount: float
            proportion (between 0 and 1) of the initial data used for training (the remaining data
            are used for testing)
        distribution: class
            class that defines the distribution of the input parameters whose influence is tested
            in the sensitivity analysis
        sensitivity_experiment_size: float (int)
            amount of estimations of the metamodel to evaluate the sensitivity
        type_of_Sobol_sensitivity_implementation: str
            type of Sobol algorithm. Used only to generate the name of the .pkl file in which the
            sensitivity algorithm is stored.

    Returns:
        -------
        None

    """

    complete_pkl_filename_metamodel = miu.create_pkl_name(type_of_metamodel, training_amount)
    _, results_from_algo = miu.extract_metamodel_and_data_from_pkl(complete_pkl_filename_metamodel)
    metamodel = metamodelposttreatment.get_metamodel_from_results_algo(results_from_algo)
    sensitivity_algo_Jansen = compute_sensitivity_algo_Jansen(distribution, metamodel, sensitivity_experiment_size)
    complete_pkl_filename_sensitivy_algo = miu.create_pkl_name_sensitivityalgo(
        type_of_metamodel, training_amount, sensitivity_experiment_size, type_of_Sobol_sensitivity_implementation
    )
    miu.export_sensitivity_algo_to_pkl(sensitivity_algo_Jansen, complete_pkl_filename_sensitivy_algo)


# MauntzKucherenko#
def compute_sensitivity_algo_MauntzKucherenko(distribution, metamodel, sensitivity_experiment_size):
    """
    computes the sensitivity algorithms computed after the MauntzKucherenko method

    Parameters:
        ----------
        distribution: class
            class that defines the distribution of the input parameters whose influence is tested
            in the sensitivity analysis
        metamodel: ot class
            metamodel (Kriging) computed in the metamodel_creation.py script and stored in a .pkl
            file
        sensitivity_experiment_size: float (int)
            amount of estimations of the metamodel to evaluate the sensitivity

    Returns:
        -------
        sensitivityAnalysis: ot class
            sensitivity algorithm computed with the openturns class

    """
    uniform_distribution = distribution.uniform()
    myExperiment = ot.LowDiscrepancyExperiment(
        ot.SobolSequence(), uniform_distribution, sensitivity_experiment_size, True
    )
    sensitivityAnalysis = ot.MauntzKucherenkoSensitivityAlgorithm(myExperiment, metamodel, True)
    return sensitivityAnalysis


def compute_and_export_sensitivity_algo_MauntzKucherenko(
    type_of_metamodel,
    training_amount,
    distribution,
    sensitivity_experiment_size,
    type_of_Sobol_sensitivity_implementation="MauntzKucherenko",
):
    """
    computes the sensitivity algorithms computed after the MauntzKucherenko method and exports it
    to a .pkl file

    Parameters:
        ----------
        type_of_metamodel: str
            type of metamodel that has been computed. Possible value: "Kriging"
        training_amount: float
            proportion (between 0 and 1) of the initial data used for training (the remaining data
            are used for testing)
        distribution: class
            class that defines the distribution of the input parameters whose influence is tested
            in the sensitivity analysis
        sensitivity_experiment_size: float (int)
            amount of estimations of the metamodel to evaluate the sensitivity
        type_of_Sobol_sensitivity_implementation: str
            type of Sobol algorithm. Used only to generate the name of the .pkl file in which the
            sensitivity algorithm is stored.

    Returns:
        -------
        None

    """

    complete_pkl_filename_metamodel = miu.create_pkl_name(type_of_metamodel, training_amount)
    _, results_from_algo = miu.extract_metamodel_and_data_from_pkl(complete_pkl_filename_metamodel)
    metamodel = metamodelposttreatment.get_metamodel_from_results_algo(results_from_algo)
    sensitivity_algo_MauntzKucherenko = compute_sensitivity_algo_MauntzKucherenko(
        distribution, metamodel, sensitivity_experiment_size
    )
    complete_pkl_filename_sensitivy_algo = miu.create_pkl_name_sensitivityalgo(
        type_of_metamodel, training_amount, sensitivity_experiment_size, type_of_Sobol_sensitivity_implementation
    )
    miu.export_sensitivity_algo_to_pkl(sensitivity_algo_MauntzKucherenko, complete_pkl_filename_sensitivy_algo)


# Martinez#
def compute_sensitivity_algo_Martinez(distribution, metamodel, sensitivity_experiment_size):
    """
    computes the sensitivity algorithms computed after the Martinez method

    Parameters:
        ----------
        distribution: class
            class that defines the distribution of the input parameters whose influence is tested
            in the sensitivity analysis
        metamodel: ot class
            metamodel (Kriging) computed in the metamodel_creation.py script and stored in a .pkl
            file
        sensitivity_experiment_size: float (int)
            amount of estimations of the metamodel to evaluate the sensitivity

    Returns:
        -------
        sensitivityAnalysis: ot class
            sensitivity algorithm computed with the openturns class

    """

    uniform_distribution = distribution.uniform()
    myExperiment = ot.LowDiscrepancyExperiment(
        ot.SobolSequence(), uniform_distribution, sensitivity_experiment_size, True
    )
    sensitivityAnalysis = ot.MartinezSensitivityAlgorithm(myExperiment, metamodel, True)
    return sensitivityAnalysis


def compute_and_export_sensitivity_algo_Martinez(
    type_of_metamodel,
    training_amount,
    distribution,
    sensitivity_experiment_size,
    type_of_Sobol_sensitivity_implementation="Martinez",
):
    """
    computes the sensitivity algorithms computed after the Martinez method and exports it to a .pkl
    file

    Parameters:
        ----------
        type_of_metamodel: str
            type of metamodel that has been computed. Possible value: "Kriging"
        training_amount: float
            proportion (between 0 and 1) of the initial data used for training (the remaining data
            are used for testing)
        distribution: class
            class that defines the distribution of the input parameters whose influence is tested
            in the sensitivity analysis
        sensitivity_experiment_size: float (int)
            amount of estimations of the metamodel to evaluate the sensitivity
        type_of_Sobol_sensitivity_implementation: str
            type of Sobol algorithm. Used only to generate the name of the .pkl file in which the
            sensitivity algorithm is stored.

    Returns:
        -------
        None

    """

    complete_pkl_filename_metamodel = miu.create_pkl_name(type_of_metamodel, training_amount)
    _, results_from_algo = miu.extract_metamodel_and_data_from_pkl(complete_pkl_filename_metamodel)
    metamodel = metamodelposttreatment.get_metamodel_from_results_algo(results_from_algo)
    sensitivity_algo_Martinez = compute_sensitivity_algo_Martinez(distribution, metamodel, sensitivity_experiment_size)
    complete_pkl_filename_sensitivy_algo = miu.create_pkl_name_sensitivityalgo(
        type_of_metamodel, training_amount, sensitivity_experiment_size, type_of_Sobol_sensitivity_implementation
    )
    miu.export_sensitivity_algo_to_pkl(sensitivity_algo_Martinez, complete_pkl_filename_sensitivy_algo)


# PLOTS#
def plot_results_sensitivity_analysis(
    type_of_metamodel,
    training_amount,
    sensitivity_experiment_size,
    type_of_Sobol_sensitivity_implementation,
    createfigure,
    pixels,
):
    """
    Plots the first and total Sobol indices

    Parameters:
        ----------
        type_of_metamodel: str
            type of metamodel that has been computed. Possible value: "Kriging"
        training_amount: float
            proportion (between 0 and 1) of the initial data used for training (the remaining data
            are used for testing)
        sensitivity_experiment_size: float (int)
            amount of estimations of the metamodel to evaluate the sensitivity
        type_of_Sobol_sensitivity_implementation: str
            type of Sobol algorithm. Used only to generate the name of the .pkl file in which the
            sensitivity algorithm is stored.
        createfigure: class
            class from the figures.utils.py script that provides a predefined figure layout
        colors: class
            class from the figures.utils.py script that provides a predefined set of colors
        pixels: str
            number of points per pixel in the figures Recommended: 360

    Returns:
        -------
        None

    """

    complete_pkl_filename_sensitivy_algo = miu.create_pkl_name_sensitivityalgo(
        type_of_metamodel, training_amount, sensitivity_experiment_size, type_of_Sobol_sensitivity_implementation
    )
    sensitivity_algo = miu.extract_sensitivity_algo_from_pkl(complete_pkl_filename_sensitivy_algo)
    first_order_indices_all_variables = sensitivity_algo.getFirstOrderIndices()
    total_order_indices_all_variables = sensitivity_algo.getTotalOrderIndices()
    first_order_indices_influent_variables = [first_order_indices_all_variables[k] for k in [0, 1]]
    total_order_indices_influent_variables = [total_order_indices_all_variables[k] for k in [0, 1]]
    fig = createfigure.square_figure_7(pixels=pixels)
    ax = fig.gca()
    ax.plot(
        first_order_indices_influent_variables,
        label="First order indice",
        color="k",
        marker="v",
        markersize=12,
        linestyle="None",
    )
    ax.plot(
        total_order_indices_influent_variables,
        label="Total indices",
        color="m",
        marker="D",
        markersize=12,
        linestyle="None",
    )
    ax.set_xlim((-0.2, 1.2))
    ax.set_xticks([0, 1])
    ax.set_xticklabels(
        [r"$\overline{\gamma}_r$", r"$\overline{\gamma}_{fs}$"],
        font=fonts.serif(),
        fontsize=fonts.axis_legend_size(),
    )
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
    ax.set_yticklabels(
        ["0", "0.25", "0.5", "0.75", "1"],
        font=fonts.serif(),
        fontsize=fonts.axis_legend_size(),
    )
    ax.set_xlabel("Variable", font=fonts.serif(), fontsize=fonts.axis_label_size())
    ax.set_ylabel("Sobol indices [ - ]", font=fonts.serif(), fontsize=fonts.axis_label_size())
    ax.legend(prop=fonts.serif(), loc="upper right", framealpha=0.7)
    filename = (
        "sobolindices_algo="
        + type_of_Sobol_sensitivity_implementation
        + "_metamodel="
        + type_of_metamodel
        + "_trainingamount="
        + str(training_amount)
        + "_size="
        + str(sensitivity_experiment_size)
        + "_"
    )
    savefigure.save_as_png(fig, filename + str(pixels) + "p")


if __name__ == "__main__":
    type_of_metamodel = "Kriging"
    training_amount = 0.7
    sensitivity_experiment_size_list = [20000]
    type_of_Sobol_sensitivity_implementation_list = ["Saltelli", "Jansen", "MauntzKucherenko", "Martinez"]

    metamodelposttreatment = MetamodelPostTreatment()
    distribution = Distribution()
    createfigure = CreateFigure()
    fonts = Fonts()
    savefigure = SaveFigure()

    for sensitivity_experiment_size in sensitivity_experiment_size_list:
        compute_and_export_sensitivity_algo_Saltelli(
            type_of_metamodel, training_amount, distribution, sensitivity_experiment_size
        )
        compute_and_export_sensitivity_algo_Jansen(
            type_of_metamodel, training_amount, distribution, sensitivity_experiment_size
        )
        compute_and_export_sensitivity_algo_MauntzKucherenko(
            type_of_metamodel, training_amount, distribution, sensitivity_experiment_size
        )
        compute_and_export_sensitivity_algo_Martinez(
            type_of_metamodel, training_amount, distribution, sensitivity_experiment_size
        )
        for type_of_Sobol_sensitivity_implementation in type_of_Sobol_sensitivity_implementation_list:
            plot_results_sensitivity_analysis(
                type_of_metamodel,
                training_amount,
                sensitivity_experiment_size,
                type_of_Sobol_sensitivity_implementation,
                createfigure,
                pixels=360,
            )
