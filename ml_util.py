import exoboot
from typing import Type
import constants
import numpy as np
import tcpip
from collections import deque


class JetsonInterface():
    def __init__(self, do_set_up_server=True, server_ip=None, recv_port=None):
        self.data = deque(maxlen=10)
        if do_set_up_server:
            self.clienttcp = tcpip.ClientTCP(server_ip, recv_port)

    def package_message(self, side: Type[constants.Side], data: exoboot.Exo.DataContainer):
        if side == constants.Side.LEFT:
            side_str = '0'
        else:
            side_str = '1'
        accel_x = '%.2f' % data.accel_x
        accel_y = '%.2f' % data.accel_y
        accel_z = '%.2f' % data.accel_z
        gyro_x = '%.2f' % data.gyro_x
        gyro_y = '%.2f' % data.gyro_y
        gyro_z = '%.2f' % data.gyro_z
        ankle_angle = '%.2f' % data.ankle_angle
        ankle_velocity = '%.2f' % data.ankle_velocity
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


jetson = JetsonInterface(do_set_up_server=False)
jetson.parse('!1,1.25,3.4444')
jetson.parse('!1,1.25,3.4444')
jetson.parse('!0,1.25,3.4444')
jetson.parse('!1,1.25,3.4444!1,2,4')
gp, ss = jetson.get_most_recent_gait_phase(side=constants.Side.LEFT)
print(gp, ss)

# print(jetson.data)


# for i in range(10):
#     for side_str in ['0', '1']:
#         accel_x = '%.2f' % np.random.rand()
#         accel_y = '%.2f' % np.random.rand()
#         accel_z = '%.2f' % np.random.rand()
#         gyro_x = '%.2f' % np.random.rand()
#         gyro_y = '%.2f' % np.random.rand()
#         gyro_z = '%.2f' % np.random.rand()
#         ankle_angle = '%.2f' % np.random.rand()
#         ankle_velocity = '%.2f' % np.random.rand()
#         message = '!'+side_str + ',' + accel_x+','+accel_y+','+accel_z+','+gyro_x + \
#             ','+gyro_y+','+gyro_z+','+ankle_angle+','+ankle_velocity
#         print(message)


# data = exoboot.Exo.DataContainer()
# data.accel_x = 5.12345
# data.accel_y = 120.123123
# message = get_data_string_for_jetson(side=constants.Side.LEFT, data=data)
# print(message)
