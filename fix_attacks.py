from tester.models import Attack, TestRun

correct_mi26 = Attack.objects.get(attack_id="MI-26")
correct_si20 = Attack.objects.get(attack_id="SI-20")

for run_id in [15, 23]:
    run = TestRun.objects.get(id=run_id)
    run.attack = correct_mi26
    run.save()

for run_id in [16, 24]:
    run = TestRun.objects.get(id=run_id)
    run.attack = correct_si20
    run.save()

print([r.attack.attack_id for r in TestRun.objects.filter(id__in=[15, 23, 16, 24])])

Attack.objects.filter(attack_id__in=["SL-19", "SL-20", "PI-25", "PI-26"]).delete()

print(Attack.objects.all().count())
