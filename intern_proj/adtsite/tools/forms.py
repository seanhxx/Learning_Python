# -*- coding: utf-8 -*-
from django import forms
from django.forms.widgets import SelectDateWidget
import datetime
# import magic
# magic.Magic(magic_file="C:/Windows/System32/magic.mgc")


class QueryForm(forms.Form):
    lot_ID = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control',
                                                          'rows': 6,
                                                          'placeholder': 'Please separate lot ID by whitespace, e.g.\n'
                                                                         '000000.001 000002.001 XXXXXX.1X\n'
                                                                         '000000.001     XXXXXX.1X\n'
                                                                         '000001.001\n000002.001 \nXXXXXX.1X'}))
    upload_file = forms.FileField()
    this_year = datetime.date.today().year
    start_date = forms.DateField(widget=SelectDateWidget(years=range(this_year-1, this_year+1)))
    end_date = forms.DateField(widget=SelectDateWidget(years=range(this_year-1, this_year+1)))

    def clean(self):
        cleaned_data = super(QueryForm, self).clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date > end_date:
            raise forms.ValidationError("Starting date should be smaller than ending date!")
        upload_file_name = cleaned_data.get("upload_file", False).name
        if not ".csv" in upload_file_name:
            raise forms.ValidationError("Uploaded file should be .csv!")
        return
