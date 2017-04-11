from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import csv
import os
from tools.forms import QueryForm
from tools.module.file_handler import FileHandler
from tools.module.job_exerciser import JobExerciser
import tools.module.applet as myfunc
import json

host = ""
port = 22

# Server User ID
username = ""
password = ""
serverpath_root = ''

def index(request):
    if request.method == "POST":
        my_query_form = QueryForm(request.POST, request.FILES)
        if my_query_form.is_valid():
            job_id = myfunc.job_id_generator(request)
            serverpath = serverpath_root + 'tmp_' + job_id + '/'

            lot_ID = my_query_form.cleaned_data['lot_ID']
            uploaded_file = request.FILES['upload_file']
            start_date = my_query_form.cleaned_data['start_date'].isoformat()
            end_date = my_query_form.cleaned_data['end_date'].isoformat()

            info_dict = {'job_id': job_id,
                         'start_date': start_date,
                         'end_date': end_date,
                         'upload_file': uploaded_file.name}
            request.session['info_dict'] = info_dict

            myfh = FileHandler(host, port, username, password, serverpath)
            myfh.kinit()
            myfh.upload(serverpath + 'failed_lot.csv', uploaded_file, None)
            pyscriptpath = myfunc.build_python_script(job_id, serverpath, lot_ID,
                                                      uploaded_file.name, start_date, end_date)
            myfh.upload(serverpath + 'adhoc.py', None, pyscriptpath)

            new_thread = JobExerciser(job_id, host, username, password, serverpath)
            new_thread.start()

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
        fpout_rf = os.path.join(os.path.realpath(''), 'pyscript', 'tmp_' + job_id, 'result_rf.csv')
        with open(fpout_rf, newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                writer.writerow(row)
    except FileNotFoundError:
        raise Http404("File does not exist")
    return response


def download_k(request, job_id):
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="result_k.csv"'
        writer = csv.writer(response)
        fpout_k = os.path.join(os.path.realpath(''), 'pyscript', 'tmp_' + job_id, 'result_k.csv')
        with open(fpout_k, newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                writer.writerow(row)
    except FileNotFoundError:
        raise Http404("File does not exist")
    return response
