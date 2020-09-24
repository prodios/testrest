from django.contrib import admin

from .models import Program, Borrower, Application, BlackList

admin.site.register(Program)
admin.site.register(Borrower)
admin.site.register(Application)
admin.site.register(BlackList)
