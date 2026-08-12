from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from .LLM.ollama_client import send_prompt
from .models import Attack, TestRun, Llm_model, Response, Report
import time
import json


def home(request):
    attacks = Attack.objects.all()

    categories = sorted(Attack.objects.values_list("category", flat=True).distinct())

    attacks_json = json.dumps(
        [
            {
                "id": attack.attack_id,
                "name": attack.name,
                "category": attack.category,
            }
            for attack in attacks
        ]
    )

    llm_response = None

    if request.method == "POST":

        print("POST RECEIVED")
        print(request.POST)

        selected_attack_id = request.POST.get("attack")
        selected_model = request.POST.get("model")

        attack = Attack.objects.get(attack_id=selected_attack_id)

        model = Llm_model.objects.get(name=selected_model)

        print("Prompt from database:")
        print(attack.prompt)
        start = time.perf_counter()
        ollama_model = f"{model.name}:{model.version}"
        llm_response = send_prompt(ollama_model, attack.prompt)

        end = time.perf_counter()

        print("LLM RESPONSE:")
        print(llm_response)

        test_run = TestRun.objects.create(
            user_id=request.user, model_id=model, attack_id=attack
        )

        # Save Response
        response_time_ms = int((end - start) * 1000)
        Response.objects.create(
            test_run=test_run,
            llm_response=llm_response,
            response_time_ms=response_time_ms,
        )

    return render(
        request,
        "home.html",
        {
            "categories": categories,
            "attacks_json": attacks_json,
            "llm_response": llm_response if request.method == "POST" else None,
        },
    )


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:

            login(request, user)
            return redirect("home")

        else:

            return render(
                request, "login.html", {"error": "Invalid username or password."}
            )

    return render(request, "login.html")


from django.shortcuts import render
from tester.models import Attack
import json


def attack_library(request):
    # 1. Grab filter choices from the URL search bar / dropdown
    search_query = request.GET.get("search", "").strip()
    selected_category = request.GET.get("category", "").strip()

    # 2. FIX ORDERING: Sort by category, then by the structural ID (PI-01, PI-02)
    attacks = Attack.objects.order_by("category", "attack_id")

    # 3. Calculate statistics dynamically from the database
    total_attacks = attacks.count()
    all_categories = sorted(
        list(Attack.objects.values_list("category", flat=True).distinct())
    )
    total_categories_count = len(all_categories)

    # Specific category counters for cards (adjust strings to match your JSON exactly)
    pi_count = Attack.objects.filter(category="Prompt Injection").count()
    sl_count = Attack.objects.filter(category="System Prompt Leakage").count()

    # 4. Apply filters if the user searched for something
    if search_query:
        attacks = attacks.filter(attack_id__icontains=search_query) | attacks.filter(
            name__icontains=search_query
        )
    if selected_category:
        attacks = attacks.filter(category=selected_category)

    # 5. Pack data to send to HTML template
    context = {
        "attacks": attacks,
        "categories": all_categories,
        "search_query": search_query,
        "selected_category": selected_category,
        "total_attacks": total_attacks,
        "total_categories_count": total_categories_count,
        "pi_count": pi_count,
        "sl_count": sl_count,
    }
    return render(request, "attack_library.html", context)


def logout_view(request):
    logout(request)
    return redirect("login")


def reports(request):
    return render(request, "report.html")


# Create your views here.
