from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Especialidades, DadosMedico,DatasAbertas,is_medico
from  django.contrib import messages
from django.contrib.messages import constants
from datetime import  datetime , timedelta, date
from paciente.models import Consulta, Documento
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from  django.db.models import Count
import locale

#locale.setlocale(locale.LC_ALL,'pt_BR')

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


# Create your views here.


@login_required(login_url='/usuarios/login')
def cadastro_medico(request):

    if request.method == "GET":
        if  is_medico(request.user):
            messages.add_message(request, constants.WARNING, 'Você já é um médico.')
            return redirect(reverse('abrir_horario'))
        especialidades = Especialidades.objects.all()
        return render(request, 'cadastro_medico.html', dados_medico_campos )
    elif request.method == "POST":
       
        crm = request.POST.get('crm')
        nome = request.POST.get('nome')
        cep = request.POST.get('cep')
        rua = request.POST.get('rua')
        bairro = request.POST.get('bairro')
        numero = request.POST.get('numero')
        cim = request.FILES.get('cim')
        rg = request.FILES.get('rg')
        foto = request.FILES.get('foto')
        especialidade = request.POST.get('especialidade')
        descricao = request.POST.get('descricao')
        valor_consulta = request.POST.get('valor_consulta')

        #TODO: mandar parar templates dados_medico_campos


        
        dados_medico_campos ={
            'crm': crm,
            'nome': nome,
            'cep': cep,
            'rua': rua,
            'bairro': bairro,
            'numero': numero,
            'cim': cim,
            'rg': rg,
            'foto': foto,
            'especialidade': especialidade,
            'descricao': descricao,

            'valor_consulta': valor_consulta,

        } 
        
        if not cim or not rg or not foto:

            messages.add_message(request, constants.ERROR, 'Preencha todos os campos.')
            return redirect('/medicos/cadastro_medico',dados_medico_campos)                  
        if len(crm) < 6:

            messages.add_message(request, constants.ERROR, 'CRM inválido.')
            return redirect('/medicos/cadastro_medico')
        if len(nome) < 12:

            messages.add_message(request, constants.ERROR, 'Nome inválido.')
            return redirect('/medicos/cadastro_medico')
        if len(cep) < 8:

            messages.add_message(request, constants.ERROR, 'CEP inválido.')
            return redirect('/medicos/cadastro_medico')
        if len(rua) < 8:


            messages.add_message(request, constants.ERROR, 'Rua inválida.')
            return redirect('/medicos/cadastro_medico')
        if len(bairro) < 8:

            messages.add_message(request, constants.ERROR, 'Bairro inválido.')
            return redirect('/medicos/cadastro_medico')
        if len(numero) < 1:

            messages.add_message(request, constants.ERROR, 'Número inválido.')
            return redirect('/medicos/cadastro_medico') 
        if len(descricao) < 10:


            messages.add_message(request, constants.ERROR, 'Descrição inválida.')
            return redirect('/medicos/cadastro_medico')
        
        if   len(especialidade) < 1:

            messages.add_message(request, constants.ERROR, 'Especialidade inválida.')
            return redirect('/medicos/cadastro_medico')
        


        dados_medico = DadosMedico(
            crm=crm,
            nome=nome,
            cep=cep,
            rua=rua,
            bairro=bairro,
            numero=numero,
            rg=rg,
            cedula_identidade_medica=cim,
            foto=foto,
            user=request.user,
            descricao=descricao,
            especialidade_id=especialidade,
            valor_consulta=valor_consulta
        )
        dados_medico.save()

        messages.add_message(request, constants.SUCCESS, 'Cadastro médico realizado com sucesso.')

        return redirect('/medicos/abrir_horario')


@login_required(login_url='/usuarios/login')
def abrir_horario(request):

    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')

    if request.method == "GET":
        dados_medicos = DadosMedico.objects.get(user=request.user)
        datas_abertas = DatasAbertas.objects.filter(user=request.user)
        return render(request, 'abrir_horario.html', {'dados_medicos': dados_medicos, 'datas_abertas': datas_abertas,'is_medico': is_medico(request.user)})
    elif request.method == "POST":
        data = request.POST.get('data')

        if not  data:
            messages.add_message(request, constants.ERROR, 'Digite uma data.')
            return redirect('/medicos/abrir_horario')

        data_formatada = datetime.strptime(data, "%Y-%m-%dT%H:%M")
        
        if data_formatada <= datetime.now():
            messages.add_message(request, constants.WARNING, 'A data deve ser maior ou igual a data atual.')
            return redirect('/medicos/abrir_horario')


        horario_abrir = DatasAbertas(
            data=data,
            user=request.user
        )

        horario_abrir.save()

        messages.add_message(request, constants.SUCCESS, 'Horário cadastrado com sucesso.')
        return redirect('/medicos/abrir_horario')
    


@login_required(login_url='/usuarios/login')
def consultas_medico(request):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    hoje = datetime.now().date()
     
    

    consultas_hoje = Consulta.objects.filter(data_aberta__user=request.user).filter(data_aberta__data__gte=hoje).filter(data_aberta__data__lt=hoje + timedelta(days=1)).exclude(paciente=request.user)
    

    

    consultas_restantes = Consulta.objects.exclude(id__in=consultas_hoje.values('id')).filter(data_aberta__user=request.user)


    return render(request, 'consultas_medico.html', {'consultas_hoje': consultas_hoje, 'consultas_restantes': consultas_restantes, 'is_medico': is_medico(request.user)})



@login_required(login_url='/usuarios/login')
def consulta_area_medico(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    consulta = Consulta.objects.get(id=id_consulta)
    documentos = Documento.objects.filter(consulta=consulta)

    if request.method == "GET":
        if  request.user !=  consulta.data_aberta.user:
            messages.add_message(request, constants.WARNING, 'Esse médico não pode iniciar consulta  que estava.')
            return redirect('/medicos/consultas_medico')
        
        return render(request, 'consulta_area_medico.html', {'consulta': consulta, 'documentos': documentos,'is_medico': is_medico(request.user)})  
        
    elif request.method == "POST":
        
        link = request.POST.get('link')

        if request.user !=  consulta.data_aberta.user:
            messages.add_message(request, constants.WARNING, 'Esse médico não pode iniciar essa consulta.')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}/') 

        if consulta.status == 'C':
            messages.add_message(request, constants.WARNING, 'Essa consulta já foi cancelada, você não pode inicia-la')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}/')
        elif consulta.status == "F":
            messages.add_message(request, constants.WARNING, 'Essa consulta já foi finalizada, você não pode inicia-la')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}/')
        
        consulta.link = link
        consulta.status = 'I'
        consulta.save()

        messages.add_message(request, constants.SUCCESS, 'Consulta inicializada com sucesso.')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    

@login_required(login_url='/usuarios/login')
def finalizar_consulta(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')

    consulta = Consulta.objects.get(id=id_consulta)

    if request.user !=  consulta.data_aberta.user:
        messages.add_message(request, constants.WARNING, 'Esse médico não pode finalizar essa consulta.')
        return redirect(reverse('conusultas_medico'))
    
    if consulta.status == 'I' and  consulta.data_aberta.data == datetime.now().date():
        consulta.status  = 'F'

        consulta.save()
        messages.add_message(request,constants.SUCCESS,'Essa foi finalinazar com sucesso.')
        return  redirect(f'/medicos/consulta_area_medico/{id_consulta}/')

    elif  consulta.status == 'F':
        messages.add_message(request, constants.WARNING, 'Essa consulta já foi finalizada, você não pode inicia-la')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}/')
    elif   consulta.status == 'C':
        messages.add_message(request, constants.WARNING, 'Essa consulta já foi cancelada, você não pode finilizar')

        return redirect(f'/medicos/consulta_area_medico/{id_consulta}/')
    elif    consulta.status == 'A':
        messages.add_message(request, constants.WARNING, 'Essa consulta ainda não foi inicializada, você não pode finalizar')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}/')




@login_required(login_url='/usuarios/login')
def add_documento(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    consulta = Consulta.objects.get(id=id_consulta)
    
    if consulta.data_aberta.user != request.user:
        messages.add_message(request, constants.ERROR, 'Essa consulta não é sua!')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
    
    titulo = request.POST.get('titulo')
    documento = request.FILES.get('documento')

    if not documento:
        messages.add_message(request, constants.WARNING, 'Adicione o documento.')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}/')

    documento = Documento(
        consulta=consulta,
        titulo=titulo,
        documento=documento

    )

    documento.save()

    messages.add_message(request, constants.SUCCESS, 'Documento enviado com sucesso!')
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}/')

@login_required(login_url='/usuarios/login')
@csrf_exempt
def dashboard(request):


    if not is_medico(request.user):
        return redirect('/')

    
    
    consultas_do_medico = Consulta.objects.filter(data_aberta__user=request.user)
    
    consultas_do_medico_finilazadas = consultas_do_medico.filter(status="F").filter(data_aberta__data__range=[datetime.now().date()- timedelta(weeks=52), datetime.now().date()+ timedelta(weeks=1) ]).values('data_aberta__data').annotate(quantidades_f=Count('id'))
    consultas_do_medico_canceladas = consultas_do_medico.filter(status="C").filter(data_aberta__data__range=[datetime.now().date()- timedelta(weeks=52), datetime.now().date()+ timedelta(weeks=1) ]).values('data_aberta__data').annotate(quantidades_c=Count('id'))

    data_f = [i['data_aberta__data'].strftime('%b') for i in consultas_do_medico_finilazadas]

    quantidades_f = [i['quantidades_f'] for i in consultas_do_medico_finilazadas]

    data_c =  [i['data_aberta__data'].strftime('%B') for i in consultas_do_medico_canceladas]

    quantidades_c = [i['quantidades_c'] for i in consultas_do_medico_canceladas]

    

    dados = {
       'data_c': data_c,
       'quantidades_c': quantidades_c,
       'data_f': data_f,
       'quantidades_f': quantidades_f,
       'is_medico': is_medico(request.user)
    }

   

    
    return render(request, 'dashboard.html',dados)