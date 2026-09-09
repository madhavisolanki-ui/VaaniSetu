import sys
import urllib.request
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def post(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

print("=== 1. Student Mode: Mundari Full Sentence ===")
r1 = post('http://127.0.0.1:8000/api/translate', {
    'text': 'आपन पारसी पुथी ओडोल पे।',
    'source_language': 'Mundari',
    'target_language': 'Hindi',
    'mode': 'student'
})
print(f"Source Text:    {r1['source_text']}")
print(f"Hindi Output:   {r1['translated_text_devanagari']}")
print(f"Audio URL:      {r1['audio_url']}")

print("\n=== 2. Student Mode: Mundari Single Word ===")
r2 = post('http://127.0.0.1:8000/api/translate', {
    'text': 'जोहार',
    'source_language': 'Mundari',
    'target_language': 'Hindi',
    'mode': 'student'
})
print(f"Source Text:    {r2['source_text']}")
print(f"Hindi Output:   {r2['translated_text_devanagari']}")
print(f"Audio URL:      {r2['audio_url']}")

print("\n=== 3. Teacher Mode: Hindi -> Mundari ===")
r3 = post('http://127.0.0.1:8000/api/translate', {
    'text': 'अपनी भाषा की किताब निकालो।',
    'source_language': 'Hindi',
    'target_language': 'Mundari',
    'mode': 'teacher'
})
print(f"Hindi Input:    {r3['source_text']}")
print(f"Mundari Output: {r3['translated_text_devanagari']}")
print(f"Audio URL:      {r3['audio_url']}")

print("\n=== 4. Teacher Mode: Hindi -> Ho ===")
r4 = post('http://127.0.0.1:8000/api/translate', {
    'text': 'अपनी भाषा की किताब निकालो।',
    'source_language': 'Hindi',
    'target_language': 'Ho',
    'mode': 'teacher'
})
print(f"Hindi Input:    {r4['source_text']}")
print(f"Ho Output:      {r4['translated_text_devanagari']}")
print(f"Audio URL:      {r4['audio_url']}")
