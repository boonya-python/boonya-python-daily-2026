import os
import time


def safe_filename(name):
    return "".join(c for c in name if c not in r'\/:*?"<>|')


def get_timestamp():
    return time.strftime('%Y%m%d_%H%M%S')


def build_output_path(input_path, output_dir=None):
    if output_dir is None:
        output_dir = os.path.dirname(input_path)

    os.makedirs(output_dir, exist_ok=True)

    filename = os.path.basename(input_path)
    name_without_ext = os.path.splitext(filename)[0]
    safe_name = safe_filename(name_without_ext)
    timestamp = get_timestamp()
    output_filename = f'{safe_name}_{timestamp}.pdf'

    return os.path.join(output_dir, output_filename)