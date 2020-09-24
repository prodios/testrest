from datetime import date, datetime

import requests
from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from rest_framework import status, renderers
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from loanapps.models import Application, Program, BlackList, Borrower
from loanapps.serializers import ApplicationSerializer


def index(request):
    return render(request, 'loanapps/index.html')


class ProgramValidator:
    amount_error = 'Заявка не подходит по сумме'
    age_error = 'Заемщик не подходит по возрасту'
    application_status = Application.Status.approved
    rejection_reason = ''

    def __init__(self, amount, date_of_birth):
        self.amount = amount
        self.date_of_birth = date_of_birth
        self.programs = Program.objects.all()

    def check_amount(self):
        self.programs = self.programs.filter(min_amount__lte=self.amount, max_amount__gte=self.amount)
        if not self.programs.exists():
            self.application_status = Application.Status.rejected
            self.rejection_reason = self.amount_error

    def check_age(self):
        age = relativedelta(date.today(), self.date_of_birth).years
        self.programs = self.programs.filter(min_borrower_age__lte=age, max_borrower_age__gte=age)
        if not self.programs.exists():
            self.application_status = Application.Status.rejected
            self.rejection_reason = self.age_error

    def get_program(self):
        self.check_amount()
        if self.application_status == Application.Status.approved:
            self.check_age()

        program = self.programs.first().id if self.programs.exists() else None
        return program, self.application_status, self.rejection_reason


class IEValidator:
    url = 'https://stat.gov.kz/api/juridical/gov/'
    iin_error = 'иин является ИП'
    status = Application.Status.approved
    rejection_reason = ''

    def __init__(self, iin, lang='ru'):
        self.bin = iin
        self.lang = lang

    def check_iin(self):
        r = requests.get(self.url, params={'bin': self.bin, 'lang': self.lang}, timeout=30)
        if r.status_code == status.HTTP_200_OK:
            if r.json().get('success', False):
                self.status = Application.Status.rejected
                self.rejection_reason = self.iin_error
        else:
            self.status = Application.Status.rejected
            self.rejection_reason = self.iin_error
        return self.status, self.rejection_reason


class BlackListValidator:
    iin_error = 'Заемщик в черном списке'
    status = Application.Status.approved
    rejection_reason = ''

    def __init__(self, iin):
        self.iin = iin

    def check_black_list(self):
        if BlackList.objects.filter(iin=self.iin).exists():
            self.status = Application.Status.rejected
            self.rejection_reason = self.iin_error
        return self.status, self.rejection_reason


class ApplicationAPIView(GenericAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = ApplicationSerializer
    renderer_classes = [renderers.JSONRenderer]

    def get(self, request):
        serializer = self.get_serializer(Application.objects.all(), many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data
        iin = data.pop('iin')
        if iin.isdigit() and len(iin) == 12:
            date_of_birth = datetime.strptime(str(iin)[:6], '%y%m%d').date()
            borrower, created = Borrower.objects.get_or_create(iin=iin, defaults={'date_of_birth': date_of_birth})

            data['borrower'] = borrower.id
            data['program'], application_status, rejection_reason, = ProgramValidator(
                data.get('amount'), date_of_birth).get_program()

            if application_status == Application.Status.approved:
                application_status, rejection_reason = IEValidator(iin).check_iin()

            if application_status == Application.Status.approved:
                application_status, rejection_reason = BlackListValidator(iin).check_black_list()

            data['status'] = application_status
            data['rejection_reason'] = rejection_reason

            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('iin field is incorrect!', status=status.HTTP_400_BAD_REQUEST)


# class ApplicationAPIView(GenericAPIView):
#     authentication_classes = ()
#     permission_classes = ()
#     serializer_class = ApplicationSerializer
#     renderer_classes = [renderers.JSONRenderer]
#
#     def get(self, request):
#         serializer = self.get_serializer(Application.objects.all(), many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 'Заявка отправлена!',
#                 status=status.HTTP_200_OK,
#             )
#         else:
#             return Response(
#                 data=serializer.errors,
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
