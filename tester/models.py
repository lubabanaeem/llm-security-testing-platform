from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Llm_model(models.Model):
    name = models.CharField(max_length=20)
    version = models.CharField(max_length=10)
    provider = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name} {self.version}"


class Attack(models.Model):
    attack_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    prompt = models.TextField()
    expected_behaviour = models.TextField()

    def __str__(self):
        return f"{self.attack_id} - {self.name}"


class TestRun(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    model_id = models.ForeignKey(Llm_model, on_delete=models.CASCADE)
    attack_id = models.ForeignKey(Attack, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f" {self.user_id.username} {self.attack_id.name}"


class Response(models.Model):
    test_run = models.OneToOneField(TestRun, on_delete=models.CASCADE)
    llm_response = models.TextField()
    response_time_ms = models.IntegerField()

    def __str__(self):
        return f" Response for test {self.test_run.attack_id.name}"


class Evaluation(models.Model):
    test_run = models.OneToOneField(TestRun, on_delete=models.CASCADE)
    risk_score = models.IntegerField()
    risk_level = models.CharField(max_length=20)
    verdict = models.CharField(max_length=20)
    evidence_summary = models.TextField()
    recommendations = models.TextField()
    evaluated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluation for Test {self.test_run.id}"


class Report(models.Model):
    test_run = models.OneToOneField(TestRun, on_delete=models.CASCADE)
    report_title = models.CharField(max_length=200)
    report_path = models.CharField(max_length=255)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.report_title
