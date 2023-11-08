import pandas as pd
import os
import pickle

def save_file_csv(
    data_frame:pd.DataFrame, file_name, file_path="", idx=False, hdr=True, encoding="CP949"
):
    makedirs(file_path)
    data_frame.to_csv(
        f"{file_path}{file_name}", index=idx, header=hdr, encoding=encoding
    )
    return True

def append_file_csv(
    data_frame:pd.DataFrame, file_name, file_path="", idx=False, hdr=False, encoding="CP949", mode='a'
):
    makedirs(file_path)
    data_frame.to_csv(
        f"{file_path}{file_name}", index=idx, header=hdr, encoding=encoding, mode=mode
    )
    return True

def read_file_csv(file_name, file_path="", hdr=0, encoding="CP949", nrows=None):
    return pd.read_csv(f"{file_path}{file_name}", header=hdr, encoding=encoding, nrows=nrows)


def save_file_pickle(save_file, file_name, file_path=""):
    makedirs(file_path)
    with open(f"{file_path}{file_name}.pickle", "wb") as f:
        pickle.dump(save_file, f)
        return True


def read_file_pickle(file_name, file_path=""):
    with open(f"{file_path}{file_name}.pickle", "rb") as f:
        result = pickle.load(f)
        return result


def file_exist(file_name, file_path=""):
    return os.path.isfile(f"{file_path}{file_name}")


def makedirs(path):
    if path != "":
        try:
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise

def get_data_frame(file_name, file_path="", nrows=None):
    if (
        file_exist(
            file_name,
            file_path,
        )
        == True
    ):
        return pd.DataFrame(read_file_csv(file_name, file_path, hdr=0, nrows=nrows))
    else:
        return pd.DataFrame()