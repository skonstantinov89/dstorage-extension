from django import forms

class DocumentForm(forms.Form):
    recordsCount = forms.CharField(label='',  widget=forms.TextInput(attrs={'placeholder': 'Брой записи'}),required=True)
    docfile = forms.FileField(label='Прикачи файл', required=True)