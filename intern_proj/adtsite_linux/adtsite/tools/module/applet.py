from django.core.files.base import ContentFile
from django.conf import settings
import string
import random
import os
import re
import csv


def job_id_generator(r):
    def get_client_ip(r):
        x_forwarded_for = r.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = r.META.get('REMOTE_ADDR')
        return ip

    def random_generator(size=6, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    client_IP = get_client_ip(r).replace('.', '')
    job_ID = client_IP + "_" + random_generator()
    return job_ID


def save_uploaded_file(f, path):
    full_uploading_filename = os.path.join(path, 'uploading.csv')
    fout = open(full_uploading_filename, 'wb+')
    file_content = ContentFile(f.read())
    for chunk in file_content.chunks():
        fout.write(chunk)
    fout.close()
    return full_uploading_filename


def csv_clean(ori_path, dir_path):
    lot_str = ''
    n = 0
    f_out_path = os.path.join(dir_path, 'failed_lot_uploading.csv')
    with open(f_out_path, 'w', newline='', encoding='utf8') as f1:
        f_out = csv.writer(f1)
        header = ['FNC', 'RESULT', 'LOT']
        f_out.writerow(header)
        with open(ori_path, 'r') as f:
            has_header = csv.Sniffer().has_header(f.read(1024))
            f.seek(0)
            incsv = csv.reader(f)
            if has_header:
                next(incsv)
            for row in incsv:
                lot_str = lot_str + row[2].strip() + ' '
                f_out.writerow([str(n), row[1], row[2].strip()])
                n = n + 1

    return f_out_path, lot_str.strip()


def build_python_script(localpath, remotepath, remotecsvpath, lot_id, start_date, end_date):
    read_path = os.path.join(settings.BASE_DIR, 'adhoc_in.py')
    write_path = os.path.join(localpath, 'adhoc_out.py')

    # regenerate lot id in a pattern of '000000.000','000000.000'
    def lot_id_clean(id_str):
        lot_id_list = re.split('\s+', id_str)
        temp_string = ''
        for i in lot_id_list:
            t = '\'' + i.strip() + '\'' + ','
            temp_string += t
        temp_string = temp_string[:-1]
        return temp_string

    lot_id_string = lot_id_clean(lot_id.strip())

    # Generate python script
    replacements = {'content_user_input_lot_ID': lot_id_string,
                    'content_user_input_csv_file': remotecsvpath,
                    'content_user_input_start_date': start_date,
                    'content_user_input_end_date': end_date,
                    'content_user_input_path': remotepath}

    with open(read_path) as infile, open(write_path, 'w') as outfile:
        for line in infile:
            for src, target in replacements.items():
                line = line.replace(src, target)
            outfile.write(line)

    return write_path
