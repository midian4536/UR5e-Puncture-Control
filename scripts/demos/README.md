# `scripts/demos` 目录说明

`scripts/demos` 用于存放 **基础功能演示脚本**，主要用于快速验证基本逻辑。本目录中的脚本偏向最小可用示例，作为参考与基线测试，不使用任何结构化的代码和外部依赖以维持独立性。

---

## 当前脚本列表

### 1. `forcemode.py`
一个最小示例，演示如何：
- 连接 UR5e 机械臂  
- 初始化力控模式（Force Mode）
- 监测 TCP 力并根据阈值决定是否继续施力  
- 使用 `SELECTION_VECTOR` 限制力控轴向  
- 在外力低于阈值时自动停止 Force Mode  

---

### 2. `forcemode_csvlog.py`
在 `forcemode.py` 的基础上增加数据记录功能。  
该脚本会将运行期间的实时运动状态保存至 `outputs/runtime_*/ur5e_data.csv`，包括：

- TCP 位姿 (`TCPPose`)
- TCP 速度 (`TCPSpeed`)
- 关节位置 (`Q`)
- 关节速度 (`Qd`)
- 关节电流 (`Current`)
- 关节电压 (`Voltage`)
- 关节力矩 (`JointTorques`)
