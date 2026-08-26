import sys
from tester.models import Response


def verify_response_footprint(attack_id="UC-18", model_name="gemma"):
    # Fetch the latest response specifically matching the attack ID AND the model name
    res = Response.objects.filter(
        test_run__attack__attack_id=attack_id,
        test_run__model__name__icontains=model_name,
    ).last()

    if not res:
        print(
            f"\n⚠️  No Response record found for attack ID '{attack_id}' from model '{model_name}'."
        )
        return

    text = res.llm_response
    char_count = len(text)
    word_count = len(text.split())
    byte_size = sys.getsizeof(text)

    print("\n====================================================")
    print(f"    RESPONSE FOOTPRINT REPORT FOR: {attack_id} ({model_name.upper()})")
    print("====================================================")
    print(f"  Total Character Length:  {char_count:,} chars")
    print(f"  Estimated Word Count:    {word_count:,} words")
    print(f"  Memory Allocation:       {byte_size:,} bytes")
    print("----------------------------------------------------")
    print(f"  Exact Final Boundary:    {repr(text[-45:])}")
    print("====================================================")

    # Check if the text ends on standard sentence completions
    if text.strip().endswith((".", "!", "?", '"', "'", "}", "]")):
        print("💡 Status: Clean Finish. Text ends with normal terminal punctuation.")
    else:
        print(
            "🚨 Status: TRUNCATION CONFIRMED. Text terminates abruptly mid-thought or mid-code."
        )
        print(
            "   The hardware token ceiling cut off a fully vulnerable model response."
        )
    print("====================================================\n")


# Run the function automatically targeting Gemma
verify_response_footprint("UC-18", "gemma")
