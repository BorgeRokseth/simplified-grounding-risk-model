import case_study_ship_setup as case
import matplotlib.pyplot as plt

params = case.CaseStudySystemParameters(
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

case_study_system = case.case_study_system_setup(system_params=params, time_interval=60, available_time=4)

pto_risk = []
mec_risk = []
pti_risk = []
times = range(0, 120)
for t in times:
    case_study_system.pto_mode_scenarios.update_probability(time_interval=60, available_time=t)
    case_study_system.mec_mode_scenarios.update_probability(time_interval=60, available_time=t)
    case_study_system.pti_mode_scenarios.update_probability(time_interval=60, available_time=t)
    pto_risk.append(case_study_system.pto_mode_scenarios.probability_of_grounding)
    mec_risk.append(case_study_system.mec_mode_scenarios.probability_of_grounding)
    pti_risk.append(case_study_system.pti_mode_scenarios.probability_of_grounding)

plt.plot(times, pto_risk, label='PTO')
plt.plot(times, mec_risk, label='MEC')
plt.plot(times, pti_risk, label='PTI')
plt.xlabel('Available restoration time in the event of loss of propulsion')
plt.ylabel('$P_G$')
plt.legend()
plt.show()
