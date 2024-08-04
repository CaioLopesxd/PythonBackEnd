from django.db import models

# Create your models here.

class Post(models.Model):
    id_post = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100)
    conteudo = models.TextField()
