from django.db import models
from django.utils import timezone


class Production(models.Model):
    name = models.TextField()
    logo = models.ImageField()

    def __str__(self):
        return self.name


class Idol(models.Model):
    production = models.ForeignKey(Production, on_delete=models.CASCADE)
    JapaneseName = models.CharField(max_length=30)
    KanjiName = models.CharField(max_length=30)
    KoreanName = models.CharField(max_length=30)
    age = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    birth = models.DateField()
    bloodType = models.CharField(max_length=5, blank=True, null=True)
    BWH = models.CharField(max_length=20, blank=True, null=True)
    hobby = models.TextField(blank=True, null=True)
    bornPlace = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=10)
    voice = models.CharField(max_length=30)
    mainPicture = models.ImageField()
    signPicture = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.KoreanName


class BeforeIdol(models.Model):
    nowIdol = models.ForeignKey(Idol, on_delete=models.CASCADE)
    production = models.ForeignKey(Production, on_delete=models.CASCADE)
    JapaneseName = models.CharField(max_length=30)
    KanjiName = models.CharField(max_length=30)
    KoreanName = models.CharField(max_length=30)
    age = models.IntegerField()
    height = models.IntegerField()
    weight = models.IntegerField()
    birth = models.DateField()
    bloodType = models.CharField(max_length=5)
    BWH = models.CharField(max_length=20)
    hobby = models.TextField()
    bornPlace = models.TextField()
    Color = models.CharField(max_length=10)
    Voice = models.CharField(max_length=30)
    mainPicture = models.ImageField()
    signPicture = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.KoreanName