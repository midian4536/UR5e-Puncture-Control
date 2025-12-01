# `sandbox` 目录说明

`sandbox` 用于存放 **开发过程中的临时测试脚本**。本目录中的代码用于检查控制流程、数据流以及配置结构是否正常工作，用于对代码修改进行快速测试。  

---

## 当前脚本列表

### 1. `forcemode_csvlog.py`

一个最小化的测试脚本，用于验证以下内容：

- 连接 UR5e 机械臂  
- 初始化并进入 Force Mode（力控模式）  
- 根据 TCP 力的大小决定是否继续施力  
- 使用 `SELECTION_VECTOR` 限制作用轴向  
- 将实时运动状态完整地记录到 CSV 文件  

运行脚本后，会在 `outputs/runtime_*/ur5e_data.csv` 生成数据文件，其中包含：  
- TCP 位姿 (`TCPPose`)  
- TCP 速度 (`TCPSpeed`)  
- 关节位置 (`Q`)  
- 关节速度 (`Qd`)  
- 关节电流 (`Current`)  
- 关节电压 (`Voltage`)  
- 关节力矩 (`JointTorques`)  

本脚本作为后续模块化重构（`RobotController`、`DataLogger` 等类）的最初验证基线。
