import json
import os
import re
import time
from difflib import SequenceMatcher
from typing import Dict, Any, Tuple, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
DATASET_PATH = os.path.join(DATA_DIR, "fln_dataset.json")

# Authentic Ol Chiki transliteration mapping
DEV_TO_OLCHIKI = {
    # Vowels
    'अ': 'ᱚ', 'आ': 'ᱟ', 'इ': 'ᱤ', 'ई': 'ᱤ', 'उ': 'ᱩ', 'ऊ': 'ᱩ',
    'ए': 'ᱮ', 'ऐ': 'ᱮ', 'ओ': 'ᱳ', 'औ': 'ᱳ',
    # Matras
    'ा': 'ᱟ', 'ि': 'ᱤ', 'ी': 'ᱤ', 'ु': 'ᱩ', 'ू': 'ᱩ',
    'े': 'ᱮ', 'ै': 'ᱮ', 'ो': 'ᱳ', 'ौ': 'ᱳ',
    # Consonants
    'क': 'ᱠ', 'ख': 'ᱠᱷ', 'ग': 'ᱜ', 'घ': 'ᱜᱷ', 'ङ': 'ᱝ',
    'च': 'ᱪ', 'छ': 'ᱪᱷ', 'ज': 'ᱡ', 'झ': 'ᱡᱷ', 'ञ': 'ᱧ',
    'ट': 'ᱴ', 'ठ': 'ᱴᱷ', 'ड': 'ᱰ', 'ढ': 'ᱰᱷ', 'ण': 'ᱬ',
    'त': 'ᱛ', 'थ': 'ᱛᱷ', 'द': 'ᱫ', 'ध': 'ᱫᱷ', 'न': 'ᱱ',
    'प': 'ᱯ', 'फ': 'ᱯᱷ', 'ब': 'ᱵ', 'भ': 'ᱵᱷ', 'म': 'ᱢ',
    'य': 'ᱭ', 'र': 'ᱨ', 'ल': 'ᱞ', 'व': 'ᱣ',
    'श': 'ᱥ', 'ष': 'ᱥ', 'स': 'ᱥ', 'ह': 'ᱦ',
    'ड़': 'ᱲ', 'ढ़': 'ᱲ', 'ज्ञ': 'ᱜᱭ',
    # Modifiers / Diacritics
    'ं': 'ᱸ', 'ः': 'ᱺ', '्': 'ᱽ', '़': 'ᱹ',
    # Punctuation
    '।': '᱾', '?': '?', '!': '!', ',': ',', '.': '᱾'
}

# Vocabulary dictionary for classroom speech expansion
HINDI_TO_TRIBAL_VOCAB = {
    "नमस्ते": {"s_dev": "जोहार", "s_ol": "ᱡᱚᱦᱟᱨ", "mun": "जोहार", "ho": "जोहार"},
    "धन्यवाद": {"s_dev": "जोहार / सराहव", "s_ol": "ᱡᱚᱦᱟᱨ / ᱥᱟᱨᱦᱟᱣ", "mun": "जोहार / सराहव", "ho": "जोहार"},
    "बच्चे": {"s_dev": "गिद्रा को", "s_ol": "ᱜᱤᱫᱽᱨᱟᱹ ᱠᱚ", "mun": "गिदिर को", "ho": "होन को"},
    "बच्चों": {"s_dev": "गिद्रा को", "s_ol": "ᱜᱤᱫᱽᱨᱟᱹ ᱠᱚ", "mun": "गिदिर को", "ho": "होन को"},
    "बैठो": {"s_dev": "दुड़ुब पे", "s_ol": "ᱫᱩᱲᱩᱵ ᱯᱮ", "mun": "दुबुंग पे", "ho": "दुब पे"},
    "बैठ": {"s_dev": "दुड़ुब", "s_ol": "ᱫᱩᱲᱩᱵ", "mun": "दुबुंग", "ho": "दुब"},
    "खड़े हो जाओ": {"s_dev": "तिंगुन पे", "s_ol": "ᱛᱤᱸᱜᱩᱱ ᱯᱮ", "mun": "तिंगू पे", "ho": "तिंगु पे"},
    "किताब": {"s_dev": "पुथी", "s_ol": "ᱯᱩᱛᱷᱤ", "mun": "पुथी", "ho": "पुती"},
    "कॉपी": {"s_dev": "खाथा", "s_ol": "ᱠᱷᱟᱛᱟ", "mun": "कापी", "ho": "पोथी"},
    "कलम": {"s_dev": "कोल़ोम", "s_ol": "ᱠᱚᱞᱚᱢ", "mun": "कलाम", "ho": "कलाम"},
    "खोलो": {"s_dev": "झिज पे", "s_ol": "ᱡᱷᱤᱡ ᱯᱮ", "mun": "खोल पे", "ho": "ओताय पे"},
    "पढ़ो": {"s_dev": "पाड़हाव पे", "s_ol": "ᱯᱟᱲᱦᱟᱣ ᱯᱮ", "mun": "पड़ाव पे", "ho": "पढ़ाय पे"},
    "लिखो": {"s_dev": "ओल पे", "s_ol": "ᱚᱞ ᱯᱮ", "mun": "ओल पे", "ho": "ओल पे"},
    "सुनो": {"s_dev": "आंजोम पे", "s_ol": "ᱟᱧᱡᱚᱢ ᱯᱮ", "mun": "आंजोम पे", "ho": "आयुम पे"},
    "देखो": {"s_dev": "कोयोक् पे", "s_ol": "ᱠᱚᱭᱚᱜ ᱯᱮ", "mun": "नेल पे", "ho": "नेल पे"},
    "बोलो": {"s_dev": "रोड़ पे", "s_ol": "ᱨᱚᱲ ᱯᱮ", "mun": "काजी पे", "ho": "कजी पे"},
    "गिनती": {"s_dev": "लेखा", "s_ol": "ᱞᱮᱠᱷᱟ", "mun": "लेखा", "ho": "लेखा"},
    "एक": {"s_dev": "मित्", "s_ol": "ᱢᱤᱫ", "mun": "मियद", "ho": "मियद"},
    "दो": {"s_dev": "बार", "s_ol": "ᱵᱟᱨ", "mun": "बारिया", "ho": "बारिया"},
    "तीन": {"s_dev": "पे", "s_ol": "ᱯᱮ", "mun": "आपिया", "ho": "आपिया"},
    "चार": {"s_dev": "पुन्", "s_ol": "ᱯᱩᱱ", "mun": "उपुनिया", "ho": "उपुनिया"},
    "पाँच": {"s_dev": "मोड़े", "s_ol": "ᱢᱚᱬᱮ", "mun": "मोड़ेया", "ho": "मोड़ेया"},
    "पानी": {"s_dev": "दाः", "s_ol": "ᱫᱟᱜ", "mun": "दाः", "ho": "दाः"},
    "खाना": {"s_dev": "दाका", "s_ol": "ᱫᱟᱠᱟ", "mun": "मंडी", "ho": "मंडी"},
    "हाँ": {"s_dev": "हें", "s_ol": "ᱦᱮᱸ", "mun": "हें", "ho": "हें"},
    "नहीं": {"s_dev": "बाङ", "s_ol": "ᱵᱟᱝ", "mun": "का", "ho": "का"},
    "अच्छा": {"s_dev": "बेस / मोज", "s_ol": "ᱵᱮᱥ / ᱢᱚᱡᱽ", "mun": "बेस", "ho": "बुगी"},
    "शाबाश": {"s_dev": "शाबाश", "s_ol": "ᱥᱟᱵᱟᱥ", "mun": "बेश", "ho": "बुगी"},
    "हाथ": {"s_dev": "ती", "s_ol": "ᱛᱤ", "mun": "ती", "ho": "ती"},
    "सर": {"s_dev": "गुरु गोमके", "s_ol": "ᱜᱩᱨᱩ ᱜᱚᱢᱠᱮ", "mun": "गोमके", "ho": "गुरु गोमके"},
    "मैडम": {"s_dev": "माय गोमके", "s_ol": "ᱢᱟᱹᱭ ᱜᱚᱢᱠᱮ", "mun": "माय गोमके", "ho": "माय गोमके"}
}

class NLPEngine:
    def __init__(self):
        self.dataset = []
        self.load_dataset()

    def load_dataset(self):
        if os.path.exists(DATASET_PATH):
            try:
                with open(DATASET_PATH, "r", encoding="utf-8") as f:
                    self.dataset = json.load(f)
            except Exception as e:
                print("Error loading dataset:", e)
                self.dataset = []

    def devanagari_to_olchiki(self, text: str) -> str:
        """Transliterates text in Devanagari script to Santhali Ol Chiki script"""
        result = []
        i = 0
        while i < len(text):
            char = text[i]
            # Check for two-character combinations (consonant + nukta/virama)
            if i + 1 < len(text) and text[i:i+2] in DEV_TO_OLCHIKI:
                result.append(DEV_TO_OLCHIKI[text[i:i+2]])
                i += 2
                continue
            if char in DEV_TO_OLCHIKI:
                result.append(DEV_TO_OLCHIKI[char])
            else:
                result.append(char)
            i += 1
        return "".join(result)

    def clean_text(self, text: str) -> str:
        return re.sub(r'[\।\,\.\?\!]', '', text).strip().lower()

    def string_similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, self.clean_text(a), self.clean_text(b)).ratio()

    def translate(
        self, 
        text: str, 
        source_lang: str = "Hindi", 
        target_lang: str = "Santhali",
        mode: str = "teacher"
    ) -> Dict[str, Any]:
        start_time = time.time()
        input_text = text.strip()

        # 1. Exact or high-confidence match in the 30 core FLN dataset
        best_match = None
        best_score = 0.0

        for item in self.dataset:
            if mode == "student":
                # Match against tribal texts (Santhali, Mundari, Ho)
                candidates = [
                    item.get("santhali_devanagari", ""),
                    item.get("santhali_olchiki", ""),
                    item.get("santhali_phonetic", ""),
                    item.get("mundari", ""),
                    item.get("ho", "")
                ]
                for c in candidates:
                    if not c:
                        continue
                    sim = self.string_similarity(input_text, c)
                    if sim > best_score:
                        best_score = sim
                        best_match = item
            else:
                # Teacher mode: Match against Hindi
                sim = self.string_similarity(input_text, item["hindi"])
                if sim > best_score:
                    best_score = sim
                    best_match = item

        # Exact / High similarity match (> 0.70)
        if best_match and best_score >= 0.70:
            latency = (time.time() - start_time) * 1000
            
            if mode == "student":
                # Student Mode: Student spoke tribal language, Teacher receives translated Hindi
                # 1. Output audio for teacher must be HINDI!
                hindi_audio = best_match.get("hindi_audio_file") or f"hindi_{best_match['id']}.wav"
                
                # 2. Source audio for student is tribal language
                student_tribal_audio = None
                if source_lang.lower() == "mundari":
                    student_tribal_audio = best_match.get("mundari_audio_file") or f"mundari_{best_match['id']}.wav"
                elif source_lang.lower() == "ho":
                    student_tribal_audio = best_match.get("ho_audio_file") or f"ho_{best_match['id']}.wav"
                else:  # Santhali
                    student_tribal_audio = best_match.get("audio_file") or f"santhali_{best_match['id']}.wav"

                return {
                    "source_text": input_text,
                    "source_language": source_lang,
                    "target_language": "Hindi",
                    "translated_text_devanagari": best_match["hindi"],
                    "translated_text_olchiki": None,
                    "phonetic_pronunciation": best_match.get("english"),
                    "confidence_score": round(best_score, 2),
                    "needs_review": best_score < 0.75,
                    "audio_url": f"/audios/{hindi_audio}" if hindi_audio else None,
                    "source_audio_url": f"/audios/{student_tribal_audio}" if student_tribal_audio else None,
                    "latency_ms": round(latency, 2),
                    "is_offline_cached": True
                }
            else:
                # Teacher Mode: Teacher spoke Hindi, Student receives translated Tribal language
                target_key = "santhali_devanagari"
                ol_key = "santhali_olchiki"
                tribal_audio_file = None
                if target_lang.lower() == "mundari":
                    target_key = "mundari"
                    ol_key = None
                    tribal_audio_file = best_match.get("mundari_audio_file") or f"mundari_{best_match['id']}.wav"
                elif target_lang.lower() == "ho":
                    target_key = "ho"
                    ol_key = None
                    tribal_audio_file = best_match.get("ho_audio_file") or f"ho_{best_match['id']}.wav"
                else:
                    tribal_audio_file = best_match.get("audio_file") or f"santhali_{best_match['id']}.wav"

                teacher_hindi_audio = best_match.get("hindi_audio_file") or f"hindi_{best_match['id']}.wav"
                trans_dev = best_match.get(target_key, best_match["santhali_devanagari"])
                trans_ol = best_match.get(ol_key) if ol_key else None

                return {
                    "source_text": input_text,
                    "source_language": source_lang,
                    "target_language": target_lang,
                    "translated_text_devanagari": trans_dev,
                    "translated_text_olchiki": trans_ol,
                    "phonetic_pronunciation": best_match.get("santhali_phonetic"),
                    "confidence_score": round(best_score, 2),
                    "needs_review": False,
                    "audio_url": f"/audios/{tribal_audio_file}" if tribal_audio_file else None,
                    "source_audio_url": f"/audios/{teacher_hindi_audio}" if teacher_hindi_audio else None,
                    "latency_ms": round(latency, 2),
                    "is_offline_cached": True
                }

        # 2. Vocabulary composition fallback for classroom sentences
        words = input_text.split()
        matched_words = 0

        if mode == "student":
            # Student Mode: Tribal input -> Hindi translation
            translated_hindi_words = []
            for w in words:
                clean_w = re.sub(r'[\।\,\.\?\!]', '', w).strip()
                found = False
                for hindi_k, vocab in HINDI_TO_TRIBAL_VOCAB.items():
                    tribal_forms = [vocab.get("s_dev", ""), vocab.get("s_ol", ""), vocab.get("mun", ""), vocab.get("ho", "")]
                    for tf in tribal_forms:
                        if tf and self.string_similarity(clean_w, tf) > 0.75:
                            translated_hindi_words.append(hindi_k)
                            found = True
                            matched_words += 1
                            break
                    if found:
                        break
                if not found:
                    translated_hindi_words.append(w)

            ratio = matched_words / max(len(words), 1)
            confidence = 0.70 + (ratio * 0.25)
            latency = (time.time() - start_time) * 1000
            res_hindi = " ".join(translated_hindi_words)

            return {
                "source_text": input_text,
                "source_language": source_lang,
                "target_language": "Hindi",
                "translated_text_devanagari": res_hindi,
                "translated_text_olchiki": None,
                "phonetic_pronunciation": None,
                "confidence_score": round(confidence, 2),
                "needs_review": confidence < 0.75,
                "audio_url": None,
                "latency_ms": round(latency, 2),
                "is_offline_cached": True
            }
        else:
            # Teacher Mode: Hindi input -> Tribal translation
            translated_dev_words = []
            translated_ol_words = []
            for w in words:
                clean_w = re.sub(r'[\।\,\.\?\!]', '', w).strip()
                found = False
                for k, vocab in HINDI_TO_TRIBAL_VOCAB.items():
                    if self.string_similarity(clean_w, k) > 0.75:
                        if target_lang.lower() == "mundari":
                            translated_dev_words.append(vocab.get("mun", vocab["s_dev"]))
                        elif target_lang.lower() == "ho":
                            translated_dev_words.append(vocab.get("ho", vocab["s_dev"]))
                        else:
                            translated_dev_words.append(vocab["s_dev"])
                            translated_ol_words.append(vocab["s_ol"])
                        found = True
                        matched_words += 1
                        break
                if not found:
                    translated_dev_words.append(w)
                    if target_lang.lower() == "santhali":
                        translated_ol_words.append(self.devanagari_to_olchiki(w))

            ratio = matched_words / max(len(words), 1)
            confidence = 0.65 + (ratio * 0.25)
            latency = (time.time() - start_time) * 1000

            res_dev = " ".join(translated_dev_words)
            res_ol = " ".join(translated_ol_words) if target_lang.lower() == "santhali" else None

            return {
                "source_text": input_text,
                "source_language": source_lang,
                "target_language": target_lang,
                "translated_text_devanagari": res_dev,
                "translated_text_olchiki": res_ol,
                "phonetic_pronunciation": None,
                "confidence_score": round(confidence, 2),
                "needs_review": confidence < 0.75,
                "audio_url": None,
                "latency_ms": round(latency, 2),
                "is_offline_cached": True
            }

nlp_engine = NLPEngine()
