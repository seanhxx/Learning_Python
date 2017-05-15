# -*- coding: utf-8 -*-
from django import forms
from django.forms.widgets import SelectDateWidget
import datetime


class QueryForm(forms.Form):
    is_checked = forms.BooleanField(required=False)
    lot_ID = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control',
                                                          'rows': 6,
                                                          'placeholder': 'Please separate lot ID by whitespace, e.g.\n'
                                                                         '000000.001 000002.001 XXXXXX.1X\n'
                                                                         '000000.001     XXXXXX.1X\n'
                                                                         '000001.001\n000002.001 \nXXXXXX.1X'}))
    upload_file = forms.FileField(required=False)
    this_year = datetime.date.today().year
    start_date = forms.DateField(widget=SelectDateWidget(years=range(this_year-1, this_year+1)))
    end_date = forms.DateField(widget=SelectDateWidget(years=range(this_year-1, this_year+1)))

    def clean_lot_ID(self):
        print('clean lot ID')
        data = self.cleaned_data['lot_ID']
        chk_state = self.cleaned_data['is_checked']
        if chk_state:
            self.fields['lot_ID'].required = True
        else:
            self.fields['lot_ID'].required = False
        return data

    def clean_upload_file(self):
        print('clean upload file')
        data = self.cleaned_data['upload_file']
        chk_state = self.cleaned_data['is_checked']
        if chk_state:
            self.fields['upload_file'].required = False
        else:
            self.fields['upload_file'].required = True
        return data

    def clean(self):
        cleaned_data = super(QueryForm, self).clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date > end_date:
            raise forms.ValidationError("Starting date should be smaller than ending date!")

        if self.fields['lot_ID'].required:
            print('lot_id')

        if self.fields['upload_file'].required:
            print('upload file')
            upload_file_name = cleaned_data.get("upload_file").name
            if not ".csv" in upload_file_name:
                raise forms.ValidationError("Uploaded file should be .csv!")

        if not self.fields['lot_ID'].required and not self.fields['upload_file'].required:
            self.fields['upload_file'].required = True
        return
