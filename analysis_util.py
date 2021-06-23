import pandas as pd
import exoboot
from typing import Type


def populate_data_container_from_series(df: Type[pd.Series]):
    data_container = exoboot.Exo.DataContainerWithFSRs()
    for key, value in df.items():
        if hasattr(df, key):
            setattr(data_container, key, value)
    return data_container
