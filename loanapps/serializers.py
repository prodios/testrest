from rest_framework import serializers

from loanapps.models import Application


class ApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Application
        fields = ['program', 'borrower', 'amount', 'status', 'rejection_reason']


# class CheckProgram:
#     amount_error = 'Заявка не подходит по сумме'
#     age_error = 'Заемщик не подходит по возрасту'
#     application_status = Application.Status.approved
#     rejection_reason = ''
#
#     def __init__(self, amount, date_of_birth):
#         self.amount = amount
#         self.date_of_birth = date_of_birth
#         self.programs = Program.objects.all()
#
#     def check_amount(self):
#         self.programs = self.programs.filter(min_amount__lte=self.amount, max_amount__gte=self.amount)
#         if not self.programs.exists():
#             self.application_status = Application.Status.rejected
#             self.rejection_reason = self.amount_error
#
#     def check_age(self):
#         age = relativedelta(date.today(), self.date_of_birth).years
#         self.programs = self.programs.filter(min_borrower_age__lte=age, max_borrower_age__gte=age)
#         if not self.programs.exists():
#             self.application_status = Application.Status.rejected
#             self.rejection_reason = self.age_error
#
#     def get_program(self):
#         self.check_amount()
#         if self.application_status == Application.Status.approved:
#             self.check_age()
#
#         program = self.programs.first() if self.programs.exists() else Program.objects.none()
#         return program, self.application_status, self.rejection_reason
#
#
# class CheckIE:
#     url = 'https://stat.gov.kz/api/juridical/gov/'
#     iin_error = 'иин является ИП'
#     status = Application.Status.approved
#     rejection_reason = ''
#
#     def __init__(self, iin, lang='ru'):
#         self.bin = iin
#         self.lang = lang
#
#     def check_iin(self):
#         r = requests.get(self.url, params={'bin': self.bin, 'lang': self.lang}, timeout=30)
#         if r.status_code == status.HTTP_200_OK:
#             response = r.json()
#             if response.get('success', False):
#                 self.status = Application.Status.rejected
#                 self.rejection_reason = self.iin_error
#         else:
#             self.status = Application.Status.rejected
#             self.rejection_reason = self.iin_error
#         return self.status, self.rejection_reason
#
#
# class CheckBlackList:
#     iin_error = 'Заемщик в черном списке'
#     status = Application.Status.approved
#     rejection_reason = ''
#
#     def __init__(self, iin):
#         self.iin = iin
#
#     def check_black_list(self):
#         if BlackList.objects.filter(iin=self.iin).exists():
#             self.status = Application.Status.rejected
#             self.rejection_reason = self.iin_error
#         return self.status, self.rejection_reason


# class ApplicationSerializer(serializers.Serializer):
#     iin = serializers.CharField(required=True, max_length=12, min_length=12)
#     amount = serializers.IntegerField(required=True)
#
#     def __init__(self, *args, **kwargs):
#         super(ApplicationSerializer, self).__init__(*args, **kwargs)
#
#     def validate(self, attrs):
#         iin = attrs.get('iin')
#         date_of_birth = datetime.strptime(iin[:6], '%y%m%d').date()
#
#         borrower, created = Borrower.objects.get_or_create(iin=iin, defaults={'date_of_birth': date_of_birth})
#         attrs['borrower'] = borrower
#         attrs['program'], application_status, rejection_reason, = CheckProgram(
#             attrs.get('amount'), date_of_birth).get_program()
#
#         if application_status == Application.Status.approved:
#             application_status, rejection_reason = CheckIE(iin).check_iin()
#
#         if application_status == Application.Status.approved:
#             application_status, rejection_reason = CheckBlackList(iin).check_black_list()
#
#         attrs['status'] = application_status
#         attrs['rejection_reason'] = rejection_reason
#         return attrs
#
#     def create(self, validated_data):
#         validated_data.pop('iin')
#         return Application.objects.create(**validated_data)
#
#     def update(self, instance, validated_data):
#         return super(ApplicationSerializer, self).update(instance, validated_data)
