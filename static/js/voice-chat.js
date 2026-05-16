/**
 * Live voice chat: AI coach TTS + continuous browser speech recognition.
 */
(function (global) {
    const SpeechRecognition =
        global.SpeechRecognition || global.webkitSpeechRecognition;

    function LiveVoiceChat(options) {
        this.questionText = options.questionText || "";
        this.transcriptEl = options.transcriptEl;
        this.statusEl = options.statusEl;
        this.coachEl = options.coachEl;
        this.onFinalTranscript = options.onFinalTranscript || function () {};
        this.lang = options.lang || "en-US";
        this.useGemini = !!options.useGemini;
        this.coachSpeakUrl = options.coachSpeakUrl || "/api/coach-speak";
        this._audio = null;
        this.finalText = "";
        this.interimText = "";
        this.listening = false;
        this.liveMode = false;
        this.rec = null;
        if (SpeechRecognition) {
            this.rec = new SpeechRecognition();
            this.rec.continuous = true;
            this.rec.interimResults = true;
            this.rec.lang = this.lang;
            this._bindRecognition();
        }
    }

    LiveVoiceChat.prototype.setStatus = function (text, state) {
        if (this.statusEl) this.statusEl.textContent = text;
        if (this.coachEl) {
            this.coachEl.dataset.state = state || "";
        }
    };

    LiveVoiceChat.prototype._bindRecognition = function () {
        const self = this;
        this.rec.onresult = function (e) {
            let interim = "";
            let finalChunk = "";
            for (let i = e.resultIndex; i < e.results.length; i++) {
                const bit = e.results[i][0].transcript;
                if (e.results[i].isFinal) finalChunk += bit;
                else interim += bit;
            }
            if (finalChunk) {
                self.finalText = (self.finalText + " " + finalChunk).trim();
                self.onFinalTranscript(self.finalText);
            }
            self.interimText = interim;
            self._renderTranscript();
            self._checkVoiceCommands((self.finalText + " " + interim).trim().toLowerCase());
        };
        this.rec.onerror = function (e) {
            if (e.error === "no-speech" || e.error === "aborted") return;
            self.setStatus("Mic error: " + e.error, "error");
        };
        this.rec.onend = function () {
            self.listening = false;
            if (self.liveMode) {
                try {
                    self.rec.start();
                    self.listening = true;
                } catch (err) {
                    /* ignore restart race */
                }
            } else {
                self.setStatus("Mic paused", "idle");
            }
        };
    };

    LiveVoiceChat.prototype._renderTranscript = function () {
        if (!this.transcriptEl) return;
        const show = (this.finalText + (this.interimText ? " " + this.interimText : "")).trim();
        this.transcriptEl.value = show;
    };

    LiveVoiceChat.prototype._checkVoiceCommands = function (lower) {
        if (!lower) return;
        if (/\b(submit answer|submit my answer)\b/.test(lower)) {
            const btn = document.querySelector('[data-voice-cmd="submit"]');
            if (btn) btn.click();
        } else if (/\b(next question|go next)\b/.test(lower)) {
            const btn = document.querySelector('[data-voice-cmd="next"]');
            if (btn) btn.click();
        }
    };

    LiveVoiceChat.prototype._stopAudio = function () {
        if (this._audio) {
            this._audio.pause();
            this._audio = null;
        }
        if (global.speechSynthesis) global.speechSynthesis.cancel();
    };

    LiveVoiceChat.prototype._speakBrowser = function (text, onDone) {
        const self = this;
        if (!global.speechSynthesis) {
            self.setStatus("Voice output not supported in this browser", "error");
            if (onDone) onDone();
            return;
        }
        const utter = new SpeechSynthesisUtterance(text);
        utter.lang = this.lang;
        utter.rate = 0.95;
        utter.pitch = 1;
        self.setStatus("Coach is speaking…", "speaking");
        utter.onend = function () {
            self.setStatus("Your turn — speak now", "listening");
            if (onDone) onDone();
        };
        utter.onerror = function () {
            self.setStatus("Could not play voice — read the question", "error");
            if (onDone) onDone();
        };
        global.speechSynthesis.speak(utter);
    };

    LiveVoiceChat.prototype._speakGemini = function (question, onDone) {
        const self = this;
        self.setStatus("Generating natural voice…", "speaking");
        fetch(self.coachSpeakUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: question }),
            credentials: "same-origin",
        })
            .then(function (res) {
                if (!res.ok) {
                    return res.json().then(function (j) {
                        throw new Error(j.error || "TTS unavailable");
                    }).catch(function () {
                        throw new Error("TTS unavailable (" + res.status + ")");
                    });
                }
                return res.blob();
            })
            .then(function (blob) {
                const url = URL.createObjectURL(blob);
                self._audio = new Audio(url);
                self.setStatus("Coach is speaking…", "speaking");
                self._audio.onended = function () {
                    URL.revokeObjectURL(url);
                    self._audio = null;
                    self.setStatus("Your turn — speak now", "listening");
                    if (onDone) onDone();
                };
                self._audio.onerror = function () {
                    URL.revokeObjectURL(url);
                    self._speakBrowser(
                        "Here is your interview question. " + question,
                        onDone
                    );
                };
                return self._audio.play();
            })
            .catch(function (err) {
                self.setStatus(
                    (err && err.message) ? String(err.message).slice(0, 60) : "Using browser voice…",
                    "error"
                );
                self._speakBrowser(
                    "Here is your interview question. " + question,
                    onDone
                );
            });
    };

    LiveVoiceChat.prototype.speak = function (text, onDone) {
        this._stopAudio();
        if (this.useGemini && this.questionText) {
            this._speakGemini(this.questionText, onDone);
            return;
        }
        this._speakBrowser(text, onDone);
    };

    LiveVoiceChat.prototype.speakQuestion = function (onDone) {
        const q = this.questionText || "";
        if (this.useGemini && q) {
            this._speakGemini(q, onDone);
            return;
        }
        this.speak("Here is your interview question. " + q, onDone);
    };

    LiveVoiceChat.prototype.startLive = function () {
        if (!this.rec) {
            this.setStatus("Speech recognition not supported — use Chrome or Edge", "error");
            return;
        }
        this.liveMode = true;
        this.finalText = "";
        this.interimText = "";
        this._renderTranscript();
        try {
            this.rec.start();
            this.listening = true;
            this.setStatus("Listening…", "listening");
        } catch (e) {
            this.setStatus("Click the mic to allow access", "idle");
        }
    };

    LiveVoiceChat.prototype.stopLive = function () {
        this.liveMode = false;
        if (this.rec && this.listening) {
            try {
                this.rec.stop();
            } catch (e) {
                /* ignore */
            }
        }
        this.listening = false;
        this.setStatus("Mic paused", "idle");
    };

    LiveVoiceChat.prototype.toggleLive = function () {
        if (this.liveMode) this.stopLive();
        else this.startLive();
    };

    LiveVoiceChat.prototype.resetTranscript = function () {
        this.finalText = "";
        this.interimText = "";
        this._renderTranscript();
    };

    LiveVoiceChat.prototype.isSupported = function () {
        return !!(SpeechRecognition && global.speechSynthesis);
    };

    global.LiveVoiceChat = LiveVoiceChat;
})(window);
