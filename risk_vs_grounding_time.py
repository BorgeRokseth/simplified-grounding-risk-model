from risk_model import GroundingRiskModel, ScenarioAnalysisParameters, RiskModelConfiguration, CaseStudyScenario

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from ship_in_transit_simulator.models import DriftSimulationConfiguration, \
    EnvironmentConfiguration, MachineryMode, ShipConfiguration, SimplifiedPropulsionSimulationConfiguration,  \
    ShipModelSimplifiedPropulsion, SimplifiedPropulsionMachinerySystemConfiguration, \
    MachineryModeParams, MachineryModes, StaticObstacle

# Actual ship and sailing environment setup
main_engine_capacity = 2160e3
diesel_gen_capacity = 510e3
hybrid_shaft_gen_as_generator = 'GEN'
hybrid_shaft_gen_as_motor = 'MOTOR'
hybrid_shaft_gen_as_offline = 'OFF'

max_sim_time = 800
time_interval = 10

ship_config = ShipConfiguration(
    coefficient_of_deadweight_to_displacement=0.7,
    bunkers=200000,
    ballast=200000,
    length_of_ship=80,
    width_of_ship=16,
    added_mass_coefficient_in_surge=0.4,
    added_mass_coefficient_in_sway=0.4,
    added_mass_coefficient_in_yaw=0.4,
    dead_weight_tonnage=3850000,
    mass_over_linear_friction_coefficient_in_surge=130,
    mass_over_linear_friction_coefficient_in_sway=18,
    mass_over_linear_friction_coefficient_in_yaw=90,
    nonlinear_friction_coefficient__in_surge=2400,
    nonlinear_friction_coefficient__in_sway=4000,
    nonlinear_friction_coefficient__in_yaw=400
)
env_forces_setup = EnvironmentConfiguration(
    current_velocity_component_from_north=0,
    current_velocity_component_from_east=1,
    wind_speed=3,
    wind_direction=0
)

pto_params = MachineryModeParams(
    main_engine_capacity=main_engine_capacity,
    electrical_capacity=0,
    shaft_generator_state=hybrid_shaft_gen_as_generator
)

mec_params = MachineryModeParams(
    main_engine_capacity=main_engine_capacity,
    electrical_capacity=diesel_gen_capacity,
    shaft_generator_state=hybrid_shaft_gen_as_offline
)

pti_params = MachineryModeParams(
    main_engine_capacity=0,
    electrical_capacity=2*diesel_gen_capacity,
    shaft_generator_state=hybrid_shaft_gen_as_motor
)

pto_mode = MachineryMode(params=pti_params)
mec_mode = MachineryMode(params=mec_params)
pti_mode = MachineryMode(pti_params)


machinery_config = SimplifiedPropulsionMachinerySystemConfiguration(
    hotel_load=200e3,
    machinery_modes=MachineryModes([pto_mode, mec_mode, pti_mode]),
    thrust_force_dynamic_time_constant=15,
    rudder_angle_to_sway_force_coefficient=50e3,
    rudder_angle_to_yaw_force_coefficient=1000e3,
    max_rudder_angle_degrees=30
)

simulation_setup = SimplifiedPropulsionSimulationConfiguration(
    route_name="/Users/borgerokseth/Documents/source/drifting-grounding-risk-model/experiement_route.txt",
    initial_north_position_m=0,
    initial_east_position_m=0,
    initial_forward_speed_m_per_s=7,
    initial_sideways_speed_m_per_s=0,
    initial_thrust_force=0,
    initial_yaw_angle_rad=45*np.pi/180,
    initial_yaw_rate_rad_per_s=0,
    machinery_system_operating_mode=1,
    integration_step=0.3,
    simulation_time=600
)

ship_model = ShipModelSimplifiedPropulsion(
    ship_config=ship_config,
    machinery_config=machinery_config,
    environment_config=env_forces_setup,
    simulation_config=simulation_setup
)

obstacle = StaticObstacle(n_pos=1500, e_pos=1600, radius=250)
secondary_obstacle = StaticObstacle(n_pos=1700, e_pos=2300, radius=250)
third_obstacle = StaticObstacle(n_pos=2300, e_pos=1450, radius=250)
time_since_last_ship_drawing = 0
desired_heading = []
rudder_angles = []


# Simulation-based online risk model setup
max_sim_time = 400
time_interval = 10

scenario_analysis_parameters = ScenarioAnalysisParameters(
    main_engine_failure_rate=3e-9,
    genset_one_failure_rate=6e-9,
    genset_two_failure_rate=6e-9,
    hsg_failure_rate=2e-9,
    main_engine_mean_start_time=50,
    main_engine_start_time_std=1.2,
    main_engine_start_time_shift=20,
    main_engine_nominal_start_prob=1,
    main_engine_mean_restart_time=50,
    main_engine_restart_time_std=1.2,
    main_engine_restart_time_shift=20,
    main_engine_nominal_restart_prob=0.4,
    genset_one_mean_start_time=35,
    genset_one_start_time_std=1.0,
    genset_one_start_time_shift=14,
    genset_one_nominal_start_prob=1,
    genset_two_mean_start_time=35,
    genset_two_start_time_std=1.0,
    genset_two_start_time_shift=14,
    genset_two_nominal_start_prob=1,
    genset_one_mean_restart_time=35,
    genset_one_restart_time_std=1.0,
    genset_one_restart_time_shift=14,
    genset_one_nominal_restart_prob=0.5,
    genset_two_mean_restart_time=35,
    genset_two_restart_time_std=1.0,
    genset_two_restart_time_shift=14,
    genset_two_nominal_restart_prob=0.5,
    hsg_mean_start_time=12,
    hsg_start_time_std=1,
    hsg_start_time_shift=3,
    hsg_nominal_start_prob=1,
    hsg_mean_restart_time=12,
    hsg_restart_time_std=1,
    hsg_restart_time_shift=3,
    hsg_nominal_restart_prob=0.8,
)

risk_configuration = RiskModelConfiguration(
    max_drift_time_s=max_sim_time,
    risk_time_interval=time_interval
)

risk_model = []
probability_of_grounding_in_pto = []
probability_of_grounding_in_mec = []
probability_of_grounding_in_pti = []
risk_model_interval = 0
risk_time = []

available_time_array = []
risk_in_pto_array = []
risk_in_mec_array = []
risk_in_pti_array = []
for available_time in range(1,400):
    scenario = CaseStudyScenario(
        available_recovery_time=available_time,
        risk_time_interval=time_interval,
        scenario_parameters=scenario_analysis_parameters
    )
    grounding_scenarios = scenario.scenario_probabilities()
    available_time_array.append(available_time)
    risk_in_pto_array.append(grounding_scenarios.pto_mode_scenarios.probability_of_grounding)
    risk_in_mec_array.append(grounding_scenarios.mec_mode_scenarios.probability_of_grounding)
    risk_in_pti_array.append(grounding_scenarios.pti_mode_scenarios.probability_of_grounding)


fig, ax = plt.subplots()
ax.plot(available_time_array, risk_in_pto_array, label="PTO")
ax.plot(available_time_array, risk_in_mec_array, label="MEC")
ax.plot(available_time_array, risk_in_pti_array, label="PTI")
ax.legend()
plt.show()
