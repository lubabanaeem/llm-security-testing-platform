from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from .LLM.ollama_client import send_prompt
from .models import Attack, TestRun, Llm_model, Response, Report
import time
import json
from django.utils import timezone

from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from tester.models import Evaluation, TestRun

from tester.evaluation.services import evaluate_security_response
from django.contrib.auth.decorators import login_required


@login_required
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
    evaluation = None

    if request.method == "POST":

        print("POST RECEIVED")
        print(request.POST)

        selected_attack_id = request.POST.get("attack")
        selected_model = request.POST.get("model")

        attack = Attack.objects.get(attack_id=selected_attack_id)
        model = Llm_model.objects.get(name=selected_model)

        test_run = TestRun.objects.create(user=request.user, model=model, attack=attack)

        try:
            start = time.perf_counter()
            ollama_model = f"{model.name}:{model.version}"
            llm_response = send_prompt(ollama_model, attack.prompt)
            end = time.perf_counter()

            if not llm_response:  # catches None, empty string, or falsy junk
                raise ValueError("Model returned an empty response")

            response_time_ms = int((end - start) * 1000)
            Response.objects.create(
                test_run=test_run,
                llm_response=llm_response,
                response_time_ms=response_time_ms,
            )
            test_run.completed_at = timezone.now()
            test_run.save()

            evaluation = evaluate_security_response(test_run.id)

        except Exception as e:
            llm_response = f"Test failed: {e}"

    return render(
        request,
        "home.html",
        {
            "categories": categories,
            "attacks_json": attacks_json,
            "llm_response": llm_response if request.method == "POST" else None,
            "evaluation": evaluation if request.method == "POST" else None,
        },
    )


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:

            login(request, user)
            next_url = request.POST.get("next") or request.GET.get("next")
            return redirect(next_url or "home")

        else:

            return render(
                request, "login.html", {"error": "Invalid username or password."}
            )

    return render(request, "login.html")


@login_required
def attack_library(request):
    # 1. Grabing filter choices from the URL search bar / dropdown
    search_query = request.GET.get("search", "").strip()
    selected_category = request.GET.get("category", "").strip()

    # 2. FIX ORDERING: Sorting by category, then by the structural ID
    attacks = Attack.objects.order_by("category", "attack_id")

    # 3. Calculating statistics dynamically from the database
    total_attacks = attacks.count()
    all_categories = sorted(
        list(Attack.objects.values_list("category", flat=True).distinct())
    )
    total_categories_count = len(all_categories)

    # Specific category counters for cards
    pi_count = Attack.objects.filter(category="Prompt Injection").count()
    sl_count = Attack.objects.filter(category="System Prompt Leakage").count()

    # 4. Applying filters if the user searched for something
    if search_query:
        attacks = attacks.filter(attack_id__icontains=search_query) | attacks.filter(
            name__icontains=search_query
        )
    if selected_category:
        attacks = attacks.filter(category=selected_category)

    # 5. Packing data to send to HTML template
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


from datetime import timedelta


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def reports_list_view(request):
    """List view for all past test runs with live search and category filtering."""
    query = request.GET.get("q", "").strip()
    category_filter = request.GET.get("category", "").strip()

    evaluations = Evaluation.objects.select_related(
        "test_run__attack", "test_run__model", "test_run__user"
    ).order_by("-evaluated_at")

    if query:
        evaluations = evaluations.filter(
            Q(test_run__attack__name__icontains=query)
            | Q(test_run__attack__attack_id__icontains=query)
            | Q(test_run__model__name__icontains=query)
            | Q(verdict__icontains=query)
        )

    if category_filter:
        evaluations = evaluations.filter(
            test_run__attack__category__iexact=category_filter
        )

    # Fetching unique categories for dropdown filter
    categories = (
        TestRun.objects.values_list("attack__category", flat=True)
        .distinct()
        .order_by("attack__category")
    )

    context = {
        "evaluations": evaluations,
        "query": query,
        "selected_category": category_filter,
        "categories": [c.strip() for c in categories if c],
    }
    return render(request, "reports_list.html", context)


@login_required
def single_report_detail_view(request, evaluation_id):
    """Detailed view for a single evaluation report formatted for viewing and PDF printing."""
    evaluation = get_object_or_404(
        Evaluation.objects.select_related(
            "test_run__attack",
            "test_run__model",
            "test_run__user",
            "test_run__response",
        ),
        id=evaluation_id,
    )

    return render(request, "report_detail.html", {"eval": evaluation})
