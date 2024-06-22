from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from django.contrib.messages import constants
from  django.contrib import auth

# Create your views here.

def cadastro(request):
    if request.method == "GET":
        if  request.user.is_authenticated:
            return redirect('/plataforma/home')
        return render(request, 'cadastro.html')
    
    elif request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get("email")
        senha = request.POST.get("senha")
        confirmar_senha = request.POST.get('confirmar_senha')

        users = User.objects.filter(username=username)

        if len(username.strip())  < 4:

            messages.add_message(request, constants.ERROR, 'Nome de usuario inválido')
            return redirect(reverse('cadastro'))
        
        if len(email.strip())  < 20:

            messages.add_message(request, constants.ERROR, 'Email inválido')
            return redirect(reverse('cadastro'))

        if users.exists():

            messages.add_message(request,constants.ERROR,'Usuario já existe')
            return redirect(reverse('cadastro'))
        
        if  senha != confirmar_senha:
            messages.add_message(request, constants.ERROR, 'As senhas não coincidem')
            return redirect(reverse('cadastro'))
        
        if len(senha) < 6:
            messages.add_message(request, constants.ERROR, 'A senha deve ter no minimo 6 caracteres')
            return redirect(reverse('cadastro'))
        
        try:

            user = User.objects.create_user(username=username, email=email, password=senha)
            user.save()
            messages.add_message(request, constants.SUCCESS, 'Usuario cadastrado com sucesso')
            return redirect(reverse('login'))
        
        except:
            messages.add_message(request,constants.ERROR,'Erro interno do sistema, tente novamente mais tarde')
            return redirect(reverse('cadastro'))
        
def login_view(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/plataforma/home')
        return render(request, 'login.html')
    
    elif request.method == "POST":

        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = auth.authenticate(username=username, password=senha)

        if not user:
            messages.add_message(request, constants.ERROR, 'Usuario ou senha invalidos')
            return redirect(reverse('login'))

        else:
            auth.login(request, user)
            return redirect(reverse('home'))
        
def logout(request):
    if  request.method == "GET":
        if  request.user.is_authenticated:
            auth.logout(request)
            return redirect(reverse('login'))
        else:

            messages.add_message(request, constants.ERROR, 'Você não está logado')

            return redirect(reverse('login'))
        
        