
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from risk_model import GroundingRiskModel, ScenarioAnalysisParameters, RiskModelConfiguration
from ship_in_transit_simulator.models import SimulationConfiguration, \
    EnvironmentConfiguration, ShipConfiguration

if __name__ == '__main__':
    import seacharts

    max_drift_sim_time = 1000
    main_time_step = 0.5

    # current has opposite direction than the name suggests.
    current_from_north = 0
    current_from_east = 0
    wind_speed = 17
    wind_direction= 0

    desired_speed_m_per_sec = 7

    # Load seachart
    size = 2000, 2000
    center = 182616, 7098718
    files = ['trondelag.gdb']
    enc = seacharts.ENC(size=size, center=center, files=files, new_data=False)

    scenario_analysis_parameters = ScenarioAnalysisParameters(
        main_engine_failure_rate=3e-9,
        main_engine_mean_restart_time=50,
        main_engine_restart_time_std=1.2,
        main_engine_restart_time_shift=20,
        main_engine_nominal_restart_prob=0.4,
    )

    risk_configuration = RiskModelConfiguration(
        max_drift_time_s=max_drift_sim_time,
        risk_time_interval=10
    )

    shore = enc.shore.geometry

    # States of the ship for which we are calculating the grounding risk
    north_position = 7098718
    east_position = 182500
    yaw_angle = 200 * np.pi/180
    speed_forward = 7
    speed_sideways = 0.4
    yaw_rate = 0.01


    drifting_sim_setup = SimulationConfiguration(
        initial_north_position_m=north_position,
        initial_east_position_m=east_position,
        initial_yaw_angle_rad=yaw_angle,
        initial_forward_speed_m_per_s=speed_forward,
        initial_sideways_speed_m_per_s=speed_sideways,
        initial_yaw_rate_rad_per_s=yaw_rate,
        integration_step=0.5,
        simulation_time=risk_configuration.max_drift_time_s
    )
    drifting_ship_setup = ShipConfiguration(
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
    current_environmental_conditions = EnvironmentConfiguration(
        current_velocity_component_from_north=-2,
        current_velocity_component_from_east=1,
        wind_speed=12,
        wind_direction=0
    )
    grounding_risk = GroundingRiskModel(
        risk_model_config=risk_configuration,
        env_config=current_environmental_conditions,
        environment=shore,
        scenario_params=scenario_analysis_parameters,
        sim_config=drifting_sim_setup,
        ttg_sim_config=drifting_ship_setup
    )

    # Plot ship poses every "snap_shot_interval" second
    drifting_ship_data = pd.DataFrame().from_dict(grounding_risk.ttg_simulator.ship_model.simulation_results)
    snap_shot_interval = 20
    time_since_snap_shot = 20
    id = 0
    ship_poses = []
    for  east, north, yaw, time in zip(
            drifting_ship_data['east position [m]'],
            drifting_ship_data['north position [m]'],
            drifting_ship_data['yaw angle [deg]'],
            drifting_ship_data['time [s]']
    ):
        if time_since_snap_shot >= snap_shot_interval:
            ship_poses.append((id, int(east), int(north), yaw, "red"))
            id += 1
            time_since_snap_shot = 0
        else:
            time_since_snap_shot += grounding_risk.ttg_simulator.ship_model.int.dt

    enc.add_vessels(*ship_poses)

    print("Risk of grounding: ", grounding_risk.calculate_risk_output())

    enc.show_display()
    plt.show()