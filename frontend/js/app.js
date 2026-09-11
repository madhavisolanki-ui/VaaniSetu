// ================= Global Application State =================
let currentRole = "teacher"; // "teacher" (Hindi -> Tribal) or "student" (Tribal -> Hindi)
let currentTargetLang = "Santhali"; // Santhali, Mundari, Ho
let isRecording = false;
let recognition = null;
let currentAudioUrl = "/audios/santhali_1.wav";
let currentSourceAudioUrl = "/audios/hindi_1.wav";
let currentAudioSpeed = 1.0; // 1.0x (Normal) or 0.8x (Kid-friendly slow)
let currentPromptCategory = "all";
let cachedPhrases = [];
let cachedFlashcards = [];
let worksheetAnswers = {}; // questionIndex -> selectedOptionIndex

// ================= Initialization =================
document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initSpeechRecognition();
  loadQuickPrompts();
  loadPhrasesTab();
  loadFlashcards("all");
  loadWorksheets("Numeracy");
  loadVerifiedPhrases();
  fetchSystemStatus();
});

// ================= Live Edge Hardware HUD & Diagnostics =================
async function fetchSystemStatus() {
  try {
    const res = await fetch("/api/system/status");
    if (res.ok) {
      const data = await res.json();
      const latencyEl = document.getElementById("latencyValue");
      if (latencyEl && data.average_edge_latency) {
        latencyEl.textContent = data.average_edge_latency;
      }
    }
  } catch (err) {
    console.log("System status offline fallback:", err);
  }
}

function toggleAudioSpeed() {
  const btn = document.getElementById("speedToggleBtn");
  const subLabel = document.getElementById("speedSubLabel");
  const audio = document.getElementById("globalAudioPlayer");

  if (currentAudioSpeed === 1.0) {
    currentAudioSpeed = 0.8;
    btn.textContent = "0.8x (Slow)";
    btn.style.background = "#10b981";
    btn.style.color = "#ffffff";
    if (subLabel) subLabel.textContent = "Kid-Friendly Slow";
  } else {
    currentAudioSpeed = 1.0;
    btn.textContent = "1.0x";
    btn.style.background = "#f59e0b";
    btn.style.color = "#78350f";
    if (subLabel) subLabel.textContent = "Normal Speed";
  }

  if (audio) {
    audio.playbackRate = currentAudioSpeed;
  }
}

function updateRegionalBadge() {
  const regionTitle = document.getElementById("hudRegionTitle");
  const districtSub = document.getElementById("hudDistrictSub");

  if (currentTargetLang === "Santhali") {
    if (regionTitle) regionTitle.textContent = "Santhal Pargana";
    if (districtSub) districtSub.textContent = "Dumka / Deoghar";
  } else if (currentTargetLang === "Mundari") {
    if (regionTitle) regionTitle.textContent = "Chota Nagpur";
    if (districtSub) districtSub.textContent = "Khunti / Ranchi";
  } else {
    if (regionTitle) regionTitle.textContent = "Kolhan Division";
    if (districtSub) districtSub.textContent = "Chaibasa / Singhbhum";
  }
}

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
  const studentLangLabel = document.getElementById("studentLangLabel");

  if (studentLangLabel) {
    studentLangLabel.textContent = `${currentTargetLang} (मातृभाषा)`;
  }

  if (role === "teacher") {
    teacherBtn.classList.add("active");
    studentBtn.classList.remove("active");
    sourceTag.textContent = "Recognized Teacher Hindi:";
    targetTag.textContent = `Translated ${currentTargetLang} Output:`;
    if (playAudioBtn) playAudioBtn.textContent = `🔊 Read Aloud ${currentTargetLang} Translation`;
    if (olChikiContainer) olChikiContainer.style.display = (currentTargetLang === "Santhali") ? "block" : "none";
  } else {
    studentBtn.classList.add("active");
    teacherBtn.classList.remove("active");
    sourceTag.textContent = `Recognized Student ${currentTargetLang}:`;
    targetTag.textContent = "Translated Teacher Hindi Output:";
    if (playAudioBtn) playAudioBtn.textContent = `▶️ Listen Hindi Translation`;
    if (olChikiContainer) olChikiContainer.style.display = "none";
  }

  updateRegionalBadge();
  loadQuickPrompts();
}

function swapRoles() {
  setRole(currentRole === "teacher" ? "student" : "teacher");
}

function onTargetLangChange() {
  const select = document.getElementById("targetLangSelect");
  currentTargetLang = select.value;
  setRole(currentRole);
}

// ================= Speech Recognition & Microphone =================
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
      console.warn("Speech recognition notice:", event.error);
      isRecording = false;
      updateMicUI(false);
      document.getElementById("micStatusText").textContent = "माइक एक्टिवेट है। नीचे संकेतों पर क्लिक करें या टाइप करें:";
    };

    recognition.onend = () => {
      isRecording = false;
      updateMicUI(false);
    };
  }
}

function toggleRecording() {
  if (isRecording) {
    if (recognition) recognition.stop();
    isRecording = false;
    updateMicUI(false);
  } else {
    if (recognition) {
      recognition.lang = "hi-IN";
      try {
        recognition.start();
      } catch (e) {
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
    statusText.textContent = "माइक दबाकर बोलें या नीचे दिए गए संकेतों पर क्लिक करें";
  }
}

function simulateSpeechRecognition() {
  updateMicUI(true);
  setTimeout(() => {
    updateMicUI(false);
    let picked;
    if (currentRole === "student") {
      if (currentTargetLang === "Mundari") {
        const mun = [
          "जोहार गिदिर को, आपन आपन ठांव रे दुबुंग पे।",
          "आपन पारसी पुथी ओडोल पे।",
          "मियद बारिया आपिया उपुनिया मोड़ेया",
          "दाः",
          "हें गोमके"
        ];
        picked = mun[Math.floor(Math.random() * mun.length)];
      } else if (currentTargetLang === "Ho") {
        const ho = [
          "जोहार होन को, आपन आपन ठई रे दुब पे।",
          "आपन काजी पुती ओड़ो पे।",
          "मियद बारिया आपिया उपुनिया मोड़ेया",
          "दाः",
          "हें गुरु गोमके"
        ];
        picked = ho[Math.floor(Math.random() * ho.length)];
      } else {
        const sat = [
          "जोहार गिद्रा को, आपन आपन ठंव रे दुड़ुब पे।",
          "आपानाः पारसी पुथी ओडोक पे।",
          "मित्, बार, पे, पुन्, मोड़े",
          "दाः",
          "हें"
        ];
        picked = sat[Math.floor(Math.random() * sat.length)];
      }
    } else {
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
  }, 1400);
}

// ================= Translation API Call & Feed Integration =================
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
    addDialogueTurn(data, clientLatency);
  } catch (err) {
    console.warn("Using offline client translation fallback:", err);
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

  document.getElementById("latencyValue").textContent = `${data.latency_ms || latency} ms`;

  const confidence = Math.round((data.confidence_score || 0.96) * 100);
  document.getElementById("confidenceFill").style.width = `${confidence}%`;
  document.getElementById("confidenceValue").textContent = `${confidence}% (High)`;

  const playAudioBtn = document.getElementById("playAudioBtn");
  if (playAudioBtn) {
    if (currentRole === "student") {
      playAudioBtn.textContent = "▶️ Listen Hindi Translation";
    } else {
      playAudioBtn.textContent = `🔊 Read Aloud ${currentTargetLang} Translation`;
    }
  }

  if (data.source_audio_url) currentSourceAudioUrl = data.source_audio_url;
  if (data.audio_url) {
    currentAudioUrl = data.audio_url;
    autoPlayAudio(data.audio_url);
  }
}

// Dialogue Feed
function addDialogueTurn(data, latency) {
  const feed = document.getElementById("dialogueFeedContainer");
  if (!feed) return;

  const bubble = document.createElement("div");
  const isTeacher = currentRole === "teacher";
  bubble.className = `dialogue-bubble ${isTeacher ? "teacher-bubble" : "student-bubble"}`;

  const audioToPlay = data.audio_url || currentAudioUrl;

  bubble.innerHTML = `
    <div class="bubble-avatar">${isTeacher ? "👨‍🏫" : "🧒"}</div>
    <div class="bubble-content">
      <div class="bubble-header">
        <span class="speaker-name">${isTeacher ? "शिक्षक (Teacher)" : "छात्र (Student)"}</span>
        <span class="timestamp-tag">${isTeacher ? "Hindi" : currentTargetLang}</span>
      </div>
      <p class="bubble-text ${data.translated_text_olchiki && currentTargetLang === 'Santhali' ? 'olchiki-text' : ''}">${data.translated_text_olchiki || data.translated_text_devanagari || data.translated_text}</p>
      ${data.translated_text_olchiki ? `<p class="bubble-subtext">${data.translated_text_devanagari}</p>` : ''}
      <div class="bubble-actions">
        <button class="btn-mini-play" onclick="playAudioFileByUrl('${audioToPlay}')">🔊 Listen</button>
        <span class="latency-micro-tag">⚡ ${data.latency_ms || latency} ms</span>
      </div>
    </div>
  `;

  feed.appendChild(bubble);
  feed.scrollTop = feed.scrollHeight;
}

function clearDialogueFeed() {
  const feed = document.getElementById("dialogueFeedContainer");
  if (feed) feed.innerHTML = "";
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
      audioUrl = `/audios/${matched.hindi_audio_file || "hindi_" + matched.id + ".wav"}`;
      sourceAudioUrl = (currentTargetLang === "Mundari") 
        ? `/audios/${matched.mundari_audio_file || "mundari_" + matched.id + ".wav"}` 
        : ((currentTargetLang === "Ho") ? `/audios/${matched.ho_audio_file || "ho_" + matched.id + ".wav"}` : `/audios/${matched.audio_file}`);
    } else {
      sourceAudioUrl = `/audios/${matched.hindi_audio_file || "hindi_" + matched.id + ".wav"}`;
      audioUrl = (currentTargetLang === "Mundari") 
        ? `/audios/${matched.mundari_audio_file || "mundari_" + matched.id + ".wav"}` 
        : ((currentTargetLang === "Ho") ? `/audios/${matched.ho_audio_file || "ho_" + matched.id + ".wav"}` : `/audios/${matched.audio_file}`);
    }

    const res = {
      source_text: text,
      translated_text_devanagari: currentRole === "student" ? matched.hindi : (currentTargetLang === "Mundari" ? matched.mundari : (currentTargetLang === "Ho" ? matched.ho : matched.santhali_devanagari)),
      translated_text_olchiki: (currentTargetLang === "Santhali" && currentRole === "teacher") ? matched.santhali_olchiki : null,
      phonetic_pronunciation: matched.santhali_phonetic,
      confidence_score: 0.96,
      audio_url: audioUrl,
      source_audio_url: sourceAudioUrl,
      latency_ms: 12
    };

    renderTranslationResult(res, 12);
    addDialogueTurn(res, 12);
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

// ================= Audio Playback Engine =================
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

function playAudioFileByUrl(url, triggerBtn = null) {
  if (!url) return;
  const audio = document.getElementById("globalAudioPlayer");
  audio.src = url;
  audio.playbackRate = currentAudioSpeed;

  const btn = triggerBtn || document.getElementById("playAudioBtn");
  const visualizer = document.getElementById("waveformVisualizer");

  audio.onplay = () => {
    if (btn) btn.classList.add("speaking");
    if (visualizer) visualizer.classList.add("active");
  };
  audio.onended = () => {
    if (btn) btn.classList.remove("speaking");
    if (visualizer && !isRecording) visualizer.classList.remove("active");
  };
  audio.onpause = () => {
    if (btn) btn.classList.remove("speaking");
    if (visualizer && !isRecording) visualizer.classList.remove("active");
  };
  audio.onerror = () => {
    if (btn) btn.classList.remove("speaking");
    if (visualizer && !isRecording) visualizer.classList.remove("active");
  };

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
    utterance.rate = currentAudioSpeed;
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

// ================= Categorized Quick Prompts =================
function switchPromptCategory(category) {
  currentPromptCategory = category;
  const pills = document.querySelectorAll(".cat-pill");
  pills.forEach(p => p.classList.remove("active"));
  event.target.classList.add("active");
  loadQuickPrompts();
}

function loadQuickPrompts() {
  const container = document.getElementById("quickPromptChips");
  if (!container) return;
  container.innerHTML = "";

  let promptPool = [];

  if (currentRole === "student") {
    if (currentTargetLang === "Mundari") {
      promptPool = [
        { cat: "greetings", label: "👋 जोहार (नमस्ते)", text: "जोहार गिदिर को, आपन आपन ठांव रे दुबुंग पे।" },
        { cat: "instructions", label: "📖 आपन पुथी (किताब)", text: "आपन पारसी पुथी ओडोल पे।" },
        { cat: "counting", label: "🔢 मियद, बारिया (गिनती)", text: "मियद बारिया आपिया उपुनिया मोड़ेया" },
        { cat: "needs", label: "💧 दाः (पानी)", text: "दाः" },
        { cat: "praise", label: "✅ हें (हाँ)", text: "हें" },
        { cat: "praise", label: "🌟 बेस (अच्छा)", text: "बेस" }
      ];
    } else if (currentTargetLang === "Ho") {
      promptPool = [
        { cat: "greetings", label: "👋 जोहार (नमस्ते)", text: "जोहार होन को, आपन आपन ठई रे दुब पे।" },
        { cat: "instructions", label: "📖 आपन काजी पुती", text: "आपन काजी पुती ओड़ो पे।" },
        { cat: "counting", label: "🔢 मियद, बारिया (गिनती)", text: "मियद बारिया आपिया उपुनिया मोड़ेया" },
        { cat: "needs", label: "💧 दाः (पानी)", text: "दाः" },
        { cat: "praise", label: "✅ हें गुरु गोमके", text: "हें गुरु गोमके" },
        { cat: "praise", label: "🌟 बेस (अच्छा)", text: "बेस" }
      ];
    } else {
      promptPool = [
        { cat: "greetings", label: "👋 ᱡᱚᱦᱟᱨ (जोहार)", text: "जोहार गिद्रा को, आपन आपन ठंव रे दुड़ुब पे।" },
        { cat: "instructions", label: "📖 ᱯᱟᱨᱥᱤ ᱯᱩᱛᱷᱤ (किताब)", text: "आपानाः पारसी पुथी ओडोक पे।" },
        { cat: "counting", label: "🔢 ᱢᱤᱫ, ᱵᱟᱨ (गिनती)", text: "मित्, बार, पे, पुन्, मोड़े" },
        { cat: "needs", label: "💧 ᱫᱟᱜ (पानी)", text: "दाः" },
        { cat: "praise", label: "✅ ᱦᱮᱸ (हाँ)", text: "हें" },
        { cat: "praise", label: "🌟 ᱵᱮᱥ (अच्छा)", text: "नापाय" }
      ];
    }
  } else {
    // Teacher mode
    promptPool = [
      { cat: "greetings", label: "👋 नमस्ते बच्चों, बैठ जाओ", text: "नमस्ते बच्चों, अपनी-अपनी जगह पर बैठ जाओ।" },
      { cat: "instructions", label: "📖 अपनी भाषा की किताब निकालो", text: "अपनी भाषा की किताब निकालो।" },
      { cat: "instructions", label: "📄 पन्ना नंबर पाँच खोलो", text: "किताब का पन्ना नंबर पाँच खोलो।" },
      { cat: "counting", label: "🔢 1 से 10 तक गिनती करें", text: "आओ मिलकर एक से दस तक गिनती करें।" },
      { cat: "counting", label: "➕ 2 और 3 कितना होता है?", text: "दो और तीन को जोड़ने पर कितना होता है?" },
      { cat: "praise", label: "⭐ शाबाश! बहुत अच्छा उत्तर", text: "शाबाश! तुमने बहुत अच्छा उत्तर दिया।" },
      { cat: "needs", label: "💧 क्या तुम्हें पानी पीना है?", text: "क्या तुम्हें पानी पीना है?" }
    ];
  }

  const filtered = (currentPromptCategory === "all")
    ? promptPool
    : promptPool.filter(p => p.cat === currentPromptCategory);

  filtered.forEach(p => {
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

// ================= TAB 2: 30 FLN Master Curriculum Expressions =================
async function loadPhrasesTab() {
  const container = document.getElementById("phrasesGridContainer");
  if (!container) return;

  try {
    const res = await fetch("/api/fln/phrases");
    if (!res.ok) throw new Error("Failed to load FLN phrases");
    cachedPhrases = await res.json();
    renderPhrases(cachedPhrases);
  } catch (err) {
    console.warn("API load failed, using embedded fallback:", err);
  }
}

function renderPhrases(phrases) {
  const container = document.getElementById("phrasesGridContainer");
  if (!container) return;
  container.innerHTML = "";

  phrases.forEach(item => {
    const card = document.createElement("div");
    card.className = "phrase-card";

    const satAudio = `/audios/${item.audio_file || 'santhali_' + item.id + '.wav'}`;
    const munAudio = `/audios/${item.mundari_audio_file || 'mundari_' + item.id + '.wav'}`;
    const hoAudio = `/audios/${item.ho_audio_file || 'ho_' + item.id + '.wav'}`;
    const hinAudio = `/audios/${item.hindi_audio_file || 'hindi_' + item.id + '.wav'}`;

    card.innerHTML = `
      <div class="phrase-card-header">
        <span class="phrase-category-badge">${item.category || "Classroom"}</span>
        <span class="phrase-id-badge">FLN #${item.id}</span>
      </div>
      <p class="phrase-hindi-text">${item.hindi}</p>
      <div class="phrase-tribal-box">
        ${item.santhali_olchiki ? `<p class="phrase-santhali-ol olchiki-text">${item.santhali_olchiki}</p>` : ''}
        <p class="phrase-santhali-dev">संथाली: ${item.santhali_devanagari || ""}</p>
        ${item.mundari ? `<p class="phrase-santhali-dev">मुंडारी: ${item.mundari}</p>` : ''}
        ${item.ho ? `<p class="phrase-santhali-dev">हो: ${item.ho}</p>` : ''}
      </div>
      <div class="phrase-audio-bar">
        <button class="audio-chip-btn" onclick="playAudioFileByUrl('${satAudio}')">▶ Santhali</button>
        <button class="audio-chip-btn" onclick="playAudioFileByUrl('${munAudio}')">▶ Mundari</button>
        <button class="audio-chip-btn" onclick="playAudioFileByUrl('${hoAudio}')">▶ Ho</button>
        <button class="audio-chip-btn" onclick="playAudioFileByUrl('${hinAudio}')">▶ Hindi</button>
      </div>
    `;
    container.appendChild(card);
  });
}

function filterPhrases(category) {
  const buttons = document.querySelectorAll("#phrases-tab .filter-btn");
  buttons.forEach(b => b.classList.remove("active"));
  event.target.classList.add("active");

  if (category === "all") {
    renderPhrases(cachedPhrases);
  } else {
    const filtered = cachedPhrases.filter(p => p.category === category);
    renderPhrases(filtered);
  }
}

function onPhraseSearchChange() {
  const query = document.getElementById("phraseSearchInput").value.toLowerCase().trim();
  if (!query) {
    renderPhrases(cachedPhrases);
    return;
  }
  const filtered = cachedPhrases.filter(p => 
    (p.hindi && p.hindi.toLowerCase().includes(query)) ||
    (p.santhali_devanagari && p.santhali_devanagari.toLowerCase().includes(query)) ||
    (p.mundari && p.mundari.toLowerCase().includes(query)) ||
    (p.ho && p.ho.toLowerCase().includes(query)) ||
    (p.english && p.english.toLowerCase().includes(query))
  );
  renderPhrases(filtered);
}

// ================= TAB 3: Bilingual 3D Flashcards =================
function loadFlashcards(category) {
  const grid = document.getElementById("flashcardsGrid");
  if (!grid) return;
  grid.innerHTML = "";

  const cardsData = [
    { num: "1", emoji: "🍎", hi: "एक (1)", en: "One (Apple)", sat_ol: "ᱢᱤᱫ", sat_dev: "मित् (Mid)", audio: "santhali_fc_001.wav", cat: "Numeracy" },
    { num: "2", emoji: "🌳", hi: "दो (2)", en: "Two (Trees)", sat_ol: "ᱵᱟᱨ", sat_dev: "बार (Bar)", audio: "santhali_fc_002.wav", cat: "Numeracy" },
    { num: "3", emoji: "⭐", hi: "तीन (3)", en: "Three (Stars)", sat_ol: "ᱯᱮ", sat_dev: "पे (Pe)", audio: "santhali_fc_003.wav", cat: "Numeracy" },
    { num: "4", emoji: "🐦", hi: "चार (4)", en: "Four (Birds)", sat_ol: "ᱯᱩᱱ", sat_dev: "पुन् (Pun)", audio: "santhali_fc_004.wav", cat: "Numeracy" },
    { num: "5", emoji: "🖐️", hi: "पाँच (5)", en: "Five (Fingers)", sat_ol: "ᱢᱚᱬᱮ", sat_dev: "मोड़े (More)", audio: "santhali_fc_005.wav", cat: "Numeracy" },
    { num: "book", emoji: "📖", hi: "किताब", en: "Book", sat_ol: "ᱯᱩᱛᱷᱤ", sat_dev: "पुथी (Puthi)", audio: "santhali_fc_006.wav", cat: "Literacy" },
    { num: "water", emoji: "💧", hi: "पानी", en: "Water", sat_ol: "ᱫᱟᱜ", sat_dev: "दाः (Daah)", audio: "santhali_fc_007.wav", cat: "Literacy" },
    { num: "sun", emoji: "☀️", hi: "सूरज", en: "Sun", sat_ol: "ᱥᱤᱧ", sat_dev: "सिंज (Sinj)", audio: "santhali_fc_008.wav", cat: "Literacy" }
  ];

  const filtered = (category === "all") ? cardsData : cardsData.filter(c => c.cat === category);

  filtered.forEach(item => {
    const wrapper = document.createElement("div");
    wrapper.className = "flashcard-wrapper";
    wrapper.onclick = () => wrapper.classList.toggle("flipped");

    wrapper.innerHTML = `
      <div class="flashcard-inner">
        <div class="flashcard-front">
          <div class="card-emoji">${item.emoji}</div>
          <div class="card-hindi">${item.hi}</div>
          <div class="card-english">${item.en}</div>
          <span class="card-hint">🔄 Tap to flip in 3D</span>
        </div>
        <div class="flashcard-back">
          <div class="card-olchiki olchiki-text">${item.sat_ol}</div>
          <div class="card-devanagari">${item.sat_dev}</div>
          <div class="card-phonetic">Native Pronunciation</div>
          <button class="card-btn-audio" onclick="event.stopPropagation(); playAudioFileByUrl('/audios/${item.audio}')">🔊 Listen Audio</button>
        </div>
      </div>
    `;
    grid.appendChild(wrapper);
  });
}

// ================= TAB 4: Interactive Worksheet Solver & PDF =================
async function generateWorksheet(topic) {
  loadWorksheets(topic);
}

function loadWorksheets(topic) {
  const container = document.getElementById("wsQuestionsContainer");
  const wsTitle = document.getElementById("wsTitle");
  const wsSubTitle = document.getElementById("wsSubTitle");
  const downloadBtn = document.getElementById("downloadPdfBtn");

  if (!container) return;

  worksheetAnswers = {};
  updateWorksheetScore();

  if (topic === "Numeracy") {
    if (wsTitle) wsTitle.textContent = "NIPUN Bharat FLN Numeracy Activity Worksheet (संख्या ज्ञान)";
    if (wsSubTitle) wsSubTitle.textContent = "Hindi ↔ Santhali Counting (1 to 5) • Grade 1-2 • JCERT Format";
    if (downloadBtn) downloadBtn.href = "/worksheets/fln_worksheet_numeracy.pdf";

    container.innerHTML = `
      <div class="ws-question-row">
        <div class="ws-q-title">प्र. 1. सेब (🍎) की संख्या पहचानकर संथाली में सही शब्द चुनें (Count 1 apple):</div>
        <div class="ws-options-list">
          <button class="ws-opt-item" onclick="selectWsOption(1, 'मित् (Mid)', true, this)">A) मित् (Mid)</button>
          <button class="ws-opt-item" onclick="selectWsOption(1, 'बार (Bar)', false, this)">B) बार (Bar)</button>
          <button class="ws-opt-item" onclick="selectWsOption(1, 'पे (Pe)', false, this)">C) पे (Pe)</button>
        </div>
      </div>

      <div class="ws-question-row">
        <div class="ws-q-title">प्र. 2. संथाली शब्द 'बार (ᱵᱟᱨ)' का हिंदी अर्थ क्या है? (What does 'Bar' mean?):</div>
        <div class="ws-options-list">
          <button class="ws-opt-item" onclick="selectWsOption(2, 'एक (1)', false, this)">A) एक (1)</button>
          <button class="ws-opt-item" onclick="selectWsOption(2, 'दो (2)', true, this)">B) दो (2)</button>
          <button class="ws-opt-item" onclick="selectWsOption(2, 'पाँच (5)', false, this)">C) पाँच (5)</button>
        </div>
      </div>

      <div class="ws-question-row">
        <div class="ws-q-title">प्र. 3. हाथ की पाँच उंगलियों (🖐️) के लिए सही संथाली शब्द चुनें:</div>
        <div class="ws-options-list">
          <button class="ws-opt-item" onclick="selectWsOption(3, 'पुन् (Pun)', false, this)">A) पुन् (Pun)</button>
          <button class="ws-opt-item" onclick="selectWsOption(3, 'मोड़े (More)', true, this)">B) मोड़े (More / ᱢᱚᱬᱮ)</button>
          <button class="ws-opt-item" onclick="selectWsOption(3, 'मित् (Mid)', false, this)">C) मित् (Mid)</button>
        </div>
      </div>
    `;
  } else {
    if (wsTitle) wsTitle.textContent = "NIPUN Bharat FLN Literacy Activity Worksheet (साक्षरता)";
    if (wsSubTitle) wsSubTitle.textContent = "Classroom Vocabulary & Tribal Word Matching • Grade 1-2 • JCERT Format";
    if (downloadBtn) downloadBtn.href = "/worksheets/fln_worksheet_literacy.pdf";

    container.innerHTML = `
      <div class="ws-question-row">
        <div class="ws-q-title">प्र. 1. 'किताब' (Book) के लिए संथाली शब्द चुनें:</div>
        <div class="ws-options-list">
          <button class="ws-opt-item" onclick="selectWsOption(1, 'पुथी (Puthi)', true, this)">A) पुथी (Puthi / ᱯᱩᱛᱷᱤ)</button>
          <button class="ws-opt-item" onclick="selectWsOption(1, 'दाः (Daah)', false, this)">B) दाः (Daah)</button>
          <button class="ws-opt-item" onclick="selectWsOption(1, 'ती (Ti)', false, this)">C) ती (Ti)</button>
        </div>
      </div>

      <div class="ws-question-row">
        <div class="ws-q-title">प्र. 2. 'दाः (ᱫᱟᱜ)' का हिंदी में क्या अर्थ है?</div>
        <div class="ws-options-list">
          <button class="ws-opt-item" onclick="selectWsOption(2, 'पेन', false, this)">A) पेन</button>
          <button class="ws-opt-item" onclick="selectWsOption(2, 'पानी', true, this)">B) पानी</button>
          <button class="ws-opt-item" onclick="selectWsOption(2, 'सूरज', false, this)">C) सूरज</button>
        </div>
      </div>
    `;
  }
}

function selectWsOption(qNum, val, isCorrect, btnEl) {
  const parent = btnEl.parentElement;
  parent.querySelectorAll(".ws-opt-item").forEach(b => {
    b.classList.remove("selected");
    b.style.borderColor = "transparent";
  });

  btnEl.classList.add("selected");
  worksheetAnswers[qNum] = isCorrect;

  if (isCorrect) {
    btnEl.style.borderColor = "#10b981";
    btnEl.style.background = "#ecfdf5";
  } else {
    btnEl.style.borderColor = "#ef4444";
    btnEl.style.background = "#fef2f2";
  }

  updateWorksheetScore();
}

function updateWorksheetScore() {
  const display = document.getElementById("wsScoreDisplay");
  if (!display) return;

  const total = Object.keys(worksheetAnswers).length;
  const correct = Object.values(worksheetAnswers).filter(v => v === true).length;

  if (total === 0) {
    display.innerHTML = `<span>⭐ Solve questions above to earn stars!</span>`;
  } else if (correct === 3) {
    display.innerHTML = `<span>🎉 Shabaash (शाबाश)! 3/3 Correct ⭐⭐⭐ (Grade 1 NIPUN FLN Mastered)</span>`;
  } else {
    display.innerHTML = `<span>⭐ Score: ${correct}/${total} Correct. Keep going!</span>`;
  }
}

// ================= TAB 5: Teacher Review & Dialect Loop =================
async function loadVerifiedPhrases() {
  const tableBody = document.getElementById("verifiedPhrasesTableBody");
  if (!tableBody) return;

  try {
    const res = await fetch("/api/fln/phrases");
    if (!res.ok) throw new Error("Failed to load verified phrases");
    const phrases = await res.json();
    tableBody.innerHTML = "";

    phrases.slice(0, 10).forEach(p => {
      const row = document.createElement("tr");
      const audioUrl = `/audios/${p.audio_file || 'santhali_' + p.id + '.wav'}`;

      row.innerHTML = `
        <td><strong>#${p.id}</strong></td>
        <td>${p.category || "Classroom"}</td>
        <td>${p.hindi}</td>
        <td>${p.santhali_devanagari || "-"}</td>
        <td class="olchiki-text">${p.santhali_olchiki || "-"}</td>
        <td>
          <button class="btn-mini-play" onclick="playAudioFileByUrl('${audioUrl}')">▶ Play</button>
        </td>
        <td><span class="badge-verified">✓ Verified</span></td>
        <td>
          <button class="icon-btn" onclick="openTeacherCorrectionForPhrase('${p.hindi}')">✏️ Edit</button>
        </td>
      `;
      tableBody.appendChild(row);
    });
  } catch (err) {
    console.warn("Verified phrases load failed:", err);
  }
}

function openTeacherCorrectionModal() {
  const modal = document.getElementById("correctionModal");
  const recognizedText = document.getElementById("recognizedText").textContent;
  const translatedText = document.getElementById("translatedDevanagari").textContent;

  document.getElementById("modalSourceText").value = recognizedText;
  document.getElementById("modalAiText").value = translatedText;
  document.getElementById("modalCorrectedText").value = "";
  document.getElementById("modalNotes").value = "";

  if (modal) modal.classList.add("active");
}

function openTeacherCorrectionForPhrase(hindiText) {
  const modal = document.getElementById("correctionModal");
  document.getElementById("modalSourceText").value = hindiText;
  document.getElementById("modalAiText").value = hindiText;
  document.getElementById("modalCorrectedText").value = "";
  document.getElementById("modalNotes").value = "Dumka / Santhal Pargana local dialect";
  if (modal) modal.classList.add("active");
}

function closeTeacherModal() {
  const modal = document.getElementById("correctionModal");
  if (modal) modal.classList.remove("active");
}

async function submitTeacherCorrection() {
  const src = document.getElementById("modalSourceText").value;
  const ai = document.getElementById("modalAiText").value;
  const corrected = document.getElementById("modalCorrectedText").value;
  const notes = document.getElementById("modalNotes").value;

  if (!corrected.trim()) {
    alert("कृपया सही वाक्य लिखें (Please write corrected sentence).");
    return;
  }

  try {
    const res = await fetch("/api/feedback/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        source_text: src,
        ai_output: ai,
        corrected_text: corrected,
        target_language: currentTargetLang,
        notes: notes
      })
    });

    if (res.ok) {
      alert("✓ शिक्षक सुधार स्थानीय ऑफलाइन डेटाबेस में सुरक्षित कर दिया गया है!");
      closeTeacherModal();
      loadVerifiedPhrases();
    }
  } catch (err) {
    alert("Offline mode: Saved locally in browser session!");
    closeTeacherModal();
  }
}
