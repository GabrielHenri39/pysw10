from django.shortcuts import render, redirect
from medico.models import DadosMedico, Especialidades, DatasAbertas, is_medico
from django.contrib.auth.decorators import login_required
from datetime import datetime , timedelta
from django.contrib import messages
from django.contrib.messages import constants
from .models import Consulta,Documento
from django.db import transaction
from django.urls import reverse


# Create your views here.

@login_required(login_url='/usuarios/login')
def home(request): 
    
    if request.method == "GET":
        medico_filtrar =  request.GET.get('medico')
        especialidades_filtrar = request.GET.getlist('especialidades')
        medicos = DadosMedico.objects.all()
        if medico_filtrar:
            medicos = medicos.filter(nome__icontains=medico_filtrar)
        
        if especialidades_filtrar:
            medicos = medicos.filter(especialidade_id__in=especialidades_filtrar)

        especialidades = Especialidades.objects.all()
        consulta = Consulta.objects.all()
        consultas_medico = []
        consultas = []


        if consulta.filter(paciente=request.user):
            
            consultas = consulta.filter(status="A").filter(paciente=request.user) \
                    .filter(data_aberta__data__lte=datetime.today().date() +timedelta(days=7))

        if is_medico(request.user):
            consultas_medico = consulta.filter(status="A").filter(data_aberta__user=request.user) \
                .filter(data_aberta__data__lte=datetime.today().date() + timedelta(days=7))
            
         

            

            
        
        return render(request, 'home.html',{'medicos':medicos,'especialidades': especialidades,'is_medico': is_medico(request.user),'consultas':consultas,'consultas_medico':consultas_medico})


@login_required(login_url='/usuarios/login')
def escolher_horario(request, id_dados_medicos):
    if request.method == "GET":
        medico = DadosMedico.objects.get(id=id_dados_medicos) 
        datas_abertas = DatasAbertas.objects.filter(user=medico.user).filter(data__gte=datetime.now()).filter(agendado=False)
        return render(request, 'escolher_horario.html', {'medico': medico, 'datas_abertas': datas_abertas,'is_medico': is_medico(request.user)})
    
@login_required(login_url='/usuarios/login')
def agendar_horario(request, id_data_aberta):
    if request.method == "GET":
        data_aberta = DatasAbertas.objects.get(id=id_data_aberta)
    

        if data_aberta.user == request.user:

            messages.add_message(request, constants.ERROR, 'Você não pode agendar um horário com você mesmo.')
            return redirect(reverse('home'))
        
        with  transaction.atomic():
            horario_agendado = Consulta(
                paciente=request.user,
                data_aberta=data_aberta
            )

            horario_agendado.save()
       
            data_aberta.agendado = True
            
            data_aberta.save()

       

        messages.add_message(request, constants.SUCCESS, 'Horário agendado com sucesso.')

        return redirect(reverse('minhas_consultas'))
    

@login_required(login_url='/usuarios/login')
def minhas_consultas(request):
    if request.method == "GET":
        
        minhas_consultas = Consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=datetime.now())

        
        
        especialidades_filtrar = request.GET.get('especialidades')
        data_filtrar = request.GET.get('data')
        
       

        if  especialidades_filtrar:
            
           minhas_consultas = minhas_consultas.filter(data_aberta__user__dadosmedico__especialidade__especialidade__icontains=especialidades_filtrar)


        if data_filtrar:

            minhas_consultas = minhas_consultas.filter(data_aberta__data__gte=data_filtrar)
        return render(request, 'minhas_consultas.html', {'minhas_consultas': minhas_consultas,'is_medico': is_medico(request.user)})


@login_required(login_url='/usuarios/login')
def consulta(request, id_consulta):
    if request.method == 'GET':
        
        consulta = Consulta.objects.get(id=id_consulta)
        dado_medico = DadosMedico.objects.get(user=consulta.data_aberta.user)
        documendos = Documento.objects.filter(consulta=consulta)

        if request.user != consulta.paciente:
            messages.add_message(request, constants.ERROR, 'Esse horário não é seu!')
            return redirect(reverse('minhas_consultas'))

        return render(request, 'consulta.html', {'consulta': consulta, 'dado_medico': dado_medico, 'is_medico': is_medico(request.user),'documentos':documendos})


@login_required(login_url='usuarios/login')
def cancelar_consulta(request, id_consulta):
    
        consulta = Consulta.objects.get(id=id_consulta)
        if request.user != consulta.paciente:
            messages.add_message(request, constants.ERROR, 'Esse horário não é seu!')
            return redirect(reverse('minhas_consultas'))

        if consulta.status == 'A':

            consulta.status = 'C'
            data_abertaa = DatasAbertas.objects.get(id=consulta.data_aberta.id)
            data_abertaa.agendado  = False
            data_abertaa.save()
        
            consulta.save()
            messages.add_message(request, constants.SUCCESS, 'Consulta cancelada com sucesso.')
        elif  consulta.status == 'C':

            messages.add_message(request, constants.ERROR, 'Consulta já foi cancelada.')

        elif consulta.status == 'F':


            messages.add_message(request, constants.ERROR, 'Consulta já foi finalizada.')

        elif consulta.status == "I":


            messages.add_message(request, constants.ERROR, 'Consulta já foi iniciada.')

           

        
        return redirect(reverse('minhas_consultas'))