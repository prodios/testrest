from django.db import models


class Program(models.Model):
    min_amount = models.PositiveIntegerField()
    max_amount = models.PositiveIntegerField()
    min_borrower_age = models.PositiveIntegerField()
    max_borrower_age = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.min_amount} - {self.max_amount} / {self.min_borrower_age} - {self.max_borrower_age}'

    class Meta:
        db_table = 'programs'
        ordering = ['min_amount', 'max_amount']


class Borrower(models.Model):
    iin = models.DecimalField(max_digits=12, decimal_places=0, unique=True)
    date_of_birth = models.DateField()

    def __str__(self):
        return f'{self.iin}'

    class Meta:
        db_table = 'borrowers'
        ordering = ['iin']


class Application(models.Model):

    class Status(models.IntegerChoices):
        approved = 0, 'Одобрено'
        rejected = 1, 'Отказ'

    program = models.ForeignKey(Program, blank=True, null=True, on_delete=models.PROTECT, related_name='applications')
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE, related_name='applications')
    amount = models.PositiveIntegerField()
    status = models.IntegerField(blank=True, null=True, choices=Status.choices)
    rejection_reason = models.TextField(default='', blank=True)

    def __str__(self):
        return f'{self.borrower} - {self.amount} - {self.get_status_display()}'

    class Meta:
        db_table = 'applications'


class BlackList(models.Model):
    iin = models.DecimalField(max_digits=12, decimal_places=0, unique=True)

    def __str__(self):
        return f'{self.iin}'

    class Meta:
        db_table = 'black_lists'
        ordering = ['iin']
