# `demos` 目录说明

`demos` 用于存放 **基础功能演示脚本**，主要用于快速验证基本逻辑。本目录中的脚本偏向最小可用示例，作为参考与基线测试，不使用外部依赖以维持独立性。

---

## 当前脚本列表

### 1. `forcemode.py`
一个最小示例，演示如何：
- 连接 UR5e 
- 初始化力控模式（Force Mode）

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

---

### 3. `visual.py`
获得outputs目录下最新的runtime目录，进行可视化，包括：

- 关节电流 (`Current`)
- 关节电压 (`Voltage`)
- 关节力矩 (`JointTorques`)
- TCP轨迹

---

### 4. `direct_torq.py`
使用 RTDE 的 `directTorque` 接口 **直接控制关节扭矩** 的最小示例。

---

### 5. `torq_curr_plot.py`
用于在 `directTorque` 基础上分析 **“指令扭矩–实际扭矩–电机电流”关系** 的实验脚本。

> ⚠ 当前版本尚未更新，仍为 **错误实现，存在以下问题：**
>
> - 使用了 `rtde_c.getJointTorques()` 在实时控制循环中读取关节力矩  
> - `RTDEControlInterface` 的读取接口是阻塞式的，会破坏 500 Hz 控制周期的实时性  
> - 这会导致扭矩控制不稳定，波形畸变

**后续需要的优化方向：**

- 将关节力矩读取统一改为 `rtde_r.getJointTorques()`，与 `getActualCurrent()` 一样都走 `RTDEReceive` 实时数据通道。
