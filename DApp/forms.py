from django import forms


class InsertDataForm(forms.Form):
    wallet_address = forms.CharField(label="Inserisci l'indirizzo del tuo wallet:")
    private_key = forms.CharField(label="Inserisci la chiave privata:")
