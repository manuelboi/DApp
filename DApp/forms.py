from django import forms


class InsertDataForm(forms.Form):
    private_key = forms.CharField(label="Inserisci la chiave privata:")
