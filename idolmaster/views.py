from django.shortcuts import render, redirect
from .models import Idol, Production
from .utils import get_idol_byId
from django.utils import timezone
import math

AFTER_INDEX = 3
PAGE_INDEX = 14


def idol_main(req):
    productions: str = req.GET.get('productions')
    if productions:
        req.session['productions'] = productions.split(',')
        return redirect(idol_main)

    clicked: str = req.GET.get('clicked')
    if clicked:
        pro_selected: list = req.session.get('productions')
        pro_selected.append(clicked)
        pro_selected.sort()
        req.session['productions'] = pro_selected

        return redirect(idol_main)

    unclicked: str = req.GET.get('unclicked')
    if unclicked:
        pro_selected: list = req.session.get('productions')
        pro_selected.remove(unclicked)
        req.session['productions'] = pro_selected

        return redirect(idol_main)

    pro_Objects = Production.objects.all()
    selected_pro = list()
    if req.session.get('productions', False):
        for i in req.session.get('productions'):
            selected_pro.append(Production.objects.get(id=int(i)))
    else:
        tmp = list()
        for i in pro_Objects:
            tmp.append(str(i.id))
            selected_pro.append(i)
        req.session['productions'] = tmp

    idols = Idol.objects.all().filter(production=selected_pro[0])

    for i in range(1, len(selected_pro)):
        idols = idols | Idol.objects.all().filter(production=selected_pro[i])

    today_time = timezone.now()
    today_idols = idols.filter(birth=today_time)

    before_idols = idols.filter(birth__lt=today_time)
    for idol in before_idols:
        idol.birth = idol.birth.replace(today_time.year + 1, idol.birth.month, idol.birth.day)
        idol.save()

    after_idols = idols.filter(birth__gt=today_time).order_by('birth')

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
    len(today_idols) > 0 else False, 'after': after_idols_result, 'productions': pro_Objects,
                                             'selected_pro': selected_pro})


def idol_all(req):
    should_refresh = False
    # 인덱싱 기능
    index: str = req.GET.get('index')
    if index:
        req.session['index'] = index
        should_refresh = True

    if not req.session.get('index', False):
        req.session['index'] = 1

    index: int = int(req.session['index']) - 1

    # 분류 추가
    clicked: str = req.GET.get('clicked')
    if clicked:
        pro_selected: list = req.session.get('productions')
        pro_selected.append(clicked)
        pro_selected.sort()
        req.session['productions'] = pro_selected
        req.session['index'] = 1

        should_refresh = True

    # 분류 제외
    unclicked: str = req.GET.get('unclicked')
    if unclicked:
        pro_selected: list = req.session.get('productions')
        pro_selected.remove(unclicked)
        req.session['productions'] = pro_selected
        req.session['index'] = 1

        should_refresh = True

    if should_refresh:
        return redirect(idol_all)

    idols = Idol.objects.all()

    # 전부 헤제되거나 처음접속이면 모두선택
    productions: str = req.GET.get('production')
    if productions:
        req.session['productions'] = productions
        return redirect(idol_all)

    pro_Objects = Production.objects.all()
    result = list()

    selected_pro = list()
    if req.session.get('productions', False):
        for i in req.session.get('productions'):
            selected_pro.append(Production.objects.get(id=int(i)))
    else:
        tmp = list()
        for i in pro_Objects:
            tmp.append(str(i.id))
            selected_pro.append(i)
        req.session['productions'] = tmp

    for i in selected_pro:
        result.extend(idols.filter(production=i))

    return render(req, 'idoldb/idol_all.html',
                  {'idols': result[PAGE_INDEX * index:PAGE_INDEX * (index + 1)], 'productions': pro_Objects,
                   'selected_pro': selected_pro,
                   'full_index': range(1, int(math.ceil(len(result) / PAGE_INDEX)) + 1), 'now_index': index + 1})


def idol_search(req, value=''):
    if value == '':
        return redirect(idol_all)
    should_refresh = False
    if req.session.get('last_search', False):
        if req.session.get('last_search') == value:
            pass
        else:
            req.session['index'] = 1
    else:
        req.session['index'] = 1
    req.session['last_search'] = value
    # 인덱싱 기능
    index: str = req.GET.get('index')
    if index:
        req.session['index'] = index
        should_refresh = True

    if not req.session.get('index', False):
        req.session['index'] = 1

    index: int = int(req.session['index']) - 1

    # 분류 추가
    clicked: str = req.GET.get('clicked')
    if clicked:
        pro_selected: list = req.session.get('productions')
        pro_selected.append(clicked)
        pro_selected.sort()
        req.session['productions'] = pro_selected
        req.session['index'] = 1

        should_refresh = True

    # 분류 제외
    unclicked: str = req.GET.get('unclicked')
    if unclicked:
        pro_selected: list = req.session.get('productions')
        pro_selected.remove(unclicked)
        req.session['productions'] = pro_selected
        req.session['index'] = 1

        should_refresh = True

    # 전부 헤제되거나 처음접속이면 모두선택
    productions: str = req.GET.get('production')
    if productions:
        req.session['productions'] = productions
        should_refresh = True

    if should_refresh:
        return redirect(idol_search, value)

    idols = Idol.objects.all()

    idols = idols.filter(KoreanName__icontains=value)

    pro_Objects = Production.objects.all()
    result = list()

    selected_pro = list()
    if req.session.get('productions', False):
        for i in req.session.get('productions'):
            selected_pro.append(Production.objects.get(id=int(i)))
    else:
        tmp = list()
        for i in pro_Objects:
            tmp.append(str(i.id))
            selected_pro.append(i)
        req.session['productions'] = tmp

    for i in selected_pro:
        result.extend(idols.filter(production=i))

    return render(req, 'idoldb/idol_search.html',
                  {'idols': result[PAGE_INDEX * index:PAGE_INDEX * (index + 1)], 'productions': pro_Objects,
                   'selected_pro': selected_pro,
                   'full_index': range(1, int(math.ceil(len(result) / PAGE_INDEX)) + 1), 'now_index': index + 1,
                   'search_value': value, 'is_none': len(result) == 0})


def idol_detail(req, idol_id):
    idol = get_idol_byId(idol_id)
    return render(req, 'idoldb/idol_detail.html', {'idol': idol})
