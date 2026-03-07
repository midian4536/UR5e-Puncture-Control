import time, numpy as np, rtde_control, rtde_receive
from commons.config_loader import ConfigLoader


class RobotController:
    def __init__(self, cfg: ConfigLoader):
        self.ip = cfg.get("robot", "ip")
        self.start_pose = cfg.get("robot", "start_pose")

        self.selection_vector = cfg.get("force_mode", "selection_vector")
        self.type = cfg.get("force_mode", "type")
        self.limits = cfg.get("force_mode", "limits")
        self.damping = cfg.get("force_mode", "damping")
        self.gain_scaling = cfg.get("force_mode", "gain_scaling")
        self.force_threshold = cfg.get("force_mode", "threshold")
        self.time_stop = cfg.get("force_mode", "time_stop")

        self.c = rtde_control.RTDEControlInterface(self.ip)
        self.r = rtde_receive.RTDEReceiveInterface(self.ip)

        self.c.zeroFtSensor()
        self.stop_flag = True
        self.low_force_start_time = None
        self.count =0

    def move_to_start(self):
        joints = self.c.getInverseKinematics(self.start_pose, self.r.getActualQ())
        self.c.moveJ(joints, 0.1, 0.1)
        time.sleep(1)

    def init_force_mode(self):
        self.c.forceModeSetGainScaling(self.gain_scaling)
        self.c.forceModeSetDamping(self.damping)
    def step(self) -> dict:
        t_start = self.c.initPeriod()

        wrench = np.array(self.r.getActualTCPForce())
        force = wrench[:3]
        fmag = np.linalg.norm(force)
        # if self.count % 10 == 0:
        #     print(fmag)
        # self.count += 1

        if fmag > self.force_threshold:
            self.stop_flag = False
            self.low_force_start_time = None
            self.c.forceMode(
                [0] * 6, self.selection_vector, [0] * 6, self.type, self.limits
            )
        else:
            if self.low_force_start_time is None:
                self.low_force_start_time = time.time()
            elif time.time() - self.low_force_start_time > self.time_stop:
                if not self.stop_flag:
                    self.c.forceModeStop()
                    self.c.stopJ()
                    self.stop_flag = True

        state = {
            "timestamp": time.time(),
            "tcp_pose": np.array(self.r.getActualTCPPose()),
            "tcp_speed": np.array(self.r.getActualTCPSpeed()),
            "q": np.array(self.r.getActualQ()),
            "qd": np.array(self.r.getActualQd()),
            "curr": np.array(self.r.getActualCurrent()),
            "volt": np.array(self.r.getActualJointVoltage()),
            #"torq": np.array(self.c.getJointTorques()),
            "torq": np.eye(6),
        }

        self.c.waitPeriod(t_start)
        return state

    def shutdown(self):
        self.c.forceModeStop()
        self.c.stopScript()
