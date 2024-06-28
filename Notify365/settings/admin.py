from django.contrib import admin
from .models import Company, State, CompanyType, ProviderType, TemplateCategory, RequiredDocument, Product



admin.site.register(Company)
admin.site.register(State)
admin.site.register(CompanyType)
admin.site.register(ProviderType)
admin.site.register(TemplateCategory)
admin.site.register(RequiredDocument)
admin.site.register(Product)
