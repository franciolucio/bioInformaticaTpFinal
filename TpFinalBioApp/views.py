import json
import os
<<<<<<< HEAD
import re
from django.core import serializers
from subprocess import Popen, PIPE
=======
import platform
import subprocess
>>>>>>> b20dda35eca5a3ebd166dc3b974fd557006cf40e

import gmplot
from Bio import SeqIO, AlignIO
from Bio.Align.Applications import ClustalwCommandline
from django.contrib import messages
from django.shortcuts import render, redirect

from TpFinalBioApp.forms import SecuenceForm
# Create your views here.
from TpFinalBioApp.handler import handle_uploaded_file, SequenceHandler
from TpFinalBioApp.models import Secuence


def home(request):
    return render(request,"TpFinalBioApp/home.html")

def map(request):
    data = serializers.serialize('json', Secuence.objects.all(), fields=('latitud','longitud'))
    return render(request,"TpFinalBioApp/map.html",{'markers': data})

def upload(request):
    if request.method == 'POST':
        form = SecuenceForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            form.save()
            return redirect('UploadedSecuence')
    else:
        form = SecuenceForm()
    return render(request,"TpFinalBioApp/upload.html", {

        'form': form
    })



def uploaded_secuence(request):
    path = 'secuences/secuence.fasta'

    handler = SequenceHandler()
    handler.validate_sequences(path)

    fasta_sequences = SeqIO.parse(open(path, 'r'), 'fasta')

    if not handler.has_errors:
        for fasta in handler.dic_data:
            coordenadas = convertDirectionToCoordinates(fasta['loc'])
            fasta_to_insert = Secuence()
            fasta_to_insert.address = fasta['loc']
            fasta_to_insert.latitud = coordenadas[0]
            fasta_to_insert.longitud = coordenadas[1]
            fasta_to_insert.bio_id = fasta['gb']
            fasta_to_insert.content = fasta['seq']
            fasta_to_insert.length = len(fasta['seq'])
            fasta_to_insert.save()
            
        clustalw_exe = r"C:\Program Files (x86)\ClustalW2\clustalw2.exe"
        clustalw_cline = ClustalwCommandline(clustalw_exe, infile=path, output='CLUSTAL')
        assert os.path.isfile(clustalw_exe), "Clustal W executable missing"
        stdout, stderr = clustalw_cline()
        alignment = AlignIO.read('secuences/secuence.aln', "clustal")
        print('alineamiento \n' + str(alignment))


        cmd = ['powershell.exe', '-ExecutionPolicy', 'ByPass', '-File', 'secuences/scripts/armado del arbol.ps1']
        ec = subprocess.call(cmd)
        print("Powershell returned: {0:d}".format(ec))


        messages.success(request, f"El archivo se ha subido correctamente")
        print(platform.system())
        return render(request, "TpFinalBioApp/uploaded_secuence.html", {'fasta_sequences': fasta_sequences})
    else:
        messages.error(request, f"El archivo no es correcto. " + handler.error_message)
        return redirect('Home')


def convertDirectionToCoordinates(self, direction):
    apikey = 'AIzaSyAqJwGQtaGHY5Bm56dMzfcRgRRQ9uCn8G8'
    return gmplot.GoogleMapPlotter.geocode(direction, apikey=apikey)