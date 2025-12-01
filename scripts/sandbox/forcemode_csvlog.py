from commons.config_loader import ConfigLoader
from commons.robot_controller import RobotController
from commons.data_logger import DataLogger
from commons.utils import find_config_path


def main():
    yaml_path = find_config_path("robot.yaml")
    cfg = ConfigLoader(yaml_path)
    controller = RobotController(cfg)
    logger = DataLogger(cfg)

    controller.move_to_start()
    controller.init_force_mode()

    try:
        while True:
            state = controller.step()
            logger.log(state)
    except KeyboardInterrupt:
        pass
    finally:
        logger.close()
        controller.shutdown()


if __name__ == "__main__":
    main()
