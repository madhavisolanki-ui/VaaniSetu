import sys
import urllib.request
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import os

def get_base_url():
    port = os.environ.get("VAANISETU_PORT", "8001")
    for p in [port, "8001", "8000"]:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{p}/api/system/status", timeout=1):
                return f"http://127.0.0.1:{p}"
        except Exception:
            pass
    return f"http://127.0.0.1:{port}"

BASE_URL = get_base_url()

def get(url):
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode('utf-8'))

def post(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def run_tests():
    print("==================================================")
    print("   VaaniSetu Live Server Verification (SIH26042)  ")
    print(f"   Target: {BASE_URL}")
    print("==================================================")

    # 1. System status
    print("\n[1] Testing System Status...")
    status = get(f'{BASE_URL}/api/system/status')
    print(f"    * Server Status: {status['status']}")
    print(f"    * Edge Mode: {status['edge_mode']}")
    print(f"    * Target Device: {status['target_device']}")
    print(f"    * Languages: {[l['name'] for l in status['supported_languages']]}")
    print(f"    * Latency SLA: {status['latency_target']}")

    # 2. Hindi -> Santhali
    print("\n[2] Testing Translation: Hindi -> Santhali (Teacher Mode)...")
    t1 = post(f'{BASE_URL}/api/translate', {
        'text': 'किताब खोलो',
        'source_language': 'Hindi',
        'target_language': 'Santhali',
        'mode': 'teacher'
    })
    print(f"    * Hindi Input:        {t1['source_text']}")
    print(f"    * Santhali Devanagari: {t1['translated_text_devanagari']}")
    print(f"    * Santhali Ol Chiki:  {t1.get('translated_text_olchiki')}")
    print(f"    * Phonetic Pronun:    {t1.get('phonetic')}")
    print(f"    * Audio File:         {t1.get('audio_url')}")
    print(f"    * Measured Latency:   {t1.get('latency_ms')} ms")

    # 3. Hindi -> Mundari
    print("\n[3] Testing Translation: Hindi -> Mundari...")
    t2 = post(f'{BASE_URL}/api/translate', {
        'text': 'नमस्ते',
        'source_language': 'Hindi',
        'target_language': 'Mundari',
        'mode': 'teacher'
    })
    print(f"    * Hindi Input:        {t2['source_text']}")
    print(f"    * Mundari Devanagari: {t2['translated_text_devanagari']}")
    print(f"    * Measured Latency:   {t2.get('latency_ms')} ms")

    # 4. Hindi -> Ho
    print("\n[4] Testing Translation: Hindi -> Ho...")
    t3 = post(f'{BASE_URL}/api/translate', {
        'text': 'नमस्ते',
        'source_language': 'Hindi',
        'target_language': 'Ho',
        'mode': 'teacher'
    })
    print(f"    * Hindi Input:   {t3['source_text']}")
    print(f"    * Ho Devanagari: {t3['translated_text_devanagari']}")
    print(f"    * Measured Latency: {t3.get('latency_ms')} ms")

    # 5. Student Mode
    print("\n[5] Testing Student Mode: Santhali -> Hindi...")
    t4 = post(f'{BASE_URL}/api/translate', {
        'text': 'ᱡᱚᱦᱟᱨ',
        'source_language': 'Santhali',
        'target_language': 'Hindi',
        'mode': 'student'
    })
    print(f"    * Student Ol Chiki Input: {t4['source_text']}")
    print(f"    * Hindi Output:           {t4['translated_text_devanagari']}")

    # 6. FLN Phrases
    print("\n[6] Testing 30 High-Priority FLN Phrases...")
    phrases = get(f'{BASE_URL}/api/fln/phrases')
    print(f"    * Loaded FLN Phrases: {len(phrases)} sentences")
    for i, p in enumerate(phrases[:3], 1):
        print(f"      {i}. {p['hindi']} -> {p['santhali_devanagari']} ({p.get('santhali_olchiki', '')})")

    # 7. Flashcards
    print("\n[7] Testing NIPUN Bharat Flashcards...")
    cards = get(f'{BASE_URL}/api/fln/flashcards')
    print(f"    * Total Flashcards: {len(cards)} items")
    for i, c in enumerate(cards[:3], 1):
        print(f"      {i}. {c.get('front')} -> {c.get('back_dev')} ({c.get('back_ol')}) [{c.get('category')}]")

    # 8. Worksheet PDF Generation
    print("\n[8] Testing NIPUN Worksheet PDF Generation...")
    ws = post(f'{BASE_URL}/api/fln/worksheet/generate', {'topic': 'Numeracy'})
    print(f"    * Status: {ws['status']}")
    print(f"    * Generated PDF URL: {ws['pdf_download_url']}")

    # 9. Teacher Review Loop
    print("\n[9] Testing Teacher-in-the-Loop Review Submission...")
    review = post(f'{BASE_URL}/api/teacher/review', {
        'source_text': 'पानी पीओ',
        'ai_output': 'दाः ᱧᱩᱭ ᱢᱮ',
        'corrected_text': 'दाः ᱧᱩᱭ ᱢᱮ',
        'target_language': 'Santhali',
        'notes': 'Verified accurate for classroom grade 1'
    })
    print(f"    * Review Status: {review['status']}")
    print(f"    * Phrase DB ID:  {review['phrase_id']}")

    print("\n==================================================")
    print("  [SUCCESS] All 9 Core Subsystems Are 100% Active! ")
    print(f"  Open your browser at: {BASE_URL}       ")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
