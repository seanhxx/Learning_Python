from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import csv
import os
from tools.forms import QueryForm
from tools.module.file_handler_pexpect import FileHandler
from tools.module.job_exerciser import JobExerciser
import tools.module.applet as myfunc
import json
import logging
from django.conf import settings

host = "fslhdppclient02.imfs.micron.com"
port = 22

# Server User ID
username = "xiaoxiang"
password = "Seanhu42"
# remotepath_root = '/home/xiaoxiang/test'
remotepath_root = "/home/hdfsbe/auto-diagnostics/server_tmp_files"


def index(request):
    if request.method == "POST":
        my_query_form = QueryForm(request.POST, request.FILES)
        if my_query_form.is_valid():
            # create job unique ID for tracking
            job_id = myfunc.job_id_generator(request)
            remotepath = os.path.join(remotepath_root, 'tmp_' + job_id)
            localpath = os.path.join(os.path.dirname(settings.BASE_DIR), "tmp_job_files", 'tmp_' + job_id)
            try:
                os.mkdir(localpath)
            except Exception as e:
                logging.warning(str(e))
                pass

            start_date = my_query_form.cleaned_data['start_date'].isoformat()
            end_date = my_query_form.cleaned_data['end_date'].isoformat()
            info_dict = {'job_id': job_id,
                         'start_date': start_date,
                         'end_date': end_date}
            request.session['info_dict'] = info_dict

            # Check input method
            chk_state = my_query_form.cleaned_data['is_checked']
            if chk_state:
                lot_ID = my_query_form.cleaned_data['lot_ID']
                raise Http404('This feature is still under development!')
            else:
                try:
                    uploaded_file = request.FILES['upload_file']
                    localcsvpath_ori = myfunc.save_uploaded_file(uploaded_file, localpath)
                    localcsvpath, lot_ID = myfunc.csv_clean(localcsvpath_ori, localpath)
                except Exception as e:
                    logging.error(str(e))
                    raise Http404("Local CSV File Handling Error: " + str(e))

            try:
                remotecsvpath = os.path.join(remotepath, 'failed_lot.csv')
                localpypath = myfunc.build_python_script(localpath, remotepath, remotecsvpath, lot_ID, start_date, end_date)
                remotepypath = os.path.join(remotepath, 'adhoc.py')
            except Exception as e:
                logging.error(str(e))
                raise Http404("Local Python Script File Handling Error: " + str(e))

            try:
                myfh = FileHandler(host, port, username, password, remotepath, localpath)
                myfh.kinit()
                myfh.su_hdfsbe()
                myfh.upload(remotecsvpath, localcsvpath)
                myfh.upload(remotepypath, localpypath)
                myfh.kill()
            except Exception as e:
                logging.error(str(e))
                raise Http404("Job Uploading Error: " + str(e))

            try:
                new_thread = JobExerciser(job_id, host, username, password, remotepath, localpath)
                new_thread.start()
            except Exception as e:
                logging.error(str(e))
                raise Http404("Job Executing Error: " + str(e))

            return HttpResponseRedirect(reverse('result', kwargs={'job_id': job_id}))
    else:
        my_query_form = QueryForm()
    return render(request, 'tools/index.html', {'form': my_query_form})


def query_result(request, job_id):
    info_dict = request.session['info_dict']
    return render(request, 'tools/result.html', {'dict': json.dumps(info_dict),
                                                 'job_id': job_id})


def download_rf(request, job_id):
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="result_rf.csv"'
        writer = csv.writer(response)
        fpout_rf = os.path.join(os.path.dirname(settings.BASE_DIR), "tmp_job_files", 'tmp_' + job_id, 'result_rf.csv')
        with open(fpout_rf, newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                writer.writerow(row)
    except FileNotFoundError:
        raise Http404("FileNotFoundError: File result_rf.csv does not exist")
    return response


def download_k(request, job_id):
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="result_k.csv"'
        writer = csv.writer(response)
        fpout_k = os.path.join(os.path.dirname(settings.BASE_DIR), "tmp_job_files", 'tmp_' + job_id, 'result_k.csv')
        with open(fpout_k, newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                writer.writerow(row)
    except FileNotFoundError:
        raise Http404("FileNotFoundError: File result_k.csv does not exist")
    return response


def download_raw(request, job_id):
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="result_raw.csv"'
        writer = csv.writer(response)
        fpout_k = os.path.join(os.path.dirname(settings.BASE_DIR), "tmp_job_files", 'tmp_' + job_id, 'result_raw.csv')
        with open(fpout_k, newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                writer.writerow(row)
    except FileNotFoundError:
        raise Http404("FileNotFoundError: File result_raw.csv does not exist")
    return response
