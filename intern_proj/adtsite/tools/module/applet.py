import string
import random
import os
import re
import logging


def get_client_ip(r):
    x_forwarded_for = r.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = r.META.get('REMOTE_ADDR')
    return ip


def job_id_generator(r):
    def random_generator(size=6, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
    client_IP = get_client_ip(r).replace('.', '')
    job_ID = client_IP + "_" + random_generator()
    return job_ID


def build_python_script(job_id, serverpath, lot_id, csv_name, start_date, end_date):
    source_path = os.path.realpath('')
    input_path = os.path.join(source_path, 'adhoc_in.py')
    output_path = os.path.join(source_path, 'pyscript', 'tmp_' + job_id, 'adhoc_out.py')
    try:
        os.mkdir(os.path.join(source_path, 'pyscript', 'tmp_' + job_id))
    except FileExistsError:
        logging.warning("The current path is existing!")

    # regenerate lot id in a pattern of '000000.000','000000.000'
    def lot_id_clean(id_str):
        lot_id_list = re.split('\s+', id_str)
        temp_string = ''
        for i in lot_id_list:
            t = '\'' + i.strip() + '\'' + ','
            temp_string += t
        temp_string = temp_string[:-1]
        return temp_string

    lot_id_string = lot_id_clean(lot_id)

    # python script generation
    replacements = {'content_user_input_lot_ID': lot_id_string,
                    'content_user_input_csv_file': serverpath + 'failed_lot.csv',
                    'content_user_input_start_date': start_date,
                    'content_user_input_end_date': end_date,
                    'content_user_input_path': serverpath}

    with open(input_path) as infile, open(output_path, 'w') as outfile:
        for line in infile:
            for src, target in replacements.items():
                line = line.replace(src, target)
            outfile.write(line)

    return output_path
