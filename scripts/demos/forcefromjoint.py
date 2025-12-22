import sys, math, rtde_control, rtde_receive, numpy as np
import matplotlib.pyplot as plt
from loguru import logger
from scipy.signal import butter, filtfilt

def get_ur5e_jacobian(q, ref_frame='base_link', target_frame='wrist_3_link'):
    """
    根据UR5e的URDF描述计算几何雅可比矩阵的关系。
    """
    q = np.array(q, dtype=np.float64)
    if len(q) != 6:
        raise ValueError("关节角 q 必须包含 6 个元素")

    def rpy_to_mat(roll, pitch, yaw):
        """计算 Rz * Ry * Rx (Extrinsic X-Y-Z / Intrinsic Z-Y-X)"""
        cx, sx = np.cos(roll), np.sin(roll)
        cy, sy = np.cos(pitch), np.sin(pitch)
        cz, sz = np.cos(yaw), np.sin(yaw)
        Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
        Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
        Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
        return Rz @ Ry @ Rx

    def get_transform(xyz, rpy):
        T = np.eye(4)
        T[:3, :3] = rpy_to_mat(*rpy)
        T[:3, 3] = xyz
        return T

    def joint_transform(theta):
        c, s = np.cos(theta), np.sin(theta)
        T = np.eye(4)
        T[:3, :3] = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        return T

    pi = np.pi
    chain = [
        {'name': 'base_link', 'parent': 'world', 'T': np.eye(4), 'type': 'fixed'},
        {'name': 'base_link_inertia', 'parent': 'base_link', 'T': get_transform([0, 0, 0], [0, 0, pi]), 'type': 'fixed'},
        {'name': 'shoulder_link', 'parent': 'base_link_inertia', 'T': get_transform([0, 0, 0.1625], [0, 0, 0]), 'type': 'revolute', 'q_idx': 0},
        {'name': 'upper_arm_link', 'parent': 'shoulder_link', 'T': get_transform([0, 0, 0], [pi/2, 0, 0]), 'type': 'revolute', 'q_idx': 1},
        {'name': 'forearm_link', 'parent': 'upper_arm_link', 'T': get_transform([-0.425, 0, 0], [0, 0, 0]), 'type': 'revolute', 'q_idx': 2},
        {'name': 'wrist_1_link', 'parent': 'forearm_link', 'T': get_transform([-0.3922, 0, 0.1333], [0, 0, 0]), 'type': 'revolute', 'q_idx': 3},
        {'name': 'wrist_2_link', 'parent': 'wrist_1_link', 'T': get_transform([0, -0.0997, 0], [pi/2, 0, 0]), 'type': 'revolute', 'q_idx': 4},
        {'name': 'wrist_3_link', 'parent': 'wrist_2_link', 'T': get_transform([0, 0.0996, 0], [pi/2, pi, pi]), 'type': 'revolute', 'q_idx': 5},
        {'name': 'flange', 'parent': 'wrist_3_link', 'T': get_transform([0, 0, 0], [0, -pi/2, -pi/2]), 'type': 'fixed'},
        {'name': 'tool0', 'parent': 'flange', 'T': get_transform([0, 0, 0], [pi/2, 0, pi/2]), 'type': 'fixed'}
    ]

    global_transforms = {}
    global_transforms['world'] = np.eye(4)
    joint_axes = {} 
    joint_positions = {}

    for link in chain:
        parent_T = global_transforms[link['parent']]
        local_fixed_T = link['T']
        
        if link['type'] == 'revolute':
            idx = link['q_idx']
            T_rot = joint_transform(q[idx])
            T_current_joint_frame = parent_T @ local_fixed_T
            
            joint_axes[idx] = T_current_joint_frame[:3, 2] # Z axis
            joint_positions[idx] = T_current_joint_frame[:3, 3] # Origin
            
            global_transforms[link['name']] = T_current_joint_frame @ T_rot
        else:
            global_transforms[link['name']] = parent_T @ local_fixed_T

    if ref_frame not in global_transforms:
        # 尝试处理别名，如 ref_frame 为 "base" 可能指 base_link
        if ref_frame == "base": ref_frame = "base_link"
        else: raise ValueError(f"未知的 ref_frame: {ref_frame}")
        
    if target_frame not in global_transforms:
        raise ValueError(f"未知的 target_frame: {target_frame}")

    T_ref = global_transforms[ref_frame]
    T_target = global_transforms[target_frame]
    
    p_target = T_target[:3, 3] # 目标在全局坐标系下的位置
    
    J_global = np.zeros((6, 6))
    
    def get_ancestors(frame_name):
        ancestors = []
        current = frame_name
        while current != 'world':
            link_def = next((item for item in chain if item['name'] == current), None)
            if link_def:
                ancestors.append(current)
                current = link_def['parent']
            else:
                break
        return ancestors

    target_ancestors = get_ancestors(target_frame) # 包含 target_frame 自身
    ref_ancestors = get_ancestors(ref_frame)

    for i in range(6):
        joint_child_link = [item['name'] for item in chain if item.get('q_idx') == i][0]
        is_upstream_of_target = joint_child_link in target_ancestors
        is_upstream_of_ref = joint_child_link in ref_ancestors
        
        if is_upstream_of_target and not is_upstream_of_ref:
            z_i = joint_axes[i]
            p_i = joint_positions[i]
            
            J_global[:3, i] = np.cross(z_i, p_target - p_i)
            J_global[3:, i] = z_i

    R_ref = T_ref[:3, :3]
    R_ref_inv = R_ref.T
    
    J_ref = np.zeros((6, 6))
    J_ref[:3, :] = R_ref_inv @ J_global[:3, :]
    J_ref[3:, :] = R_ref_inv @ J_global[3:, :]
    
    return J_ref

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

cutoff_freq = 20.0  
order = 4  
b, a = butter(order, cutoff_freq, btype='low', analog=False, fs=freq)

actual_torques_history = []

rtde_c.zeroFtSensor()

actual_torque_log = []
current_log = []
tcp_force_log = [[], [], [], [], [], []]
tcp_force_by_joint_log = [[], [], [], [], [], []]
time_log = []

try:
        while counter * dt < 10.0:
            t0 = rtde_c.initPeriod()

            currents = rtde_r.getActualCurrent()

            actual_torques_raw = np.array(rtde_c.getJointTorques())*-1
            

            actual_torques_history.append(actual_torques_raw)

            if len(actual_torques_history) > 100:
                actual_torques_history.pop(0)
            

            actual_torques = np.zeros(6)
            for i in range(6):
                torque_joint = [torque[i] for torque in actual_torques_history]
                if len(torque_joint) > 0:
                    actual_torques[i] = filtfilt(b, a, torque_joint, padlen=0)[-1]
                else:
                    actual_torques[i] = actual_torques_raw[i]
            actual_tcp_force = rtde_r.getActualTCPForce()
            q = rtde_r.getActualQ()
            Jac = get_ur5e_jacobian(q, ref_frame='base_link', target_frame='tool0')
            tcp_force_by_joint = np.linalg.pinv(Jac.T) @ actual_torques
            
            tcp_force_by_joint_reversed = tcp_force_by_joint.copy()
            tcp_force_by_joint_reversed[2] = -tcp_force_by_joint_reversed[2]
            tcp_force_by_joint_reversed[5] = -tcp_force_by_joint_reversed[5]

            actual_torque_log.append(actual_torques[4])
            for i in range(6):
                tcp_force_log[i].append(actual_tcp_force[i])
                tcp_force_by_joint_log[i].append(tcp_force_by_joint_reversed[i])
                
            current_log.append(currents[4])
            time_log.append(counter * dt)
            counter += 1
            rtde_c.waitPeriod(t0)
except KeyboardInterrupt:
    logger.warning("Interrupted by user.")

finally:
    rtde_c.stopScript()
    logger.info("Done.")

plt.figure(figsize=(10, 10))

plt.subplot(2, 1, 1)
plt.plot(time_log, actual_torque_log)
plt.title("Actual Joint Torque (Joint 5)")
plt.ylabel("Torque (Nm)")

plt.subplot(2, 1, 2)
plt.plot(time_log, current_log)
plt.title("Joint 5 Motor Current (A)")
plt.ylabel("Current (A)")
plt.xlabel("Time (s)")

plt.figure(figsize=(10, 25))

plt.subplot(6, 1, 1)
plt.plot(time_log, tcp_force_log[0])
plt.title("TCP Force x-axis")
plt.ylabel("Force (N)")

plt.subplot(6, 1, 2)
plt.plot(time_log, tcp_force_log[1])
plt.title("TCP Force y-axis")
plt.ylabel("Force (N)")

plt.subplot(6, 1, 3)
plt.plot(time_log, tcp_force_log[2])
plt.title("TCP Force z-axis")
plt.ylabel("Force (N)")

plt.subplot(6, 1, 4)
plt.plot(time_log, tcp_force_log[3])
plt.title("TCP Force rx-axis")
plt.ylabel("Torque (Nm)")

plt.subplot(6, 1, 5)
plt.plot(time_log, tcp_force_log[4])
plt.title("TCP Force ry-axis")
plt.ylabel("Torque (Nm)")

plt.subplot(6, 1, 6)
plt.plot(time_log, tcp_force_log[5])
plt.title("TCP Force rz-axis")
plt.ylabel("Torque (Nm)")
plt.xlabel("Time (s)")

plt.figure(figsize=(10, 25))

plt.subplot(6, 1, 1)
plt.plot(time_log, tcp_force_by_joint_log[0])
plt.title("TCP Force by Joint x-axis")
plt.ylabel("Force (N)")

plt.subplot(6, 1, 2)
plt.plot(time_log, tcp_force_by_joint_log[1])
plt.title("TCP Force by Joint y-axis")
plt.ylabel("Force (N)")

plt.subplot(6, 1, 3)
plt.plot(time_log, tcp_force_by_joint_log[2])
plt.title("TCP Force by Joint z-axis")
plt.ylabel("Force (N)")

plt.subplot(6, 1, 4)
plt.plot(time_log, tcp_force_by_joint_log[3])
plt.title("TCP Force by Joint rx-axis")
plt.ylabel("Torque (Nm)")

plt.subplot(6, 1, 5)
plt.plot(time_log, tcp_force_by_joint_log[4])
plt.title("TCP Force by Joint ry-axis")
plt.ylabel("Torque (Nm)")

plt.subplot(6, 1, 6)
plt.plot(time_log, tcp_force_by_joint_log[5])
plt.title("TCP Force by Joint rz-axis")
plt.ylabel("Torque (Nm)")
plt.xlabel("Time (s)")

plt.tight_layout()
plt.show()