# Robocon GUI ROS1 Flow

Project ini sudah disesuaikan untuk flow:

```text
Jetson Xavier
├─ GUI PyQt5 full Python
│  ├─ publish command ke /robocon/gui_cmd
│  └─ subscribe telemetry dari /robocon/telemetry
└─ Robot autonomous node
   ├─ subscribe /robocon/gui_cmd
   └─ publish telemetry ke /robocon/telemetry
```

## Perubahan utama

- ROS2 `rclpy` diganti ROS1 `rospy`.
- Custom message `robocon_interfaces/msg/GuiCommand` tidak dipakai lagi.
- Message command memakai `std_msgs/String` berisi JSON.
- GUI sekarang bisa menerima telemetry balik dari robot.
- Package build system diganti dari `ament_python` ke `catkin`.

## Topic

### `/robocon/gui_cmd`
Arah: GUI -> Robot

Contoh payload:

```json
{
  "cmd": "START_OTONOM",
  "color": "MERAH",
  "checkpoints": [1, 3, 5],
  "status": "OTONOM"
}
```

### `/robocon/telemetry`
Arah: Robot -> GUI

Contoh payload:

```json
{
  "status": "RUNNING",
  "battery": 12.4,
  "mcu_temp": 43.2,
  "xavier_temp": 58.0,
  "current_checkpoint": 3,
  "error": null
}
```

## Cara build di Jetson ROS1 Noetic

Letakkan folder `robocon_gui` dan `robocon_robot` ke dalam `~/catkin_ws/src`.

```bash
mkdir -p ~/catkin_ws/src
cp -r src/robocon_gui ~/catkin_ws/src/
cp -r src/robocon_robot ~/catkin_ws/src/
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

## Cara menjalankan

Terminal 1:

```bash
source /opt/ros/noetic/setup.bash
roscore
```

Terminal 2:

```bash
source /opt/ros/noetic/setup.bash
source ~/catkin_ws/devel/setup.bash
rosrun robocon_robot robot_command_subscriber
```

Terminal 3:

```bash
source /opt/ros/noetic/setup.bash
source ~/catkin_ws/devel/setup.bash
rosrun robocon_gui robocon_gui
```

## Catatan

File `robot_command_subscriber.py` masih contoh adapter. Bagian TODO bisa kamu isi dengan logic robot asli, misalnya panggil controller motor, serial ke microcontroller, atau pipeline autonomous yang sudah ada.
