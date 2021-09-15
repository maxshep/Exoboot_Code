from dataclasses import dataclass, field, InitVar


@dataclass
class DataContainer:
    '''A nested dataclass within Exo, reserving space for instantaneous data.'''
    do_include_FSRs: InitVar[bool] = False
    do_include_sync: InitVar[bool] = False
    do_include_did_slip: InitVar[bool] = False
    do_include_gen_vars: InitVar[bool] = False
    # Optional fields--init in __post__init__
    heel_fsr: bool = field(init=False)
    toe_fsr: bool = field(init=False)
    did_slip: bool = field(init=False)
    sync: bool = field(init=False)
    gen_var1: float = field(init=False)
    gen_var2: float = field(init=False)
    gen_var3: float = field(init=False)

    def __post_init__(self, do_include_FSRs, do_include_did_slip, do_include_sync, do_include_gen_vars):
        if do_include_FSRs:
            self.heel_fsr = False
            self.toe_fsr = False
        if do_include_did_slip:
            self.did_slip = False
        if do_include_gen_vars:
            print('adding gen vars...')
            self.gen_var1 = None
            self.gen_var2 = None
            self.gen_var3 = None
        if do_include_sync:
            print('adding sync...')
            self.sync = False


my_data = DataContainer(
    do_include_FSRs=False, do_include_did_slip=False,
    do_include_gen_vars=True, do_include_sync=True)

print(my_data.__dict__)
