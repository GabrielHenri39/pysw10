from django.db import models
from django.contrib.auth.models import User
from medico.models import DatasAbertas
from datetime import datetime, timedelta


# Create your models here.


class Consulta(models.Model):
    status_choices = (
        ('A', 'Agendada'),
        ('F', 'Finalizada'),
        ('C', 'Cancelada'),
        ('I', 'Iniciada')

    )
    paciente = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    data_aberta = models.ForeignKey(DatasAbertas, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=1, choices=status_choices, default='A')
    link = models.URLField(null=True, blank=True)
    
    @property
    def quanto_falta_consulta(self):

       res = self.data_aberta.data.day -  datetime.now().day
       horias=  f"{self.data_aberta.data.hour}:{self.data_aberta.data.minute:02d}"
       if res > 1:
           return f"em {res} dias"
       elif res == 1:
           return f"em {res} dia"
       elif  res == 0:
           return f"Hoje às {horias}"
       
       
       

    def __str__(self):
        return self.paciente.username
    

class Documento(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.DO_NOTHING)
    titulo = models.CharField(max_length=30)
    documento = models.FileField(upload_to='documentos')

    def __str__(self):
        return self.titulo