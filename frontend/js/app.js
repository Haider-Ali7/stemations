/**
 * Stemations - Minimal, Modern JavaScript Controller
 * Connects clean minimal UI with FastAPI SSE streaming agent.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Generator Inputs
  const topicInput = document.getElementById("topic-input");
  const modelSelect = document.getElementById("model-select");
  const modelSelectMobile = document.getElementById("model-select-mobile");
  const generationForm = document.getElementById("generation-form");
  const btnGenerate = document.getElementById("btn-generate");
  const generateSpinner = document.getElementById("generate-spinner");
  const generateIcon = document.getElementById("generate-icon");
  const generateBtnLabel = document.getElementById("generate-btn-label");

  // Orchestration & Streaming Console
  const orchestrationSection = document.getElementById("orchestration-section");
  const stageBadge = document.getElementById("stage-badge");
  const consoleFeed = document.getElementById("console-feed");
  const consoleClock = document.getElementById("console-clock");

  // Showcase Elements
  const showcaseSection = document.getElementById("showcase-section");
  const showcaseTitle = document.getElementById("showcase-title");
  const showcaseMeta = document.getElementById("showcase-meta");
  const primaryVideoPlayer = document.getElementById("primary-video-player");
  const primaryVideoSource = document.getElementById("primary-video-source");
  const btnDownloadVideo = document.getElementById("btn-download-video");
  const btnCopyLink = document.getElementById("btn-copy-link");

  // Tabs Elements
  const tabBtnScript = document.getElementById("tab-btn-script");
  const tabBtnCode = document.getElementById("tab-btn-code");
  const tabBtnPathway = document.getElementById("tab-btn-pathway");
  const tabPaneScript = document.getElementById("tab-pane-script");
  const tabPaneCode = document.getElementById("tab-pane-code");
  const tabPanePathway = document.getElementById("tab-pane-pathway");
  const deckScriptText = document.getElementById("deck-script-text");
  const scriptWordCount = document.getElementById("script-word-count");
  const deckCodeText = document.getElementById("deck-code-text");
  const deckPathwayList = document.getElementById("deck-pathway-list");
  const btnCopyCode = document.getElementById("btn-copy-code");

  // Examples Grid / Reel
  const videoReel = document.getElementById("video-reel");
  const btnReelPrev = document.getElementById("btn-reel-prev");
  const btnReelNext = document.getElementById("btn-reel-next");

  // Modals
  const modalVideo = document.getElementById("modal-video");
  const modalPlayer = document.getElementById("modal-player");
  const modalPlayerSource = document.getElementById("modal-player-source");
  const modalVideoTitle = document.getElementById("modal-video-title");
  const modalDownloadBtn = document.getElementById("modal-download-btn");
  const modalVideoClose = document.getElementById("modal-video-close");

  const modalDiagnostic = document.getElementById("modal-diagnostic");
  const modalDiagnosticClose = document.getElementById("modal-diagnostic-close");
  const modalDiagnosticRefresh = document.getElementById("modal-diagnostic-refresh");
  const btnDiagnosticOpen = document.getElementById("btn-diagnostic-open");
  const diagnosticLines = document.getElementById("diagnostic-lines");
  const diagnosticStatusText = document.getElementById("diagnostic-status-text");

  // Mobile Menu
  const btnMobileMenu = document.getElementById("btn-mobile-menu");
  const btnMobileMenuClose = document.getElementById("btn-mobile-menu-close");
  const mobileMenuOverlay = document.getElementById("mobile-menu-overlay");
  const mobileMenuDrawer = document.getElementById("mobile-menu-drawer");

  let timerInterval = null;
  let activeEventSource = null;
  let reelScrollIndex = 0;

  // 1. Initial State Loading
  loadModels();
  checkSystemHealth();
  loadRecentVideos();
  setupHeroVideoFallback();

  // Sync model selectors (desktop ↔ mobile)
  if (modelSelect && modelSelectMobile) {
    modelSelect.addEventListener("change", () => {
      modelSelectMobile.value = modelSelect.value;
    });
    modelSelectMobile.addEventListener("change", () => {
      modelSelect.value = modelSelectMobile.value;
    });
  }

  // 2. Quick Starter Chips
  document.querySelectorAll(".chip-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const topic = btn.getAttribute("data-topic");
      if (topic) {
        topicInput.value = topic;
        topicInput.focus();
      }
    });
  });

  // 3. Generation Form Submission
  generationForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const topic = topicInput.value.trim();
    if (!topic) return;

    const model = modelSelect ? modelSelect.value : (modelSelectMobile ? modelSelectMobile.value : "");
    startGenerationStream(topic, model);
  });

  function startGenerationStream(topic, model) {
    setGeneratingState(true);

    // Reset console & stage markers
    consoleFeed.innerHTML = "";
    resetStageHighlights();
    highlightStage(1);
    stageBadge.textContent = "Analyzing Topic";

    orchestrationSection.classList.remove("hidden");
    orchestrationSection.scrollIntoView({ behavior: "smooth", block: "nearest" });

    // Start timer
    let seconds = 0;
    consoleClock.textContent = "00:00";
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
      seconds++;
      const mins = String(Math.floor(seconds / 60)).padStart(2, "0");
      const secs = String(seconds % 60).padStart(2, "0");
      consoleClock.textContent = `${mins}:${secs}`;
    }, 1000);

    if (activeEventSource) {
      activeEventSource.close();
    }

    const sseUrl = `/api/generate/stream?topic=${encodeURIComponent(topic)}&model=${encodeURIComponent(model)}`;
    activeEventSource = new EventSource(sseUrl);

    activeEventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === "step") {
          appendConsoleMessage(data.phase, data.message);
          updateStageProgress(data.phase);
        } else if (data.type === "complete") {
          activeEventSource.close();
          clearInterval(timerInterval);
          setGeneratingState(false);

          if (data.success) {
            stageBadge.textContent = "Complete";
            highlightStage(5);
            handleGenerationSuccess(data);
          } else {
            stageBadge.textContent = "Offline Reference";
            handleGenerationFallback(data, topic);
          }
        } else if (data.type === "error") {
          activeEventSource.close();
          clearInterval(timerInterval);
          setGeneratingState(false);
          appendConsoleMessage("ERROR", data.message || "Synthesis process halted.");
        }
      } catch (err) {
        console.error("Error parsing SSE:", err);
      }
    };

    activeEventSource.onerror = (err) => {
      console.warn("SSE stream closed:", err);
      activeEventSource.close();
      clearInterval(timerInterval);
      setGeneratingState(false);
    };
  }

  function setGeneratingState(isGenerating) {
    btnGenerate.disabled = isGenerating;
    if (isGenerating) {
      generateSpinner.classList.remove("hidden");
      generateIcon.classList.add("hidden");
      generateBtnLabel.textContent = "Generating...";
      btnGenerate.classList.add("opacity-80", "cursor-not-allowed");
    } else {
      generateSpinner.classList.add("hidden");
      generateIcon.classList.remove("hidden");
      generateBtnLabel.textContent = "Generate Video";
      btnGenerate.classList.remove("opacity-80", "cursor-not-allowed");
    }
  }

  function appendConsoleMessage(phase, message) {
    const row = document.createElement("div");
    row.className = "flex items-start gap-2 text-xs py-1 border-b border-slate-800/50";

    const badge = document.createElement("span");
    badge.className = "px-1.5 py-0.5 rounded text-[10px] font-bold font-mono " + getBadgeColor(phase);
    badge.textContent = phase;

    const text = document.createElement("span");
    text.className = "text-slate-300 flex-grow";
    text.textContent = message;

    row.appendChild(badge);
    row.appendChild(text);
    consoleFeed.appendChild(row);

    consoleFeed.scrollTop = consoleFeed.scrollHeight;
  }

  function getBadgeColor(phase) {
    const p = phase.toUpperCase();
    if (p.includes("PLAN") || p.includes("SKILL")) return "bg-orange/20 text-orange";
    if (p.includes("MANIM") || p.includes("RENDER")) return "bg-emerald-500/20 text-emerald-400";
    if (p.includes("TTS") || p.includes("VOICE")) return "bg-purple-500/20 text-purple-400";
    return "bg-slate-800 text-slate-300";
  }

  function updateStageProgress(phase) {
    const p = phase.toUpperCase();
    if (p === "SKILL_LOAD" || p === "PLAN") {
      highlightStage(1);
      stageBadge.textContent = "Structuring Lesson";
    } else if (p === "LLM_PLAN" || p === "CODE_READY") {
      highlightStage(2);
      stageBadge.textContent = "Designing Geometry";
    } else if (p === "TOOL_MANIM" || p === "SELF_HEAL" || p === "RENDER_SUCCESS") {
      highlightStage(3);
      stageBadge.textContent = "Rendering Vectors";
    } else if (p === "TOOL_TTS" || p === "TTS_SUCCESS") {
      highlightStage(4);
      stageBadge.textContent = "Synthesizing Audio";
    } else if (p === "TOOL_COMPOSE" || p === "COMPLETE") {
      highlightStage(5);
      stageBadge.textContent = "Final Composition";
    }
  }

  function resetStageHighlights() {
    for (let i = 1; i <= 5; i++) {
      const col = document.getElementById(`step-col-${i}`);
      if (col) col.className = "p-2 rounded-xl border border-border bg-soft text-muted text-xs";
    }
  }

  function highlightStage(num) {
    for (let i = 1; i <= num; i++) {
      const col = document.getElementById(`step-col-${i}`);
      if (col) {
        if (i === num) {
          col.className = "p-2 rounded-xl border-2 border-orange bg-white text-orange font-semibold text-xs";
        } else {
          col.className = "p-2 rounded-xl border border-border bg-white text-heading text-xs";
        }
      }
    }
  }

  // 4. Generation Success & Inspector Deck
  function handleGenerationSuccess(data) {
    showcaseTitle.textContent = data.topic;
    showcaseMeta.textContent = `1080×1920 Mobile Format • ${data.model_used || "Gemma 4"}`;

    if (data.video_url) {
      primaryVideoSource.src = data.video_url;
      primaryVideoPlayer.load();
      btnDownloadVideo.href = `${data.video_url}?download=true`;
      btnDownloadVideo.setAttribute("download", `stemation_${data.topic.toLowerCase().replace(/\s+/g, "_")}.mp4`);
    }

    deckScriptText.textContent = data.script || "Script synthesized.";
    const words = data.script ? data.script.split(/\s+/).filter(Boolean).length : 0;
    scriptWordCount.textContent = `${words} words`;

    deckCodeText.textContent = data.manim_code || "# Scene code compiled successfully";

    renderPathwayRecommendations(data.next_topics || []);

    showcaseSection.classList.remove("hidden");
    showcaseSection.scrollIntoView({ behavior: "smooth", block: "start" });

    loadRecentVideos();
  }

  function handleGenerationFallback(data, topic) {
    if (data.cached_demo && data.cached_demo.video_url) {
      showcaseTitle.textContent = `${data.cached_demo.title || topic} (Reference)`;
      showcaseMeta.textContent = "Verified reference video loaded.";

      primaryVideoSource.src = data.cached_demo.video_url;
      primaryVideoPlayer.load();
      btnDownloadVideo.href = data.cached_demo.video_url;

      deckScriptText.textContent = data.cached_demo.script || "Reference script.";
      deckCodeText.textContent = data.cached_demo.manim_code || "# Reference code";

      showcaseSection.classList.remove("hidden");
      showcaseSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  function renderPathwayRecommendations(topics) {
    deckPathwayList.innerHTML = "";
    if (!topics || topics.length === 0) {
      deckPathwayList.innerHTML = `<div class="text-xs text-muted py-2">No follow-up pathway topics.</div>`;
      return;
    }

    topics.forEach((nextTopic, idx) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "w-full text-left p-2.5 rounded-xl border border-border bg-soft hover:border-orange hover:bg-white transition-all flex items-center justify-between group";

      btn.innerHTML = `
        <span class="text-xs font-medium text-heading group-hover:text-orange">${idx + 1}. ${nextTopic}</span>
        <span class="text-xs text-orange opacity-0 group-hover:opacity-100 transition-opacity">Generate →</span>
      `;

      btn.addEventListener("click", () => {
        topicInput.value = nextTopic;
        const model = modelSelect ? modelSelect.value : "";
        startGenerationStream(nextTopic, model);
      });

      deckPathwayList.appendChild(btn);
    });
  }

  // 5. Tabs Switching
  function switchTab(activeBtn, activePane) {
    [tabBtnScript, tabBtnCode, tabBtnPathway].forEach((btn) => {
      btn.className = "px-3 py-1.5 rounded-lg text-muted hover:text-heading transition-colors";
    });
    [tabPaneScript, tabPaneCode, tabPanePathway].forEach((pane) => {
      pane.classList.add("hidden");
    });

    activeBtn.className = "px-3 py-1.5 rounded-lg bg-soft border border-border text-heading";
    activePane.classList.remove("hidden");
  }

  tabBtnScript.addEventListener("click", () => switchTab(tabBtnScript, tabPaneScript));
  tabBtnCode.addEventListener("click", () => switchTab(tabBtnCode, tabPaneCode));
  tabBtnPathway.addEventListener("click", () => switchTab(tabBtnPathway, tabPanePathway));

  btnCopyCode.addEventListener("click", () => {
    navigator.clipboard.writeText(deckCodeText.textContent).then(() => {
      btnCopyCode.textContent = "Copied!";
      setTimeout(() => (btnCopyCode.textContent = "Copy Code"), 2000);
    });
  });

  btnCopyLink.addEventListener("click", () => {
    navigator.clipboard.writeText(window.location.href).then(() => {
      btnCopyLink.textContent = "Copied!";
      setTimeout(() => (btnCopyLink.textContent = "Copy Link"), 2000);
    });
  });

  // 6. Examples Grid with Hover-To-Play
  let allLoadedVideos = [];

  async function loadRecentVideos() {
    try {
      const res = await fetch("/api/recent-videos?limit=12");
      if (!res.ok) throw new Error("Recent videos fetch failed");
      const data = await res.json();
      allLoadedVideos = data.videos || [];
      reelScrollIndex = 0;
      renderVideoGrid(getVisibleVideos());
    } catch (err) {
      console.warn("Could not load recent videos:", err);
      videoReel.innerHTML = `<div class="p-6 text-center text-muted text-xs col-span-full">Examples archive ready. Use generator above.</div>`;
    }
  }

  function getVisibleVideos() {
    // Show 4 at a time on desktop
    const perPage = 4;
    return allLoadedVideos.slice(reelScrollIndex, reelScrollIndex + perPage);
  }

  // Reel navigation buttons
  if (btnReelPrev) {
    btnReelPrev.addEventListener("click", () => {
      if (reelScrollIndex > 0) {
        reelScrollIndex = Math.max(0, reelScrollIndex - 4);
        renderVideoGrid(getVisibleVideos());
      }
    });
  }

  if (btnReelNext) {
    btnReelNext.addEventListener("click", () => {
      if (reelScrollIndex + 4 < allLoadedVideos.length) {
        reelScrollIndex += 4;
        renderVideoGrid(getVisibleVideos());
      }
    });
  }

  function renderVideoGrid(videos) {
    videoReel.innerHTML = "";
    if (videos.length === 0) {
      videoReel.innerHTML = `<div class="p-6 text-center text-muted text-xs col-span-full">No videos rendered yet.</div>`;
      return;
    }

    videos.forEach((vid) => {
      const card = document.createElement("div");
      card.className = "example-card flex flex-col justify-between";

      card.innerHTML = `
        <div class="example-thumbnail group cursor-pointer">
          <video src="${vid.url}" preload="metadata" muted playsinline loop></video>
          <div class="absolute inset-0 bg-black/25 group-hover:bg-transparent flex items-center justify-center transition-all pointer-events-none">
            <div class="w-10 h-10 rounded-full bg-white/90 text-heading flex items-center justify-center shadow-md group-hover:scale-105 transition-transform">
              <svg class="w-4 h-4 ml-0.5 fill-current" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
            </div>
          </div>
          <div class="absolute top-2 right-2 px-2 py-0.5 rounded-full badge-peach text-[10px] font-semibold">
            ${vid.size_mb || 0.8}MB
          </div>
        </div>

        <div class="p-3.5 flex flex-col justify-between flex-grow">
          <div>
            <h4 class="text-xs font-bold text-heading truncate mb-1" title="${vid.title}">${vid.title}</h4>
            <p class="text-[11px] text-muted line-clamp-1 mb-3">
              ${vid.script_preview || "Precision 9:16 vertical animation."}
            </p>
          </div>

          <div class="flex items-center gap-2 pt-2 border-t border-border">
            <button type="button" class="btn-reel-play btn-orange flex-1 py-1.5 text-xs text-center">
              Watch
            </button>
            <a href="${vid.download_url}" download class="btn-secondary p-1.5" title="Download MP4">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            </a>
          </div>
        </div>
      `;

      // Hover-to-play functionality on video thumbnail
      const thumbnailEl = card.querySelector(".example-thumbnail");
      const videoEl = card.querySelector("video");

      thumbnailEl.addEventListener("mouseenter", () => {
        videoEl.play().catch(() => {});
      });

      thumbnailEl.addEventListener("mouseleave", () => {
        videoEl.pause();
        videoEl.currentTime = 0;
      });

      // Click to open focus modal player
      const triggerPlay = () => openModalPlayer(vid.title, vid.url, vid.download_url);
      card.querySelector(".btn-reel-play").addEventListener("click", triggerPlay);
      thumbnailEl.addEventListener("click", triggerPlay);

      videoReel.appendChild(card);
    });

    // Update button states
    if (btnReelPrev) {
      btnReelPrev.disabled = reelScrollIndex === 0;
      btnReelPrev.classList.toggle("opacity-40", reelScrollIndex === 0);
    }
    if (btnReelNext) {
      const hasMore = reelScrollIndex + 4 < allLoadedVideos.length;
      btnReelNext.disabled = !hasMore;
      btnReelNext.classList.toggle("opacity-40", !hasMore);
    }
  }

  // 7. Focus Video Player Modal
  function openModalPlayer(title, videoUrl, downloadUrl) {
    modalVideoTitle.textContent = title;
    modalPlayerSource.src = videoUrl;
    modalDownloadBtn.href = downloadUrl;
    modalPlayer.load();
    modalVideo.classList.remove("hidden");
    modalPlayer.play().catch(() => {});
  }

  function closeModalPlayer() {
    modalPlayer.pause();
    modalVideo.classList.add("hidden");
  }

  modalVideoClose.addEventListener("click", closeModalPlayer);
  modalVideo.addEventListener("click", (e) => {
    if (e.target === modalVideo) closeModalPlayer();
  });

  // 8. System Diagnostics Modal
  async function checkSystemHealth() {
    try {
      const res = await fetch("/api/health");
      if (!res.ok) return;
      const data = await res.json();
      diagnosticStatusText.textContent = data.ok ? "Engine Ready" : "Online";
    } catch {
      diagnosticStatusText.textContent = "Online";
    }
  }

  async function loadModels() {
    try {
      const res = await fetch("/api/models");
      if (!res.ok) return;
      const data = await res.json();
      if (data.models && data.models.length > 0) {
        // Update both desktop and mobile selectors
        [modelSelect, modelSelectMobile].forEach((sel) => {
          if (!sel) return;
          sel.innerHTML = "";
          data.models.forEach((m) => {
            const opt = document.createElement("option");
            opt.value = m;
            opt.textContent = m;
            if (m === data.default) opt.selected = true;
            sel.appendChild(opt);
          });
        });
      }
    } catch (err) {
      console.warn("Using default model options:", err);
    }
  }

  btnDiagnosticOpen.addEventListener("click", () => {
    fetchDiagnosticReport();
    modalDiagnostic.classList.remove("hidden");
  });

  modalDiagnosticClose.addEventListener("click", () => {
    modalDiagnostic.classList.add("hidden");
  });

  modalDiagnosticRefresh.addEventListener("click", fetchDiagnosticReport);

  async function fetchDiagnosticReport() {
    diagnosticLines.innerHTML = `<div class="p-2 text-muted">Checking engines...</div>`;
    try {
      const res = await fetch("/api/health");
      const data = await res.json();
      diagnosticLines.innerHTML = "";

      if (data.diagnostics && data.diagnostics.length > 0) {
        data.diagnostics.forEach((msg) => {
          const line = document.createElement("div");
          line.className = "p-1.5 rounded bg-soft text-heading border border-border";
          line.textContent = msg;
          diagnosticLines.appendChild(line);
        });
      }

      const summary = document.createElement("div");
      summary.className = data.ok ? "p-1.5 text-emerald-600 font-semibold" : "p-1.5 text-orange font-semibold";
      summary.textContent = data.ok ? "All engine subsystems operational." : "Running with fallback safeguards.";
      diagnosticLines.appendChild(summary);
    } catch (err) {
      diagnosticLines.innerHTML = `<div class="p-2 text-red-500">Diagnostics error: ${err.message}</div>`;
    }
  }

  // 9. Mobile Menu
  function openMobileMenu() {
    mobileMenuOverlay.classList.remove("hidden");
    requestAnimationFrame(() => {
      mobileMenuOverlay.classList.remove("opacity-0");
      mobileMenuDrawer.classList.remove("translate-x-full");
    });
  }

  function closeMobileMenu() {
    mobileMenuOverlay.classList.add("opacity-0");
    mobileMenuDrawer.classList.add("translate-x-full");
    setTimeout(() => {
      mobileMenuOverlay.classList.add("hidden");
    }, 300);
  }

  if (btnMobileMenu) btnMobileMenu.addEventListener("click", openMobileMenu);
  if (btnMobileMenuClose) btnMobileMenuClose.addEventListener("click", closeMobileMenu);
  if (mobileMenuOverlay) mobileMenuOverlay.addEventListener("click", closeMobileMenu);

  // Close mobile menu when a nav link is clicked
  document.querySelectorAll(".mobile-nav-link").forEach((link) => {
    link.addEventListener("click", closeMobileMenu);
  });

  // 10. Hero Video Fallback
  function setupHeroVideoFallback() {
    const heroVideo = document.getElementById("hero-sample-video");
    const fallback = document.getElementById("hero-video-fallback");
    if (!heroVideo || !fallback) return;

    heroVideo.addEventListener("error", () => {
      fallback.classList.remove("hidden");
    });

    // Also check if the video has no valid source after a short delay
    setTimeout(() => {
      if (heroVideo.networkState === HTMLMediaElement.NETWORK_NO_SOURCE || heroVideo.error) {
        fallback.classList.remove("hidden");
      }
    }, 2000);
  }

  // 11. Global Keyboard Shortcuts
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeModalPlayer();
      modalDiagnostic.classList.add("hidden");
      closeMobileMenu();
    }
  });
});
