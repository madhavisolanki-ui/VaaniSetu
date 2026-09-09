import json
import os
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
DATASET_PATH = os.path.join(DATA_DIR, "fln_dataset.json")

class FLNGenerator:
    def __init__(self):
        self.dataset = []
        if os.path.exists(DATASET_PATH):
            with open(DATASET_PATH, "r", encoding="utf-8") as f:
                self.dataset = json.load(f)

    def get_flashcards(self, category: str = "all") -> List[Dict[str, Any]]:
        flashcards = []
        
        # 1. Numeracy Flashcards
        numeracy_cards = [
            {"id": "num_1", "category": "Numeracy", "front": "1 (एक)", "back_dev": "मित् (Mid)", "back_ol": "ᱢᱤᱫ", "icon": "🍎", "audio_file": "santhali_10.wav"},
            {"id": "num_2", "category": "Numeracy", "front": "2 (दो)", "back_dev": "बार (Bar)", "back_ol": "ᱵᱟᱨ", "icon": "🍎🍎", "audio_file": "santhali_10.wav"},
            {"id": "num_3", "category": "Numeracy", "front": "3 (तीन)", "back_dev": "पे (Pe)", "back_ol": "ᱯᱮ", "icon": "⭐⭐⭐", "audio_file": "santhali_10.wav"},
            {"id": "num_4", "category": "Numeracy", "front": "4 (चार)", "back_dev": "पुन् (Pun)", "back_ol": "ᱯᱩᱱ", "icon": "⭐⭐⭐⭐", "audio_file": "santhali_10.wav"},
            {"id": "num_5", "category": "Numeracy", "front": "5 (पाँच)", "back_dev": "मोड़े (Mone)", "back_ol": "ᱢᱚᱬᱮ", "icon": "🖐️", "audio_file": "santhali_10.wav"},
            {"id": "num_6", "category": "Numeracy", "front": "10 (दस)", "back_dev": "गेल (Gel)", "back_ol": "ᱜᱮᱞ", "icon": "👐", "audio_file": "santhali_11.wav"}
        ]

        # 2. Classroom Vocabulary Flashcards
        vocab_cards = [
            {"id": "voc_1", "category": "Literacy", "front": "किताब (Book)", "back_dev": "पुथी (Puthi)", "back_ol": "ᱯᱩᱛᱷᱤ", "icon": "📖", "audio_file": "santhali_2.wav"},
            {"id": "voc_2", "category": "Literacy", "front": "कॉपी (Notebook)", "back_dev": "खाथा (Khata)", "back_ol": "ᱠᱷᱟᱛᱟ", "icon": "📝", "audio_file": "santhali_8.wav"},
            {"id": "voc_3", "category": "Literacy", "front": "पेड़ (Tree)", "back_dev": "दारे (Dare)", "back_ol": "ᱫᱟᱨᱮ", "icon": "🌳", "audio_file": "santhali_23.wav"},
            {"id": "voc_4", "category": "Literacy", "front": "पानी (Water)", "back_dev": "दाः (Daag)", "back_ol": "ᱫᱟᱜ", "icon": "💧", "audio_file": "santhali_20.wav"},
            {"id": "voc_5", "category": "Literacy", "front": "गाय (Cow)", "back_dev": "गाई (Gay)", "back_ol": "ᱜᱟᱹᱭ", "icon": "🐄", "audio_file": "santhali_24.wav"},
            {"id": "voc_6", "category": "Literacy", "front": "हाथ (Hand)", "back_dev": "ती (Ti)", "back_ol": "ᱛᱤ", "icon": "✋", "audio_file": "santhali_6.wav"}
        ]

        # 3. Phrasal Flashcards from Dataset
        phrase_cards = []
        for item in self.dataset[:10]:
            phrase_cards.append({
                "id": f"phrase_{item['id']}",
                "category": item.get("category", "General"),
                "front": item["hindi"],
                "back_dev": item["santhali_devanagari"],
                "back_ol": item.get("santhali_olchiki", ""),
                "phonetic": item.get("santhali_phonetic", ""),
                "english": item.get("english", ""),
                "icon": "💬",
                "audio_file": item.get("audio_file")
            })

        all_cards = numeracy_cards + vocab_cards + phrase_cards
        if category != "all":
            return [c for c in all_cards if c.get("category", "").lower() == category.lower()]
        return all_cards

    def generate_worksheet_data(self, topic: str = "Numeracy") -> Dict[str, Any]:
        if topic.lower() == "numeracy":
            return {
                "title": "NIPUN Bharat FLN Numeracy Worksheet",
                "sub_title": "Hindi ↔ Santhali Counting & Word Recognition",
                "grade": "Primary Grade 1-2",
                "instructions": "Match the Hindi numerals and words with the correct Santhali words (Devanagari & Ol Chiki).",
                "questions": [
                    {"q_num": 1, "question": "1 (एक) का संथाली शब्द चुनें:", "options": ["बार", "मित् (ᱢᱤᱫ)", "मोड़े", "गेल"], "correct": "मित् (ᱢᱤᱫ)"},
                    {"q_num": 2, "question": "3 (तीन) + 2 (दो) = 5 (पाँच) संथाली में क्या होगा?", "options": ["पे आर बार = मोड़े (ᱢᱚᱬᱮ)", "पुन् आर मित्", "बार आर बार"], "correct": "पे आर बार = मोड़े (ᱢᱚᱬᱮ)"},
                    {"q_num": 3, "question": "हाथ (Hand) को संथाली में क्या कहते हैं?", "options": ["ती (ᱛᱤ)", "दारे", "दाः"], "correct": "ती (ᱛᱤ)"},
                    {"q_num": 4, "question": "गाय (Cow) हमें क्या देती है?", "options": ["तोआ (दूध)", "दाः (पानी)", "दाका (खाना)"], "correct": "तोआ (दूध)"}
                ]
            }
        else:
            return {
                "title": "NIPUN Bharat FLN Literacy Worksheet",
                "sub_title": "Classroom Vocabulary & Mother-Tongue Learning",
                "grade": "Primary Grade 1-2",
                "instructions": "Bilingual classroom sentences and vocabulary check.",
                "questions": [
                    {"q_num": 1, "question": "'किताब खोलो' का सही संथाली अनुवाद क्या है?", "options": ["पुथी झिज पे", "खाथा ओल पे", "दुड़ुब पे"], "correct": "पुथी झिज पे"},
                    {"q_num": 2, "question": "'नमस्ते' को संथाली और मुंडारी में क्या कहते हैं?", "options": ["जोहार (Johar)", "राम-राम", "सलाम"], "correct": "जोहार (Johar)"},
                    {"q_num": 3, "question": "'पेड़ के पत्ते हरे होते हैं' में 'पेड़' का संथाली शब्द:", "options": ["दारे (ᱫᱟᱨᱮ)", "साकम", "रंग"], "correct": "दारे (ᱫᱟᱨᱮ)"}
                ]
            }

fln_generator = FLNGenerator()
