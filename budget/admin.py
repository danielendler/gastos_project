from django.contrib import admin
from budget.models import Category, Month, Expenditure, UserProfile, RecurringEvent


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('gastos_name',
                    'gastos_created_date',
                    'gastos_expense_date',
                    'gastos_category',
                    'gastos_value',
                    'gastos_author',
                    )


class RecurringAdmin(admin.ModelAdmin):
    list_display = ('category',
                    'value',
                    'recurrence',
                    'in_or_outcome',
                    'date_from',
                    'date_to',
                    'annotation',
                    'author',
                    )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Month)
admin.site.register(Expenditure, ExpenseAdmin)
admin.site.register(UserProfile)
admin.site.register(RecurringEvent,RecurringAdmin)








