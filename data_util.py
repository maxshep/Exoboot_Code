import exoboot
import time
from typing import Type
import csv
import constants


def get_big_data_container_from_exo_list(exo_list, fields_to_disclude=None):
    left_exo = None
    right_exo = None
    for exo in exo_list:
        if exo.side == constants.Side.LEFT:
            left_exo = exo
        elif exo.side == constants.Side.RIGHT:
            right_exo = exo
    if left_exo is None or right_exo is None:
        raise ValueError('exo list does not contain both a right and left exo')
    return BilateralDataContainer(left_exo_data=left_exo.data,
                                  right_exo_data=right_exo.data,
                                  fields_to_disclude=fields_to_disclude)


class BilateralDataContainer():
    def __init__(self,
                 left_exo_data: Type[exoboot.Exo.DataContainer],
                 right_exo_data: Type[exoboot.Exo.DataContainer],
                 fields_to_disclude: None):

        self.left = left_exo_data
        self.right = right_exo_data
        if fields_to_disclude is None:
            self.fields_to_disclude = []
        else:
            self.fields_to_disclude = fields_to_disclude
        self.loop_time = 0
        self.did_slip = False
        self.big_dict = {}
        self.update_dict()

    def update_dict(self):
        for key, value in self.left.__dict__.items():
            if key not in self.fields_to_disclude:
                self.big_dict[key+'_left'] = value
        for key, value in self.right.__dict__.items():
            if key not in self.fields_to_disclude:
                self.big_dict[key+'_right'] = value
        self.big_dict['did_slip'] = self.did_slip
        self.big_dict['loop_time'] = self.loop_time


class BilateralDataSaver():
    def __init__(self, file_ID: str, data: Type[BilateralDataContainer]):
        '''file_ID is used as a custom file identifier after date.'''
        self.file_ID = file_ID
        self.data = data
        subfolder_name = 'exo_data/'
        filename = subfolder_name + \
            time.strftime("%Y%m%d_%H%M_") + file_ID + \
            '_BI' + '.csv'
        self.my_file = open(filename, 'w', newline='')
        self.writer = csv.DictWriter(
            self.my_file, fieldnames=self.data.big_dict.keys())
        self.writer.writeheader()

    def write_data(self, loop_time=None):
        '''Writes new row of Config data to Config file.'''
        self.data.loop_time = loop_time
        self.writer.writerow(self.data.big_dict)

    def close_file(self):
        if self.file_ID is not None:
            self.my_file.close()


if __name__ == '__main__':
    left_exo_data = exoboot.Exo.DataContainer()
    right_exo_data = exoboot.Exo.DataContainer()
    fields_to_disclude = ['accel_x', 'accel_z']
    data = BilateralDataContainer(
        left_exo_data=left_exo_data, right_exo_data=right_exo_data, fields_to_disclude=fields_to_disclude)
    writer = BilateralDataSaver(file_ID='bitest', data=data)
    writer.write_data()
