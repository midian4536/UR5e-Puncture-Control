import sys, math, time, numpy as np, rtde_control, rtde_receive
from loguru import logger

ROBOT_IP = "192.168.11.5"

SELECTION_VECTOR = [1, 1, 1, 0, 0, 0]
TYPE = 2
LIMITS = [10.0, 10.0, 10.0, 1.0, 1.0, 1.0]
DAMPING = 0.003
GAIN_SCALING = 1.0

START_POSE = [0, -0.4, 0.3, math.pi, 0, 0]
FORCE_THRESHOLD = 7.0

logger.remove()
logger.add(
    sys.stdout,
    format="{time} | {level} | {message}",
    level="INFO",
    enqueue=True,
)

logger.info(f"Connecting to robot at {ROBOT_IP}")

rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
rtde_c.zeroFtSensor()

try:
    start_pose_joints = rtde_c.getInverseKinematics(START_POSE, rtde_r.getActualQ())
    logger.info("IK computation successful.")
except Exception as e:
    logger.error(f"IK computation failed: {e}")
    sys.exit(1)

logger.info("Moving to initial joint configuration...")
rtde_c.moveJ(start_pose_joints, 0.1, 0.1)
time.sleep(1)

rtde_c.forceModeSetGainScaling(GAIN_SCALING)
rtde_c.forceModeSetDamping(DAMPING)

logger.info("Force mode initialized.")
time.sleep(1)
stop_flag = True

try:
    while True:
        t_start = rtde_c.initPeriod()

        wrench_tcp = np.array(rtde_r.getActualTCPForce())
        force_tcp = wrench_tcp[:3]

        fmag = np.linalg.norm(force_tcp)

        logger.debug(f"Force magnitude: {fmag:.3f}")

        if fmag > FORCE_THRESHOLD:
            logger.info(f"Force above threshold ({fmag:.2f} N). Continuing force mode.")
            stop_flag = False

            rtde_c.forceMode(
                [0, 0, 0, 0, 0, 0],
                SELECTION_VECTOR,
                [0, 0, 0, 0, 0, 0],
                TYPE,
                LIMITS,
            )
        else:
            if not stop_flag:
                rtde_c.forceModeStop()
                stop_flag = True
                logger.info("Force below threshold. Stopping movement.")

        rtde_c.waitPeriod(t_start)

except KeyboardInterrupt:
    logger.warning("Interrupted by user.")

finally:
    logger.info("Exiting force mode and stopping script...")
    rtde_c.forceModeStop()
    rtde_c.stopScript()
    logger.info("Done.")
