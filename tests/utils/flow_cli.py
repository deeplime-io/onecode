import os
import shutil
import tempfile
import uuid

from slugify import slugify


def _clean_flow(flow: str):
    tmp = tempfile.gettempdir()
    path = os.path.join(tmp, flow)

    if os.path.exists(path):
        shutil.rmtree(path)

    return tmp


def _generate_flow_name():
    name = f"My Flow Id_{uuid.uuid4().hex[:6]}"
    flow_name = slugify(name, lowercase=False, separator=' ')
    flow_folder = slugify(name, lowercase=False, separator='_')
    flow_id = slugify(flow_folder, separator='_')

    return flow_name, flow_folder, flow_id


def _generate_csv_file(
    flow: str,
    to_file: str,
    empty: bool = False
) -> str:
    out_file = os.path.join(flow, 'data', to_file)
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'w') as f:
        f.write("A,B,C\n")

        if not empty:
            f.write("0,1,2\n")
            f.write("3,4,5\n")

    return out_file
