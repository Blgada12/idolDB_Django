import math

from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from idolmaster.utils import productions_click_controller, auto_login_controller, productions_filter_controller

from users.models import User
from .models import Idol, Production
from .serializers import IdolSerializer
from ngdb.utils import get_idol_byId

AFTER_INDEX = 3
PAGE_INDEX = 14


class idolMain(View):
    def get(self, req):
        productions_click_controller(req)
        isLogin, user = auto_login_controller(req)
        op, selected_pro = productions_filter_controller(req)

        oi = Idol.objects

        idols = oi.filter(production=selected_pro[0])

        for i in range(1, len(selected_pro)):
            idols = idols | oi.filter(production=selected_pro[i])

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
        rDict = dict(today=today_idols, isToday=True if
        len(today_idols) > 0 else False, after=after_idols_result, productions=op.all(), selected_pro=selected_pro,
                     isLogin=isLogin, now='main', user=user)

        for i in after_date:
            after_idols_result.append(idols.filter(birth__day=i[1], birth__month=i[0]))
        return render(req, 'idoldb/index.html', rDict)


class idolAll(View):
    def get(self, req):

        productions_click_controller(req)
        isLogin, user = auto_login_controller(req)

        oi = Idol.objects
        idols = oi.all()

        # 전부 헤제되거나 처음접속이면 모두선택
        productions: str = req.GET.get('production')
        if productions:
            req.session['productions'] = productions
            return redirect('idolAll')

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

        if not req.session.get('isLogin', False):
            req.session['isLogin'] = False

        rDict = {'idols': result[PAGE_INDEX * index:PAGE_INDEX * (index + 1)], 'productions': pro_Objects,
                 'selected_pro': selected_pro, 'now_index': index + 1}

        if index > 0:
            rDict['canDown'] = index
        else:
            rDict['canDown'] = None
        if index + 2 < int(math.ceil(len(result) / PAGE_INDEX)) + 1:
            rDict['canUp'] = index + 2
        else:
            rDict['canUp'] = None
        rindex = list(set(range(index - 1, index + 4)) & set(range(1, int(math.ceil(len(result) / PAGE_INDEX)) + 1)))
        rindex.sort()
        rDict['full_index'] = rindex
        rDict['now'] = 'all'

        return render(req, 'idoldb/all.html', rDict)


class idolSearch(View):
    def get(self, req, value=''):
        if value == '':
            return redirect('idolAll')
        should_refresh = False
        if req.session.get('last_search', False):
            if not req.session.get('last_search') == value:
                req.session['index_search'] = 1
                should_refresh = True
        else:
            req.session['index_search'] = 1
            should_refresh = True
        req.session['last_search'] = value
        # 인덱싱 기능
        index: str = req.GET.get('index')
        if index:
            req.session['index_search'] = index
            should_refresh = True

        if not req.session.get('index_search', False):
            req.session['index_search'] = 1
            should_refresh = True

        index: int = int(req.session['index_search']) - 1

        # 분류 추가
        clicked: str = req.GET.get('clicked_search')
        if clicked:
            pro_selected: list = req.session.get('productions')
            pro_selected.append(clicked)
            pro_selected.sort()
            req.session['productions'] = pro_selected
            req.session['index_search'] = 1

            should_refresh = True

        # 분류 제외
        unclicked: str = req.GET.get('unclicked')
        if unclicked:
            pro_selected: list = req.session.get('productions')
            pro_selected.remove(unclicked)
            req.session['productions'] = pro_selected
            req.session['index_search'] = 1

            should_refresh = True

        # 전부 헤제되거나 처음접속이면 모두선택
        productions: str = req.GET.get('production')
        if productions:
            req.session['productions'] = productions
            should_refresh = True

        if should_refresh:
            return redirect('idolSearch', value)

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

        if not index in range(1, int(math.ceil(len(result) / PAGE_INDEX)) + 1):
            req.session['index_search'] = 1
            index = 0

        rDict = {'idols': result[PAGE_INDEX * index:PAGE_INDEX * (index + 1)], 'productions': pro_Objects,
                 'selected_pro': selected_pro, 'now_index': index + 1,
                 'search_value': value, 'is_none': len(result) == 0}

        if index > 0:
            rDict['canDown'] = index
        else:
            rDict['canDown'] = None
        if index + 2 < int(math.ceil(len(result) / PAGE_INDEX)) + 1:
            rDict['canUp'] = index + 2
        else:
            rDict['canUp'] = None
        rindex = list(set(range(index - 1, index + 4)) & set(range(1, int(math.ceil(len(result) / PAGE_INDEX)) + 1)))
        rindex.sort()

        rDict['full_index'] = rindex
        rDict['now'] = 'search'

        return render(req, 'idoldb/search.html', rDict)


class idolDetail(View):
    def get(self, req, idol_id):
        isLogin, user = auto_login_controller(req)
        idol = get_idol_byId(idol_id)
        rDict = {'idol': idol, 'now': 'detail', 'isLogin': isLogin, 'user': user}

        return render(req, 'idoldb/detail.html', rDict)

    def post(self, req, idol_id):
        isLogin, user = auto_login_controller(req)
        idol = get_idol_byId(idol_id)
        user.myIdol = idol
        user.save()
        rDict = {'idol': idol, 'now': 'detail', 'isLogin': isLogin, 'user': user}

        return render(req, 'idoldb/detail.html', rDict)


class IdolViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    oi = Idol.objects
    queryset = oi.all()
    serializer_class = IdolSerializer

    def list(self, req, *args, **kwargs):
        queryset = self.get_queryset()
        if req.GET.get('id'):
            result = queryset.filter(id=req.GET.get('id'))
        else:
            Qs = Q(Q(KoreanName__contains=req.GET.get('korean_name') if req.GET.get('korean_name') else '') \
                   & Q(JapaneseName__contains=req.GET.get('japanese_name') if req.GET.get('japanese_name') else '') \
                   & Q(KanjiName__contains=req.GET.get('kanji_name') if req.GET.get('kanji_name') else '')
                   )

            if req.GET.get('productions'):
                po = Production.objects
                Qp = Q()
                for i in req.GET.get('productions').split(','):
                    now_production = po.get(id=i)
                    Qp |= Q(production=now_production)
                Qs &= Qp

            result = queryset.filter(Qs)

        paginator = PageNumberPagination()

        serializer = IdolSerializer(paginator.paginate_queryset(result, req), many=True)

        return paginator.get_paginated_response(serializer.data)
