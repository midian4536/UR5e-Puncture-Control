import sys, csv, math, time, numpy as np, rtde_control, rtde_receive
from pathlib import Path
from datetime import datetime
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

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = Path("outputs") / f"runtime_{timestamp}"
output_dir.mkdir(parents=True, exist_ok=True)

csv_path = output_dir / "ur5e_data.csv"

with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    header = (
        ["time"]
        + [f"tcp_pose_{i}" for i in range(6)]
        + [f"tcp_speed_{i}" for i in range(6)]
        + [f"q_{i}" for i in range(6)]
        + [f"qd_{i}" for i in range(6)]
        + [f"curr_{i}" for i in range(6)]
        + [f"volt_{i}" for i in range(6)]
        + [f"torq_{i}" for i in range(6)]
    )
    writer.writerow(header)

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

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        tcp_pose = np.array(rtde_r.getActualTCPPose(), dtype=float)
        tcp_speed = np.array(rtde_r.getActualTCPSpeed(), dtype=float)
        actual_q = np.array(rtde_r.getActualQ(), dtype=float)
        actual_qd = np.array(rtde_r.getActualQd(), dtype=float)
        actual_current = np.array(rtde_r.getActualCurrent(), dtype=float)
        voltage = np.array(rtde_r.getActualJointVoltage(), dtype=float)
        joint_torques = np.array(rtde_c.getJointTorques(), dtype=float)

        with open(csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            row = (
                [now]
                + tcp_pose.tolist()
                + tcp_speed.tolist()
                + actual_q.tolist()
                + actual_qd.tolist()
                + actual_current.tolist()
                + voltage.tolist()
                + joint_torques.tolist()
            )
            writer.writerow(row)

        rtde_c.waitPeriod(t_start)

except KeyboardInterrupt:
    logger.warning("Interrupted by user.")

finally:
    logger.info("Exiting force mode and stopping script...")
    rtde_c.forceModeStop()
    rtde_c.stopScript()
    logger.info("Done.")
