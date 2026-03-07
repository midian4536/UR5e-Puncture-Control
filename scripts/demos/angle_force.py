import sys, math, time, numpy as np, rtde_control, rtde_receive
from loguru import logger

ROBOT_IP = "192.168.11.5"
START_POSE = [0, -0.4, 0.3, math.pi, 0, 0]
TARGET_POSE = [0.086, -0.374, 0.3725, 2.10, 0.39, -0.35]
offset = [0, 0, -0.2, 0, 0, 0]         
logger.remove()
logger.add(
    sys.stdout,
    format="{time} | {level} | {message}",
    level="INFO",
    enqueue=True,
)

SELECTION_VECTOR = [1, 1, 1, 0, 0, 0]
TYPE = 2
LIMITS = [10.0, 10.0, 10.0, 1.0, 1.0, 1.0]
DAMPING = 0.007
GAIN_SCALING = 1.2
FORCE_THRESHOLD = 2.0

rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
rtde_c.zeroFtSensor()

MIDDLE_POSE = rtde_c.poseTrans(TARGET_POSE, offset)

start_pose_joint = rtde_c.getInverseKinematics(START_POSE, rtde_r.getActualQ())
middle_pose_joint = rtde_c.getInverseKinematics(MIDDLE_POSE, rtde_r.getActualQ())

rtde_c.moveJ(start_pose_joint, 0.2, 0.1)
time.sleep(1)
rtde_c.moveJ(middle_pose_joint, 0.2, 0.1)
time.sleep(1)

rtde_c.moveL(TARGET_POSE, 0.1, 0.1)
time.sleep(1)

stop_flag = True
low_force_start_time = None

rtde_c.forceModeSetGainScaling(GAIN_SCALING)
rtde_c.forceModeSetDamping(DAMPING)

rtde_c.zeroFtSensor()

try:
    while True:
        t_start = rtde_c.initPeriod()

        wrench_tcp = np.array(rtde_r.getActualTCPForce())
        force_tcp = wrench_tcp[:3]

        fmag = np.linalg.norm(force_tcp)

        if fmag > FORCE_THRESHOLD:
            stop_flag = False
            low_force_start_time = None
            rtde_c.forceMode(
                [0, 0, 0, 0, 0, 0],
                SELECTION_VECTOR,
                [0, 0, 0, 0, 0, 0],
                TYPE,
                LIMITS,
            )
        else:
            if low_force_start_time is None:
                low_force_start_time = time.time()
                logger.debug(f"Low force detected. Starting timer: {low_force_start_time:.2f}")
            elif time.time() - low_force_start_time > 2.0:
                if not stop_flag:
                    rtde_c.forceModeStop()
                    rtde_c.stopJ()
                    stop_flag = True
                    logger.info("Force below threshold for more than 2 seconds. Stopping movement.")
            else:
                logger.debug(f"Low force detected for {time.time() - low_force_start_time:.2f} seconds. Waiting for 2 seconds.")

        rtde_c.waitPeriod(t_start)

except KeyboardInterrupt:
    logger.warning("Interrupted by user.")

finally:
    logger.info("Exiting force mode and stopping script...")
    rtde_c.forceModeStop()
    rtde_c.stopScript()
    logger.info("Done.")

