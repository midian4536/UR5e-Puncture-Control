import sys, math, rtde_control, rtde_receive
from loguru import logger

ROBOT_IP = "192.168.11.5"

logger.remove()
logger.add(
    sys.stdout, format="{time} | {level} | {message}", level="INFO", enqueue=True
)

rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)

START_POSE = [0, -0.4, 0.3, math.pi, 0, 0]

try:
    start_pose_joints = rtde_c.getInverseKinematics(START_POSE, rtde_r.getActualQ())
except:
    sys.exit(1)

logger.info("Moving to initial joint configuration...")
rtde_c.moveJ(start_pose_joints, 0.1, 0.1)

logger.info("Starting direct torque control demo...")
rtde_c.stopJ(0.5)

freq = 500.0
dt = 1.0 / freq
counter = 0

AMP = 3.0
SIN_FREQ = 0.5

rtde_c.zeroFtSensor()

try:
    while True:
        t0 = rtde_c.initPeriod()

        phase = counter * dt
        torque = AMP * math.sin(2 * math.pi * SIN_FREQ * phase)

        rtde_c.directTorque([0, torque, 0, 0, torque, 0], True)

        counter += 1
        rtde_c.waitPeriod(t0)

except KeyboardInterrupt:
    logger.warning("Interrupted by user.")

finally:
    rtde_c.stopScript()
    logger.info("Done.")
