from django import forms


class InsertDataForm(forms.Form):
    decryption_key = forms.CharField(label="Inserisci la chiave di decrittazione:")
