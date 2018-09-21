from django.shortcuts import render
from .models import Idol
from .utils import get_idol_byId
from django.utils import timezone

AFTER_INDEX = 2


def idol_main(req):
    idols = Idol.objects.all()
    today_time = timezone.now()
    today_idols = idols.filter(birth=today_time)

    before_idols = idols.filter(birth__lt=today_time)
    for idol in before_idols:
        idol.birth = idol.birth.replace(today_time.year + 1, idol.birth.month, idol.birth.day)
        idol.save()

    after_idols = idols.filter(birth__gt=today_time)

    after_date = list()
    for idol in after_idols:
        isIn = False
        for i in after_date:
            if i == (idol.birth.month, idol.birth.day):
                isIn = True
                break
        if not isIn:
            after_date.append((idol.birth.month, idol.birth.day))
        if AFTER_INDEX == len(after_date):
            break

    after_idols_result = list()

    for i in after_date:
        after_idols_result.append(idols.filter(birth__day=i[1], birth__month=i[0]))

    return render(req, 'idoldb/index.html', {'today': today_idols, 'isToday': True if
    len(today_idols) > 0 else False, 'after': after_idols_result})


def idol_all(req):
    idols = Idol.objects.all()
    return render(req, 'idoldb/idol_all.html', {'idols': idols})


def idol_detail(req, idol_id):
    idol = get_idol_byId(idol_id)
    return render(req, 'idoldb/idol_detail.html', {'idol': idol})
