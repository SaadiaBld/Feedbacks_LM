from bq_connect import get_verbatims_from_bq
from claude_interface import classify_with_claude

def run():
    verbatims = get_verbatims_from_bq(scrape_date="2025-06-02")
    for i, v in enumerate(verbatims):
        print(f"\n🟦 Verbatim {i+1} :\n{v}")
        result = classify_with_claude(v)

        if result:
            print(f"✅ Thèmes détectés : {result['themes']}")
            print(f"📝 Note de satisfaction sur 5 : {result['note']}")
        else:
            print("❌ Analyse non exploitable (voir claude_errors.log)")

if __name__ == "__main__":
    run()
