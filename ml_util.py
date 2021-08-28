import exoboot
from typing import Type
import constants
import numpy as np
import tcpip
from collections import deque


class JetsonInterface():

    def __init__(self, do_set_up_server=True, server_ip='192.168.1.2', recv_port=8080):
        self.data = deque(maxlen=10)
        if do_set_up_server:
            self.clienttcp = tcpip.ClientTCP(server_ip, recv_port)

    def package_message(self, side: Type[constants.Side], data: exoboot.Exo.DataContainer):
        if side == constants.Side.LEFT:
            side_str = '0'
        else:
            side_str = '1'
        accel_x = '%.5f' % data.accel_x
        accel_y = '%.5f' % data.accel_y
        accel_z = '%.5f' % data.accel_z
        gyro_x = '%.5f' % data.gyro_x
        gyro_y = '%.5f' % data.gyro_y
        gyro_z = '%.5f' % data.gyro_z
        ankle_angle = '%.5f' % data.ankle_angle
        ankle_velocity = '%.5f' % data.ankle_velocity
        message = '!'+side_str + ',' + accel_x+','+accel_y+','+accel_z+','+gyro_x + \
            ','+gyro_y+','+gyro_z+','+ankle_angle+','+ankle_velocity
        return message

    def package_and_send_message(self, side, data_container):
        message = self.package_message(side=side, data=data_container)
        self.clienttcp.to_server(msg=message)

    def grab_message_and_parse(self):
        message = self.clienttcp.from_server()
        self.parse(message)

    def parse(self, message):
        '''parses message from jetson. Returns side, gait_phase, is_stance'''
        if message is not None:
            message_list = message.split("!")[1:]
            for message in message_list:
                data_list = message.split(",")
                self.data.appendleft([float(i) for i in data_list])

    def get_most_recent_gait_phase(self, side: Type[constants.Side]):
        for message in self.data:
            if side == constants.Side.LEFT and message[0] == 0:
                gait_phase = message[1]
                stance_swing = message[2]
                return gait_phase, stance_swing
            elif side == constants.Side.RIGHT and message[0] == 1:
                gait_phase = message[1]
                stance_swing = message[2]
                return gait_phase, stance_swing
