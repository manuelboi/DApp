from django.http import HttpResponse
from django.shortcuts import render
from DApp.Classes.Wallet import Wallet
from DApp.forms import *


def homepage(request):
    if request.method == "POST":
        insert_data_form = InsertDataForm(request.POST)
        if insert_data_form.is_valid():
            decryption_key = insert_data_form.cleaned_data['decryption_key']
            wallet = Wallet(decryption_key)
            wallet.request_data()
            return render(request, "showData.html", {"wallet": wallet})
        else:
            return HttpResponse("Errore nell'inserimento dei dati")
    else:
        insert_data_form = InsertDataForm()
    return render(request, "home.html", {"form": insert_data_form})


def showdata(request):
    return render(request, "showData.html")
