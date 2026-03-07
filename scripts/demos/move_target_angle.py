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

try:
    logger.info(f"Connecting to robot at {ROBOT_IP}")
    rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
    rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
    
    MIDDLE_POSE = rtde_c.poseTrans(TARGET_POSE, offset)
    
    start_pose_joint = rtde_c.getInverseKinematics(START_POSE, rtde_r.getActualQ())
    middle_pose_joint = rtde_c.getInverseKinematics(MIDDLE_POSE, rtde_r.getActualQ())
    
    rtde_c.moveJ(start_pose_joint, 0.1, 0.1)
    time.sleep(1)
    rtde_c.moveJ(middle_pose_joint, 0.1, 0.1)
    time.sleep(1)
    
    rtde_c.moveL(TARGET_POSE, 0.1, 0.1)
    time.sleep(1)
    
except Exception as e:
    logger.error(f"An error occurred: {e}")
    sys.exit(1)

finally:
    if 'rtde_c' in locals():
        rtde_c.stopScript()
        logger.info("Disconnected from robot.")
