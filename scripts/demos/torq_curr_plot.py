import sys, math, rtde_control, rtde_receive
import matplotlib.pyplot as plt
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
DURATION = 2.0
MAX_COUNT = int(DURATION * freq)

rtde_c.zeroFtSensor()

cmd_torque_log = []     
actual_torque_log = []   
current_log = []      
time_log = []

try:
    while counter < MAX_COUNT:
        t0 = rtde_c.initPeriod()

        phase = counter * dt
        torque = AMP * math.sin(2 * math.pi * SIN_FREQ * phase)

        rtde_c.directTorque([0, 0, 0, 0, torque, 0], False)

        currents = rtde_r.getActualCurrent()
        actual_torques = rtde_c.getJointTorques()

        cmd_torque_log.append(torque)
        actual_torque_log.append(actual_torques[4])
        current_log.append(currents[4])
        time_log.append(phase)

        counter += 1
        rtde_c.waitPeriod(t0)

except KeyboardInterrupt:
    logger.warning("Interrupted by user.")

finally:
    rtde_c.stopScript()
    logger.info("Done.")

plt.figure(figsize=(10, 10))

plt.subplot(3, 1, 1)
plt.plot(time_log, cmd_torque_log)
plt.title("Commanded Torque (Joint 5)")
plt.ylabel("Torque (Nm)")

plt.subplot(3, 1, 2)
plt.plot(time_log, actual_torque_log)
plt.title("Actual Joint Torque (Joint 5)")
plt.ylabel("Torque (Nm)")

plt.subplot(3, 1, 3)
plt.plot(time_log, current_log)
plt.title("Joint 5 Motor Current (A)")
plt.ylabel("Current (A)")
plt.xlabel("Time (s)")

plt.tight_layout()
plt.show()
