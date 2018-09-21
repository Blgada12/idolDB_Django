from django.shortcuts import render
from .models import Idol
from .utils import get_idol_byId


def idol_main(req):
    idols = Idol.objects.all()
    return render(req, 'idoldb/index.html', {})


def idol_all(req):
    idols = Idol.objects.all()
    return render(req, 'idoldb/idol_all.html', {'idols': idols})


def idol_detail(req, idol_id):
    idol = get_idol_byId(idol_id)
    return render(req, 'idoldb/idol_detail.html', {'idol': idol})
