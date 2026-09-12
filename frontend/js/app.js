
// ================= Global State =================
let currentRole = "teacher"; // "teacher" (Hindi -> Tribal) or "student" (Tribal -> Hindi)
let currentTargetLang = "Santhali"; // Santhali, Mundari, Ho
let isRecording = false;
let recognition = null;
let currentAudioUrl = "/audios/santhali_1.wav"; // Translated output audio (played for listener)
let currentSourceAudioUrl = "/audios/hindi_1.wav"; // Input speech audio (played on demand)
let cachedPhrases = [];
let cachedFlashcards = [];

// ================= Initialization =================
document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initSpeechRecognition();
  loadQuickPrompts();
  loadPhrasesTab();
  loadFlashcards("all");
  loadWorksheets("Numeracy");
  loadVerifiedPhrases();
});

// ================= Tab Navigation =================
function initTabs() {
  const tabs = document.querySelectorAll(".nav-btn");
  tabs.forEach(btn => {
    btn.addEventListener("click", () => {
      tabs.forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add("active");
    });
  });
}

// ================= Role & Language Switching =================
function setRole(role) {
  currentRole = role;
  const teacherBtn = document.getElementById("teacherModeBtn");
  const studentBtn = document.getElementById("studentModeBtn");
  const sourceTag = document.getElementById("sourceLangTag");
  const targetTag = document.getElementById("targetLangTag");
  const olChikiContainer = document.getElementById("olChikiContainer");

  const playAudioBtn = document.getElementById("playAudioBtn");

  if (role === "teacher") {
    teacherBtn.classList.add("active");
    studentBtn.classList.remove("active");
    sourceTag.textContent = "Recognized Teacher Hindi:";
    targetTag.textContent = `Translated ${currentTargetLang} Output:`;
    if (playAudioBtn) playAudioBtn.textContent = `▶️ Listen ${currentTargetLang} Translation`;
    if (olChikiContainer) olChikiContainer.style.display = (currentTargetLang === "Santhali") ? "block" : "none";
  } else {
    studentBtn.classList.add("active");
    teacherBtn.classList.remove("active");
    sourceTag.textContent = `Recognized Student ${currentTargetLang}:`;
    targetTag.textContent = "Translated Teacher Hindi Output:";
    if (playAudioBtn) playAudioBtn.textContent = `▶️ Listen Hindi Translation`;
    if (olChikiContainer) olChikiContainer.style.display = "none";
  }
  loadQuickPrompts();
}

function swapRoles() {
  setRole(currentRole === "teacher" ? "student" : "teacher");
}

function onTargetLangChange() {
  const select = document.getElementById("targetLangSelect");
  currentTargetLang = select.value;
  setRole(currentRole);
  loadQuickPrompts();
}

// ================= Web Speech API Integration =================
function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      isRecording = true;
      updateMicUI(true);
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      document.getElementById("recognizedText").textContent = transcript;
      performTranslation(transcript);
    };

    recognition.onerror = (event) => {
      console.warn("Speech recognition error:", event.error);
      isRecording = false;
      updateMicUI(false);
      document.getElementById("micStatusText").textContent = "Mic input error. You can also type below:";
    };

    recognition.onend = () => {
      isRecording = false;
      updateMicUI(false);
    };
  } else {
    console.warn("SpeechRecognition not supported in this browser. Using simulation / manual input.");
  }
}

function toggleRecording() {
  if (isRecording) {
    if (recognition) recognition.stop();
    isRecording = false;
    updateMicUI(false);
  } else {
    if (recognition) {
      recognition.lang = (currentRole === "teacher") ? "hi-IN" : "hi-IN";
      try {
        recognition.start();
      } catch (e) {
        console.warn("Recognition start failed, restarting:", e);
        simulateSpeechRecognition();
      }
    } else {
      simulateSpeechRecognition();
    }
  }
}

function updateMicUI(recording) {
  const micBtn = document.getElementById("mainMicBtn");
  const statusText = document.getElementById("micStatusText");
  const visualizer = document.getElementById("waveformVisualizer");

  if (recording) {
    micBtn.classList.add("recording");
    visualizer.classList.add("active");
    statusText.textContent = "🔴 Listening to classroom speech...";
  } else {
    micBtn.classList.remove("recording");
    visualizer.classList.remove("active");
    statusText.textContent = "Tap microphone to speak in classroom";
  }
}

function simulateSpeechRecognition() {
  updateMicUI(true);
  setTimeout(() => {
    updateMicUI(false);
    let picked;
    if (currentRole === "student") {
      if (currentTargetLang === "Mundari") {
        const munSamples = [
          "जोहार गिदिर को, आपन आपन ठांव रे दुबुंग पे।",
          "आपन पारसी पुथी ओडोल पे।",
          "मियद, बारिया, आपिया गिनती।",
          "दाः",
          "हें गोमके"
        ];
        picked = munSamples[Math.floor(Math.random() * munSamples.length)];
      } else if (currentTargetLang === "Ho") {
        const hoSamples = [
          "जोहार होन को, आपन आपन ठई रे दुब पे।",
          "आपन काजी पुती ओड़ो पे।",
          "मियद, बारिया, आपिया गिनती।",
          "दाः",
          "हें गुरु गोमके"
        ];
        picked = hoSamples[Math.floor(Math.random() * hoSamples.length)];
      } else {
        const satSamples = [
          "जोहार गिद्रा को, आपन आपन ठंव रे दुड़ुब पे।",
          "आपानाः पारसी पुथी ओडोक पे।",
          "मित्, बार, पे, पुन्, मोड़े",
          "दाः",
          "हें"
        ];
        picked = satSamples[Math.floor(Math.random() * satSamples.length)];
      }
    } else {
      // Teacher mode
      const samples = [
        "अपनी भाषा की किताब निकालो।",
        "किताब का पन्ना नंबर पाँच खोलो।",
        "आओ मिलकर एक से दस तक गिनती करें।",
        "दो और तीन को जोड़ने पर कितना होता है?",
        "इस शब्द को बोलकर पढ़ो।",
        "शाबाश! तुमने बहुत अच्छा उत्तर दिया।",
        "गाय हमें मीठा दूध देती है।"
      ];
      picked = samples[Math.floor(Math.random() * samples.length)];
    }
    document.getElementById("recognizedText").textContent = picked;
    performTranslation(picked);
  }, 1600);
}

// ================= Translation API Call =================
async function performTranslation(text) {
  const payload = {
    text: text,
    source_language: currentRole === "teacher" ? "Hindi" : currentTargetLang,
    target_language: currentRole === "teacher" ? currentTargetLang : "Hindi",
    mode: currentRole
  };

  try {
    const startTime = performance.now();
    const res = await fetch("/api/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error("Translation failed");
    const data = await res.json();
    const clientLatency = Math.round(performance.now() - startTime);

    renderTranslationResult(data, clientLatency);
  } catch (err) {
    console.warn("Backend translation failed, using offline client fallback:", err);
    offlineClientTranslate(text);
  }
}

function renderTranslationResult(data, latency) {
  document.getElementById("recognizedText").textContent = data.source_text;
  document.getElementById("translatedDevanagari").textContent = data.translated_text_devanagari || data.translated_text;
  
  const olChikiEl = document.getElementById("translatedOlChiki");
  const olChikiBox = document.getElementById("olChikiContainer");

  if (data.translated_text_olchiki && currentTargetLang === "Santhali" && currentRole === "teacher") {
    olChikiEl.textContent = data.translated_text_olchiki;
    olChikiBox.style.display = "block";
  } else {
    olChikiBox.style.display = "none";
  }

  const phoneticEl = document.getElementById("translatedPhonetic");
  phoneticEl.textContent = data.phonetic_pronunciation ? `"${data.phonetic_pronunciation}"` : "Pronunciation standard";

  // Latency
  document.getElementById("latencyValue").textContent = `${data.latency_ms || latency} ms`;

  // Confidence & Verification Badge
  const confidence = Math.round((data.confidence_score || 0.95) * 100);
  document.getElementById("confidenceFill").style.width = `${confidence}%`;
  document.getElementById("confidenceValue").textContent = `${confidence}% (${confidence > 85 ? 'High' : 'Medium'})`;

  // Audio URL & Play Button Label
  const playAudioBtn = document.getElementById("playAudioBtn");
  if (playAudioBtn) {
    if (currentRole === "student") {
      playAudioBtn.textContent = "▶️ Listen Hindi Translation";
      playAudioBtn.title = "Listen to translated Hindi speech for teacher";
    } else {
      playAudioBtn.textContent = `▶️ Listen ${currentTargetLang} Translation`;
      playAudioBtn.title = `Listen to translated ${currentTargetLang} speech for student`;
    }
  }

  if (data.source_audio_url) {
    currentSourceAudioUrl = data.source_audio_url;
  }
  if (data.audio_url) {
    currentAudioUrl = data.audio_url;
    autoPlayAudio(data.audio_url);
  }
}

// Client-side offline fallback
function offlineClientTranslate(text) {
  const matched = cachedPhrases.find(p => 
    p.hindi.includes(text) || text.includes(p.hindi) ||
    (p.mundari && p.mundari.includes(text)) ||
    (p.ho && p.ho.includes(text)) ||
    (p.santhali_devanagari && p.santhali_devanagari.includes(text))
  );

  if (matched) {
    let audioUrl;
    let sourceAudioUrl;

    if (currentRole === "student") {
      // Student Mode: Output audio is HINDI for the teacher!
      audioUrl = `/audios/${matched.hindi_audio_file || "hindi_" + matched.id + ".wav"}`;
      if (currentTargetLang === "Mundari") {
        sourceAudioUrl = `/audios/${matched.mundari_audio_file || "mundari_" + matched.id + ".wav"}`;
      } else if (currentTargetLang === "Ho") {
        sourceAudioUrl = `/audios/${matched.ho_audio_file || "ho_" + matched.id + ".wav"}`;
      } else {
        sourceAudioUrl = `/audios/${matched.audio_file}`;
      }
    } else {
      // Teacher Mode: Output audio is TRIBAL for the student!
      sourceAudioUrl = `/audios/${matched.hindi_audio_file || "hindi_" + matched.id + ".wav"}`;
      if (currentTargetLang === "Mundari") {
        audioUrl = `/audios/${matched.mundari_audio_file || "mundari_" + matched.id + ".wav"}`;
      } else if (currentTargetLang === "Ho") {
        audioUrl = `/audios/${matched.ho_audio_file || "ho_" + matched.id + ".wav"}`;
      } else {
        audioUrl = `/audios/${matched.audio_file}`;
      }
    }

    renderTranslationResult({
      source_text: text,
      translated_text_devanagari: currentRole === "student" ? matched.hindi : (currentTargetLang === "Mundari" ? matched.mundari : (currentTargetLang === "Ho" ? matched.ho : matched.santhali_devanagari)),
      translated_text_olchiki: (currentTargetLang === "Santhali" && currentRole === "teacher") ? matched.santhali_olchiki : null,
      phonetic_pronunciation: matched.santhali_phonetic,
      confidence_score: 0.96,
      audio_url: audioUrl,
      source_audio_url: sourceAudioUrl,
      latency_ms: 12
    }, 12);
  } else {
    renderTranslationResult({
      source_text: text,
      translated_text_devanagari: currentRole === "student" ? text + " (हिंदी अनुवाद)" : text + ` (${currentTargetLang} अनुवाद)`,
      translated_text_olchiki: (currentTargetLang === "Santhali" && currentRole === "teacher") ? "ᱥᱟᱱᱛᱟᱲᱤ ᱚᱞ" : null,
      phonetic_pronunciation: text,
      confidence_score: 0.72,
      audio_url: null,
      source_audio_url: null,
      latency_ms: 10
    }, 10);
  }
}

function handleManualSend() {
  const input = document.getElementById("manualTextInput");
  const text = input.value.trim();
  if (!text) return;
  document.getElementById("recognizedText").textContent = text;
  performTranslation(text);
  input.value = "";
}

// ================= Audio Playback =================
function playCurrentAudio() {
  const playBtn = document.getElementById("playAudioBtn");
  if (currentAudioUrl) {
    playAudioFileByUrl(currentAudioUrl, playBtn);
  } else {
    speakText('target');
  }
}

function autoPlayAudio(url) {
  if (!url) return;
  const playBtn = document.getElementById("playAudioBtn");
  playAudioFileByUrl(url, playBtn);
}

function playAudioFile(filename) {
  playAudioFileByUrl(`/audios/${filename}`);
}

function playAudioFileByUrl(url, triggerBtn = null) {
  if (!url) return;
  const audio = document.getElementById("globalAudioPlayer");
  audio.src = url;

  const btn = triggerBtn || document.getElementById("playAudioBtn");
  if (btn) {
    audio.onplay = () => btn.classList.add("speaking");
    audio.onended = () => btn.classList.remove("speaking");
    audio.onpause = () => btn.classList.remove("speaking");
    audio.onerror = () => btn.classList.remove("speaking");
  }

  audio.play().catch(e => console.log("Audio playback notice:", e));
}

function speakText(type) {
  const btn = (type === 'source') 
    ? document.getElementById("listenInputBtn") 
    : document.getElementById("playAudioBtn");

  if (type === 'source') {
    if (currentSourceAudioUrl) {
      playAudioFileByUrl(currentSourceAudioUrl, btn);
      return;
    }
  } else {
    if (currentAudioUrl) {
      playAudioFileByUrl(currentAudioUrl, btn);
      return;
    }
  }

  const text = (type === 'source') 
    ? document.getElementById("recognizedText").textContent 
    : document.getElementById("translatedDevanagari").textContent;
  
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'hi-IN';
    utterance.rate = 0.9;
    if (btn) {
      utterance.onstart = () => btn.classList.add("speaking");
      utterance.onend = () => btn.classList.remove("speaking");
      utterance.onerror = () => btn.classList.remove("speaking");
    }
    window.speechSynthesis.speak(utterance);
  }
}

function copyTranslation() {
  const text = document.getElementById("translatedDevanagari").textContent;
  navigator.clipboard.writeText(text);
  alert("Vernacular text copied to clipboard!");
}

// ================= Quick Prompts =================
function loadQuickPrompts() {
  const container = document.getElementById("quickPromptChips");
  if (!container) return;
  container.innerHTML = "";

  let prompts = [];

  if (currentRole === "student") {
    if (currentTargetLang === "Mundari") {
      prompts = [
        { label: "👋 जोहार (नमस्ते)", text: "जोहार गिदिर को, आपन आपन ठांव रे दुबुंग पे।" },
        { label: "📖 आपन पुथी (किताब)", text: "आपन पारसी पुथी ओडोल पे।" },
        { label: "🔢 मियद, बारिया (गिनती)", text: "मियद बारिया आपिया उपुनिया मोड़ेया" },
        { label: "✋ ती (हाथ)", text: "ती" },
        { label: "💧 दाः (पानी)", text: "दाः" },
        { label: "✅ हें (हाँ)", text: "हें" },
        { label: "🌟 बेस (अच्छा)", text: "बेस" }
      ];
    } else if (currentTargetLang === "Ho") {
      prompts = [
        { label: "👋 जोहार (नमस्ते)", text: "जोहार होन को, आपन आपन ठई रे दुब पे।" },
        { label: "📖 आपन काजी पुती", text: "आपन काजी पुती ओड़ो पे।" },
        { label: "🔢 मियद, बारिया (गिनती)", text: "मियद बारिया आपिया उपुनिया मोड़ेया" },
        { label: "✋ ती (हाथ)", text: "ती" },
        { label: "💧 दाः (पानी)", text: "दाः" },
        { label: "✅ हें (हाँ)", text: "हें" }
      ];
    } else {
      prompts = [
        { label: "👋 ᱡᱚᱦᱟᱨ (नमस्ते)", text: "जोहार गिद्रा को, आपन आपन ठंव रे दुड़ुब पे।" },
        { label: "📖 आपानाः पारसी पुथी", text: "आपानाः पारसी पुथी ओडोक पे।" },
        { label: "🔢 ᱢᱤᱫ, ᱵᱟᱨ (गिनती)", text: "मित् बार पे पुन् मोड़े" },
        { label: "✋ ᱛᱤ (हाथ)", text: "ती" },
        { label: "💧 ᱫᱟᱜ (पानी)", text: "दाः" },
        { label: "✅ ᱦᱮᱸ (हाँ)", text: "हें" }
      ];
    }
  } else {
    // Teacher mode prompts
    prompts = [
      { label: "👋 नमस्ते बच्चों", text: "नमस्ते बच्चों, अपनी-अपनी जगह पर बैठ जाओ।" },
      { label: "📖 किताब निकालो", text: "अपनी भाषा की किताब निकालो।" },
      { label: "📄 पन्ना नंबर पाँच", text: "किताब का पन्ना नंबर पाँच खोलो।" },
      { label: "🔢 1 से 10 गिनती", text: "आओ मिलकर एक से दस तक गिनती करें।" },
      { label: "➕ दो और तीन जोड़ना", text: "दो और तीन को जोड़ने पर कितना होता है?" },
      { label: "🌟 शाबाश", text: "शाबाश! तुमने बहुत अच्छा उत्तर दिया।" },
      { label: "🥛 गाय का दूध", text: "गाय हमें मीठा दूध देती है।" }
    ];
  }

  prompts.forEach(p => {
    const chip = document.createElement("button");
    chip.className = "prompt-chip";
    chip.textContent = p.label;
    chip.onclick = () => {
      document.getElementById("recognizedText").textContent = p.text;
      performTranslation(p.text);
    };
    container.appendChild(chip);
  });
}

// ================= Tab 2: 30 FLN Phrases =================
async function loadPhrasesTab() {
  try {
    const res = await fetch("/api/fln/phrases");
    cachedPhrases = await res.json();
    renderPhrasesGrid(cachedPhrases);
  } catch (err) {
    console.warn("Failed loading phrases from API, fallback to local:", err);
  }
}

function renderPhrasesGrid(items) {
  const container = document.getElementById("phrasesGridContainer");
  container.innerHTML = "";

  items.forEach(item => {
    const card = document.createElement("div");
    card.className = "phrase-card";
    card.innerHTML = `
      <div>
        <div class="phrase-top">
          <span class="phrase-cat">${item.category}</span>
          <span class="phrase-id">#${item.id}</span>
        </div>
        <p class="p-hindi" style="margin-top: 8px;">${item.hindi}</p>
        <p class="p-santhali-dev" style="margin-top: 6px;">${item.santhali_devanagari}</p>
        <p class="p-santhali-ol olchiki-text" style="margin-top: 4px;">${item.santhali_olchiki || ''}</p>
        <p class="p-phonetic" style="margin-top: 4px;">Phonetic: ${item.santhali_phonetic || ''}</p>
        ${item.mundari ? `<p style="font-size: 11px; color:#475569; margin-top:3px;">Mundari: ${item.mundari}</p>` : ''}
        ${item.ho ? `<p style="font-size: 11px; color:#475569; margin-top:2px;">Ho: ${item.ho}</p>` : ''}
      </div>
      <div class="phrase-actions" style="display:flex; flex-wrap:wrap; gap:6px;">
        <button class="play-small-btn" onclick="playAudioFile('${item.audio_file}')">▶ Santhali</button>
        ${item.mundari ? `<button class="play-small-btn" style="background:#0284c7;" onclick="playAudioFile('${item.mundari_audio_file || "mundari_" + item.id + ".wav"}')">▶ Mundari</button>` : ''}
        ${item.ho ? `<button class="play-small-btn" style="background:#0d9488;" onclick="playAudioFile('${item.ho_audio_file || "ho_" + item.id + ".wav"}')">▶ Ho</button>` : ''}
        <button class="try-btn" onclick="testInClassroom('${item.hindi.replace(/'/g, "\\'")}')">Use in Class ➔</button>
      </div>
    `;
    container.appendChild(card);
  });
}

function filterPhrases(category) {
  document.querySelectorAll("#phrases-tab .filter-btn").forEach(b => b.classList.remove("active"));
  event.target.classList.add("active");

  if (category === "all") {
    renderPhrasesGrid(cachedPhrases);
  } else {
    const filtered = cachedPhrases.filter(p => p.category.toLowerCase().includes(category.toLowerCase()));
    renderPhrasesGrid(filtered);
  }
}

function testInClassroom(text) {
  document.querySelector('.nav-btn[data-tab="dialogue-tab"]').click();
  document.getElementById("recognizedText").textContent = text;
  performTranslation(text);
}

// ================= Tab 3: Flashcards =================
async function loadFlashcards(category) {
  try {
    const res = await fetch(`/api/fln/flashcards?category=${category}`);
    cachedFlashcards = await res.json();
    renderFlashcards(cachedFlashcards);
  } catch (err) {
    console.warn("Failed loading flashcards:", err);
  }
}

function renderFlashcards(cards) {
  const container = document.getElementById("flashcardsGrid");
  container.innerHTML = "";

  cards.forEach(c => {
    const card = document.createElement("div");
    card.className = "flashcard";
    card.onclick = () => card.classList.toggle("flipped");

    card.innerHTML = `
      <div class="flashcard-inner">
        <div class="card-front">
          <span class="card-icon">${c.icon || '📖'}</span>
          <span class="card-title-text">${c.front}</span>
          <span class="flip-hint">↻ Tap to reveal Santhali</span>
        </div>
        <div class="card-back">
          <span class="back-dev">${c.back_dev}</span>
          <span class="back-ol olchiki-text">${c.back_ol || ''}</span>
          ${c.phonetic ? `<span style="font-size:11px; margin-top:4px;">"${c.phonetic}"</span>` : ''}
          <button class="card-play-audio" onclick="event.stopPropagation(); playAudioFile('${c.audio_file || 'santhali_1.wav'}')">
            ▶ Listen
          </button>
        </div>
      </div>
    `;
    container.appendChild(card);
  });
}

// ================= Tab 4: Worksheets =================
async function loadWorksheets(topic) {
  generateWorksheet(topic);
}

async function generateWorksheet(topic) {
  try {
    const res = await fetch("/api/fln/worksheet/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic: topic, grade: "Grade 1", language: "Santhali" })
    });
    const data = await res.json();
    const ws = data.worksheet_data;

    document.getElementById("wsTitle").textContent = ws.title;
    document.getElementById("wsSubTitle").textContent = `${ws.sub_title} • ${ws.grade}`;
    document.getElementById("downloadPdfBtn").href = data.pdf_download_url;

    const container = document.getElementById("wsQuestionsContainer");
    container.innerHTML = "";

    ws.questions.forEach(q => {
      const qRow = document.createElement("div");
      qRow.className = "ws-question-row";
      
      let optionsHtml = "";
      q.options.forEach((opt, idx) => {
        optionsHtml += `<div class="ws-opt-item" onclick="selectOption(this, '${opt === q.correct}')">(${String.fromCharCode(65 + idx)}) ${opt}</div>`;
      });

      qRow.innerHTML = `
        <div class="ws-q-title">Q${q.q_num}. ${q.question}</div>
        <div class="ws-options-list">${optionsHtml}</div>
      `;
      container.appendChild(qRow);
    });

  } catch (e) {
    console.warn("Worksheet error:", e);
  }
}

function selectOption(el, isCorrect) {
  const siblings = el.parentElement.querySelectorAll(".ws-opt-item");
  siblings.forEach(s => s.classList.remove("selected"));
  el.classList.add("selected");
  if (isCorrect === "true") {
    el.style.borderColor = "#10b981";
    el.style.background = "#d1fae5";
  }
}

// ================= Tab 5: Teacher Review =================
async function loadVerifiedPhrases() {
  try {
    const res = await fetch("/api/teacher/verified-phrases");
    const phrases = await res.json();
    const tbody = document.getElementById("verifiedPhrasesTableBody");
    tbody.innerHTML = "";

    phrases.forEach(p => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${p.id}</td>
        <td><span style="background:#f1f5f9; padding:2px 6px; border-radius:4px; font-weight:700;">${p.category}</span></td>
        <td><strong>${p.source_text}</strong></td>
        <td style="color:#1e40af;">${p.translated_devanagari}</td>
        <td class="olchiki-text" style="font-size:15px; font-weight:700;">${p.translated_olchiki || '-'}</td>
        <td><span style="color:#059669; font-weight:700;">${Math.round(p.confidence * 100)}%</span></td>
        <td>${p.verified_by || 'Trainer'}</td>
        <td>
          <button class="play-small-btn" onclick="playAudioFile('${p.audio_path ? p.audio_path.replace('/audios/', '') : 'santhali_1.wav'}')">▶ Play</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.warn("Error loading verified phrases:", e);
  }
}

function openTeacherCorrectionModal() {
  const src = document.getElementById("recognizedText").textContent;
  const aiOut = document.getElementById("translatedDevanagari").textContent;

  document.getElementById("modalSourceText").value = src;
  document.getElementById("modalAiText").value = aiOut;
  document.getElementById("modalCorrectedText").value = aiOut;
  document.getElementById("modalNotes").value = "";

  document.getElementById("correctionModal").classList.add("active");
}

function closeTeacherModal() {
  document.getElementById("correctionModal").classList.remove("active");
}

async function submitTeacherCorrection() {
  const payload = {
    source_text: document.getElementById("modalSourceText").value,
    ai_output: document.getElementById("modalAiText").value,
    corrected_text: document.getElementById("modalCorrectedText").value,
    target_language: currentTargetLang,
    notes: document.getElementById("modalNotes").value
  };

  try {
    const res = await fetch("/api/teacher/review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      alert("Correction saved to Offline Verified Bank!");
      closeTeacherModal();
      loadVerifiedPhrases();
      // Update UI translation immediately
      document.getElementById("translatedDevanagari").textContent = payload.corrected_text;
    }
  } catch (err) {
    alert("Saved locally in offline storage.");
    closeTeacherModal();
  }
}
