import sys
sys.path.append('..')
import logging
import rtde.rtde as rtde
import rtde.rtde_config as rtde_config

ROBOT_HOST = '192.168.56.101'
ROBOT_PORT = 30004
config_filename = 'rtdeState.xml'


class RtdeState:
    def __init__(self, robotIP, fName, frequency=500):
        self.robotIP = robotIP
        self.port = 30004
        self.con = rtde.RTDE(self.robotIP, self.port)
        self.keep_running = True
        self.config = fName
        self.frequency = frequency
        self.programState = {
            0: 'Stopping',
            1: 'Stopped',
            2: 'Playing',
            3: 'Pausing',
            4: 'Paused',
            5: 'Resuming',
            6: 'Retracting'
        }

    def initialize(self):
        logging.getLogger().setLevel(logging.INFO)
        conf = rtde_config.ConfigFile(self.config)
        self.con.connect()
        self.con.get_controller_version()
        # Try to add all additional recipe keys to setup.
        try:
            set_q_names, set_q_types = conf.get_recipe('set_q')
            self.set_q = self.con.send_input_setup(set_q_names, set_q_types)
            watchdog_names, watchdog_types = conf.get_recipe('watchdog')
            self.watchdog = self.con.send_input_setup(watchdog_names, watchdog_types)
            servo_names, servo_types = conf.get_recipe('servo')
            self.servo = self.con.send_input_setup(servo_names, servo_types)
        # Example error handling if a recipe key wasn't found.
        except KeyError as e:
            logging.debug(f'An item was not found in the XML: {e}')
        # Setup the "state" outputs which are core to this example.
        state_names, state_types = conf.get_recipe('state')
        self.con.send_output_setup(state_names, state_types, frequency=self.frequency)
        if not self.con.send_start():
            sys.exit()

    def receive(self):
        return self.con.receive()


if __name__ == "__main__":
    state_monitor = RtdeState(ROBOT_HOST, config_filename)
    state_monitor.initialize()
    runtime_old = 0
    while state_monitor.keep_running:
        state = state_monitor.receive()

        if state is None:
            break

        if state.runtime_state != runtime_old:
            logging.info(f'Robot program is {state_monitor.programState.get(state.runtime_state)}')
            runtime_old = state.runtime_state

    state_monitor.con.send_pause()
    state_monitor.con.disconnect()
