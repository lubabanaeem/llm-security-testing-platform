from django.contrib import admin

# Register your models here.

from .models import Attack, Llm_model, TestRun, Response, Report, BenchmarkCase

admin.site.register(Attack)
admin.site.register(Llm_model)
admin.site.register(TestRun)
admin.site.register(Response)
admin.site.register(Report)
admin.site.register(BenchmarkCase)
