import sys, math, time, numpy as np, rtde_control, rtde_receive
from loguru import logger

ROBOT_IP = "192.168.11.5"
 
START_POSE = [0, -0.4, 0.3, math.pi, 0, 0]
MIDDLE_POSE = [5.3296*0.0254, -17.3776*0.0254, 4.9555*0.0254, 0.608, 2.383, -2.396]
TARGET_POSE = [5.3296*0.0254, -17.3776*0.0254, 2*0.0254, 0.608,  2.383, -2.396]

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
    
    # 计算初始姿态的逆运动学
    logger.info("Computing inverse kinematics for start pose...")
    start_pose_joints = rtde_c.getInverseKinematics(START_POSE, rtde_r.getActualQ())
    logger.info("IK computation successful for start pose.")
    
    # 计算中间姿态的逆运动学
    logger.info("Computing inverse kinematics for middle pose...")
    middle_pose_joints = rtde_c.getInverseKinematics(MIDDLE_POSE, rtde_r.getActualQ())
    logger.info("IK computation successful for middle pose.")
    
    # 计算目标姿态的逆运动学
    logger.info("Computing inverse kinematics for target pose...")
    target_pose_joints = rtde_c.getInverseKinematics(TARGET_POSE, rtde_r.getActualQ())
    logger.info("IK computation successful for target pose.")
    
    # 移动到初始姿态
    logger.info("Moving to initial pose...")
    rtde_c.moveJ(start_pose_joints, 0.5, 0.1)
    time.sleep(1)  # 等待机器人稳定
    
    # 移动到中间姿态
    logger.info("Moving to middle pose...")
    rtde_c.moveJ(middle_pose_joints, 0.5, 0.1)
    time.sleep(1)  # 等待机器人稳定
    
    # 移动到目标姿态
    logger.info("Moving to target pose...")
    rtde_c.moveJ(target_pose_joints, 0.1, 0.1)
    time.sleep(1)  # 等待机器人稳定
    
    logger.info("Movement completed successfully!")
    
    # 显示当前TCP位置
    current_pose = rtde_r.getActualTCPPose()
    logger.info(f"Current TCP pose: {[round(p, 4) for p in current_pose]}")
    
except Exception as e:
    logger.error(f"An error occurred: {e}")
    sys.exit(1)

finally:
    if 'rtde_c' in locals():
        rtde_c.stopScript()
        logger.info("Disconnected from robot.")
