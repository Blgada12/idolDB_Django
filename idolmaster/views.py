import math
from datetime import datetime, timedelta, time
import uuid

from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Idol, Production, Account, CameLog
from .util import get_token, get_sha512
from .utils import get_idol_byId

from rest_framework import generics, viewsets, permissions
from .serializers import IdolSerializer
from rest_framework.decorators import action

from django.views import View

AFTER_INDEX = 3
PAGE_INDEX = 14


class idolMain(View):
    def get(self, req):
        productions: str = req.GET.get('productions')
        if productions:
            req.session['productions'] = productions.split(',')
            return redirect(self.as_view())

        clicked: str = req.GET.get('clicked')
        if clicked:
            pro_selected: list = req.session.get('productions')
            pro_selected.append(clicked)
            pro_selected.sort()
            req.session['productions'] = pro_selected

            return redirect('idolMain')

        unclicked: str = req.GET.get('unclicked')
        if unclicked:
            pro_selected: list = req.session.get('productions')
            pro_selected.remove(unclicked)
            req.session['productions'] = pro_selected

            return redirect('idolMain')

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
        rDict = {'today': today_idols, 'isToday': True if
        len(today_idols) > 0 else False, 'after': after_idols_result, 'productions': pro_Objects,
                 'selected_pro': selected_pro}
        if not req.session.get('isLogin', False):
            req.session['isLogin'] = False
        if req.session['isLogin']:
            token = req.session['token']
            rDict['token'] = token

            o = Account.objects
            if o.filter(token=token).exists():
                rDict['user'] = o.get(token=token)
            else:
                req.session['isLogin'] = False

        rDict['isLogin'] = req.session['isLogin']
        rDict['now'] = 'main'
        for i in after_date:
            after_idols_result.append(idols.filter(birth__day=i[1], birth__month=i[0]))
        return render(req, 'idoldb/index.html', rDict)


class idolAll(View):
    def get(self, req):
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
            return redirect('idolAll')

        idols = Idol.objects.all()

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
        if not req.session.get('isLogin', False):
            req.session['isLogin'] = False
        if req.session['isLogin']:
            token = req.session['token']
            rDict['token'] = token

            o = Account.objects
            if o.filter(token=token).exists():
                rDict['user'] = o.get(token=token)
            else:
                req.session['isLogin'] = False

        rDict['isLogin'] = req.session['isLogin']
        rDict['now'] = 'all'

        return render(req, 'idoldb/idol_all.html', rDict)


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

        if not req.session.get('isLogin', False):
            req.session['isLogin'] = False
        if req.session['isLogin']:
            token = req.session['token']
            rDict['token'] = token

            o = Account.objects
            if o.filter(token=token).exists():
                rDict['user'] = o.get(token=token)
            else:
                req.session['isLogin'] = False

        rDict['isLogin'] = req.session['isLogin']
        rDict['now'] = 'search'

        return render(req, 'idoldb/idol_search.html', rDict)


class idolDetail(View):
    def get(self, req, idol_id):
        idol = get_idol_byId(idol_id)
        rDict = {'idol': idol}
        if not req.session.get('isLogin', False):
            req.session['isLogin'] = False
        if req.session['isLogin']:
            token = req.session['token']
            rDict['token'] = token

            o = Account.objects
            if o.filter(token=token).exists():
                rDict['user'] = o.get(token=token)
            else:
                req.session['isLogin'] = False

        rDict['isLogin'] = req.session['isLogin']
        rDict['now'] = 'detail'
        return render(req, 'idoldb/idol_detail.html', rDict)

    def post(self, req, idol_id):
        idol = get_idol_byId(idol_id)
        rDict = {'idol': idol}
        if not req.session.get('isLogin', False):
            req.session['isLogin'] = False
        if req.session['isLogin']:
            token = req.session['token']
            rDict['token'] = token

            o = Account.objects
            if o.filter(token=token).exists():
                user = o.get(token=token)
                user.myIdol = idol
                user.save()
                rDict['user'] = o.get(token=token)
            else:
                req.session['isLogin'] = False

        rDict['isLogin'] = req.session['isLogin']
        rDict['now'] = 'detail'
        rDict['error'] = '담당 아이돌로 지정되었습니다.'
        return render(req, 'idoldb/idol_detail.html', rDict)


class register(View):
    def get(self, req):
        rDict = dict()
        rDict['now'] = 'signup'
        if not req.session.get('isLogin', False):
            req.session['isLogin'] = False
        if req.session['isLogin']:
            return redirect('idolMain')
        rDict['isLogin'] = req.session['isLogin']

        return render(req, 'idoldb/signup.html', rDict)

    def post(self, req):
        uid = uuid.uuid4()

        # 정보 받아오기
        req_data = req.POST

        # 계정 객체
        ob = Account.objects
        rDict = dict()

        # 생성 가능한지 확인
        if ob.filter(email=req_data['email']).exists():
            # 이메일이 겹침
            rDict['error'] = "이미 있는 이메일입니다."
        else:
            if ob.filter(nickname=req_data['nickname']).exists():
                rDict['error'] = "이미 있는 닉네임입니다."
            else:
                if req_data['password'] != req_data['password_same']:
                    rDict['error'] = "비밀번호가 서로 다릅니다."
                else:
                    if not 8 <= len(req_data['password']) <= 20:
                        rDict['error'] = "비밀번호는 8~20자리"
                    else:
                        if not 1 <= len(req_data['nickname']) <= 10:
                            rDict['error'] = "닉네임은 10자이내"
                        else:
                            rDict['error'] = "메일을 확인해주세요."
                            # req로 계정 생성
                            account = ob.create(email=req_data['email'],
                                                nickname=req_data['nickname'])

                            # sha512로 비밀번호
                            account.password = uid.__str__() + ":" + get_sha512(uid.__str__() + req_data['password'])

                            # 토큰 생성
                            account.token = get_token(uid.urn.__str__())

                            # 저장
                            account.save()

                            # 이메일용 템플릿 갖고오기
                            message = render_to_string('idoldb/activate_email.html', {
                                'user': account.nickname,
                                'uid': account.id,
                                'token': account.token
                            })

                            # 이메일 보내기
                            email = EmailMessage('idoldb 회원가입 메일 인증입니다.', message, to=[account.email])
                            email.send()

        rDict['now'] = 'signup'
        if not req.session.get('isLogin', False):
            req.session['isLogin'] = False
        if req.session['isLogin']:
            return redirect('idolMain')
        rDict['isLogin'] = req.session['isLogin']
        return render(req, 'idoldb/signup.html', rDict)


class emailActivate(View):
    def get(self, req, uid, token):
        rDict = dict()
        if not Account.objects.filter(id=int(uid)).exists():
            # 왜 없는 계정을 인증하려고 하시죠?
            rDict['error'] = '잘못된 접근입니다.'
        else:
            account = Account.objects.get(id=int(uid))

            if account.emailActivate:
                # 이미 인증 되셨습니다만?
                rDict['error'] = '이미 인증되었습니다.'
            else:

                if not account.token == token:
                    # 왜 토큰이 다르죠?
                    rDict['error'] = '잘못된 접근입니다.'

                else:
                    # 계정 활성화
                    account.emailActivate = True
                    account.token = get_token(uuid.uuid4().urn.__str__())

                    account.save()

                    # 정상종료
                    rDict['error'] = '메일 인증이 완료되었습니다.'

        rDict['now'] = 'logPage'
        if not req.session.get('isLogin', False):
            req.session['isLogin'] = False
        if req.session['isLogin']:
            token = req.session['token']
            rDict['token'] = token

            o = Account.objects
            if o.filter(token=token).exists():
                rDict['user'] = o.get(token=token)
            else:
                req.session['isLogin'] = False

        rDict['isLogin'] = req.session['isLogin']
        return render(req, 'idoldb/logpage.html', rDict)


class logout(View):
    def get(self, req):
        req.session['isLogin'] = False

        return redirect('idolMain')


class login(View):
    def get(self, req):
        rDict = dict()
        rDict['now'] = 'login'
        if not req.session.get('isLogin', False):
            req.session['isLogin'] = False
        if req.session['isLogin']:
            return redirect('idolMain')
        rDict['isLogin'] = req.session['isLogin']

        return render(req, 'idoldb/login.html', rDict)

    def post(self, req):
        req_data = req.POST
        ob = Account.objects
        if not ob.filter(email=req_data['email']).exists():
            rDict = dict()
            rDict['now'] = 'login'
            if not req.session.get('isLogin', False):
                req.session['isLogin'] = False
            if req.session['isLogin']:
                return redirect('idolMain')
            rDict['isLogin'] = req.session['isLogin']
            rDict['error'] = "아이디, 비밀번호가 다름"

            return render(req, 'idoldb/login.html', rDict)

        account = ob.get(email=req_data['email'])
        if account.password.split(':')[1] != get_sha512(account.password.split(':')[0] + req_data['password']):
            rDict = dict()
            rDict['now'] = 'login'
            if not req.session.get('isLogin', False):
                req.session['isLogin'] = False
            if req.session['isLogin']:
                return redirect('idolMain')
            rDict['isLogin'] = req.session['isLogin']
            rDict['error'] = "아이디, 비밀번호가 다름"

            return render(req, 'idoldb/login.html', rDict)

        if not account.emailActivate:
            rDict = dict()
            rDict['now'] = 'login'
            if not req.session.get('isLogin', False):
                req.session['isLogin'] = False
            if req.session['isLogin']:
                return redirect('idolMain')
            rDict['isLogin'] = req.session['isLogin']
            rDict['error'] = "메일 인증을 받아주세요."

            return render(req, 'idoldb/login.html', rDict)

        token_tmp = get_token(account.password.split(":")[0])
        account.token = token_tmp
        account.save()

        req.session['isLogin'] = True
        req.session['token'] = account.token
        return redirect('idolMain')


class cameLog(View):
    def get(self, req):
        rDict = dict()
        should_refresh = False
        # 인덱싱 기능
        index: str = req.GET.get('index')
        if index:
            req.session['index_log'] = index
            should_refresh = True

        if not req.session.get('index_log', False):
            req.session['index_log'] = 1
            should_refresh = True

        if should_refresh:
            return redirect(cameLog)

        index: int = int(req.session['index_log']) - 1

        if not req.session.get('isLogin', False):
            req.session['isLogin'] = False
        if req.session['isLogin']:
            token = req.session['token']
            rDict['token'] = token

            o = Account.objects
            if o.filter(token=token).exists():
                rDict['user'] = o.get(token=token)
            else:
                req.session['isLogin'] = False

        result = CameLog.objects.order_by('-date')

        if not index in range(1, int(math.ceil(len(result) / PAGE_INDEX)) + 1):
            req.session['index_search'] = 1
            index = 0

        if index > 0:
            rDict['canDown'] = index
        else:
            rDict['canDown'] = None
        if index + 2 < int(math.ceil(len(result) / PAGE_INDEX)) + 1:
            rDict['canUp'] = index + 2
        else:
            rDict['canUp'] = None
        rindex = list(
            set(range(index - 1, index + 4)) & set(range(1, int(math.ceil(len(result) / PAGE_INDEX)) + 1)))
        rindex.sort()
        rDict['full_index'] = rindex

        rDict['isLogin'] = req.session['isLogin']
        rDict['now'] = 'camelog'
        rDict['camelogs'] = result[PAGE_INDEX * index:PAGE_INDEX * (index + 1)]
        return render(req, 'idoldb/camelog.html', rDict)

    def post(self, req):
        rDict = dict()
        req_data = req.POST
        o = Account.objects
        oc = CameLog.objects

        if req.session['isLogin']:
            if o.filter(token=req.session['token']).exists():

                today = datetime.now().date()
                tomorrow = today + timedelta(1)
                today_start = datetime.combine(today, time())
                today_end = datetime.combine(tomorrow, time())

                account = o.get(token=req.session['token'])
                if oc.filter(user=account).order_by('-date').filter(date__gte=today_start).filter(
                        date__lt=today_end).exists():
                    rDict['error'] = "이미 오늘 작성했습니다."
                else:
                    if not 1 <= len(req_data['title']) <= 20:
                        rDict['error'] = "제목은 20자리 내"
                    else:
                        comment = CameLog(user=account, title=req_data['title'], info=req_data['info'])
                        comment.save()
                        rDict['error'] = "작성되었습니다!"
            else:
                req.sesstion['isLogin'] = False
                return redirect('idolMain')
        else:
            return redirect('idolMain')
        should_refresh = False
        # 인덱싱 기능
        index: str = req.GET.get('index')
        if index:
            req.session['index_log'] = index
            should_refresh = True

        if not req.session.get('index_log', False):
            req.session['index_log'] = 1
            should_refresh = True

        if should_refresh:
            return redirect(cameLog)

        index: int = int(req.session['index_log']) - 1

        if not req.session.get('isLogin', False):
            req.session['isLogin'] = False
        if req.session['isLogin']:
            token = req.session['token']
            rDict['token'] = token

            o = Account.objects
            if o.filter(token=token).exists():
                rDict['user'] = o.get(token=token)
            else:
                req.session['isLogin'] = False

        result = CameLog.objects.order_by('-date')

        if not index in range(1, int(math.ceil(len(result) / PAGE_INDEX)) + 1):
            req.session['index_search'] = 1
            index = 0

        if index > 0:
            rDict['canDown'] = index
        else:
            rDict['canDown'] = None
        if index + 2 < int(math.ceil(len(result) / PAGE_INDEX)) + 1:
            rDict['canUp'] = index + 2
        else:
            rDict['canUp'] = None
        rindex = list(
            set(range(index - 1, index + 4)) & set(range(1, int(math.ceil(len(result) / PAGE_INDEX)) + 1)))
        rindex.sort()
        rDict['full_index'] = rindex

        rDict['isLogin'] = req.session['isLogin']
        rDict['now'] = 'camelog'
        rDict['camelogs'] = result[PAGE_INDEX * index:PAGE_INDEX * (index + 1)]
        return render(req, 'idoldb/camelog.html', rDict)


class IdolViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Idol.objects.all()
    serializer_class = IdolSerializer

    def list(self, req, *args, **kwargs):
        queryset = self.get_queryset()
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

        paginator = PageNumberPagination()

        serializer = IdolSerializer(paginator.paginate_queryset(queryset.filter(Qs), req), many=True)

        return paginator.get_paginated_response(serializer.data)