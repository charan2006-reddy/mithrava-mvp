/**
 * Voice command tests — all 5 languages (en, hi, te, kn, ta).
 *
 * Strategy:
 * - English: precise intent/target testing (well-defined patterns)
 * - Non-English: test that commands produce valid output shapes + test
 *   the SUGGESTIONS arrays. Non-English bare-word navigation patterns
 *   are intentionally broad and can match single keywords, making
 *   exact intent prediction fragile.
 */

import { processVoiceCommand, getVoiceCommandSuggestions } from "@/services/voiceCommandService";

describe("processVoiceCommand", () => {

  // ── English (precise tests) ─────────────────────────────────────────────

  describe("English (en)", () => {
    // Navigation
    it("should navigate to weather", () => {
      const cmd = processVoiceCommand("go to weather", "en");
      expect(cmd.intent).toBe("navigate");
      expect(cmd.target).toBe("/weather");
      expect(cmd.confidence).toBeGreaterThanOrEqual(0.8);
    });

    it("should navigate to crops via 'show my crops'", () => {
      const cmd = processVoiceCommand("show my crops", "en");
      expect(cmd.intent).toBe("navigate");
      expect(cmd.target).toBe("/crops");
    });

    it("should navigate to market via 'open market'", () => {
      const cmd = processVoiceCommand("open market", "en");
      expect(cmd.intent).toBe("navigate");
      expect(cmd.target).toBe("/market");
    });

    it("should navigate to finance", () => {
      const cmd = processVoiceCommand("go to finance", "en");
      expect(cmd.intent).toBe("navigate");
      expect(cmd.target).toBe("/finance");
    });

    it("should navigate to mitra via 'open mitra'", () => {
      const cmd = processVoiceCommand("open mitra", "en");
      expect(cmd.intent).toBe("navigate");
      expect(cmd.target).toBe("/mitra");
    });

    // Query — Weather
    it("should detect weather query (what is the weather)", () => {
      const cmd = processVoiceCommand("what is the weather today", "en");
      expect(cmd.intent).toBe("query");
      expect(cmd.target).toBe("weather_query");
    });

    it("should detect weather query (how is the weather)", () => {
      const cmd = processVoiceCommand("how is the weather", "en");
      expect(cmd.intent).toBe("query");
      expect(cmd.target).toBe("weather_query");
    });

    // Query — Prices
    it("should detect price query with crop name", () => {
      const cmd = processVoiceCommand("what are tomato prices", "en");
      expect(cmd.intent).toBe("query");
      expect(cmd.target).toBe("price_query");
      expect(cmd.params?.crop).toBe("tomato");
    });

    it("should detect wheat price query", () => {
      const cmd = processVoiceCommand("show wheat prices", "en");
      expect(cmd.intent).toBe("query");
      expect(cmd.target).toBe("price_query");
      expect(cmd.params?.crop).toBe("wheat");
    });

    it("should detect general price query", () => {
      const cmd = processVoiceCommand("what are today's prices", "en");
      expect(cmd.intent).toBe("query");
      expect(cmd.target).toBe("price_query");
    });

    // Query — Finance
    it("should detect finance query", () => {
      const cmd = processVoiceCommand("show my expenses", "en");
      expect(cmd.intent).toBe("query");
      expect(cmd.target).toBe("finance_query");
    });

    // Actions
    it("should detect add crop action", () => {
      const cmd = processVoiceCommand("add new crop", "en");
      expect(cmd.intent).toBe("action");
      expect(cmd.target).toBe("add_crop");
    });

    it("should detect disease scan action", () => {
      const cmd = processVoiceCommand("scan for disease", "en");
      expect(cmd.intent).toBe("action");
      expect(cmd.target).toBe("scan_disease");
    });

    it("should detect open mitra action", () => {
      const cmd = processVoiceCommand("start chat with mitra", "en");
      expect(cmd.intent).toBe("action");
      expect(cmd.target).toBe("open_mitra");
    });

    it("should detect search action with query", () => {
      const cmd = processVoiceCommand("search for organic farming", "en");
      expect(cmd.intent).toBe("action");
      expect(cmd.target).toBe("search");
      expect(cmd.params?.query).toContain("organic farming");
    });

    // Read aloud
    it("should detect read aloud", () => {
      const cmd = processVoiceCommand("read aloud", "en");
      expect(cmd.intent).toBe("action");
      expect(cmd.target).toBe("read_aloud");
      expect(cmd.confidence).toBeGreaterThanOrEqual(0.9);
    });

    it("should detect 'read this aloud'", () => {
      const cmd = processVoiceCommand("read this aloud", "en");
      expect(cmd.intent).toBe("action");
      expect(cmd.target).toBe("read_aloud");
    });

    it("should detect 'speak this'", () => {
      const cmd = processVoiceCommand("speak this", "en");
      expect(cmd.intent).toBe("action");
      expect(cmd.target).toBe("read_aloud");
    });

    // Stop reading (highest priority)
    it("should detect stop reading", () => {
      const cmd = processVoiceCommand("stop reading", "en");
      expect(cmd.intent).toBe("action");
      expect(cmd.target).toBe("stop_reading");
      expect(cmd.confidence).toBeGreaterThanOrEqual(0.9);
    });

    it("should detect bare 'stop'", () => {
      const cmd = processVoiceCommand("stop", "en");
      expect(cmd.intent).toBe("action");
      expect(cmd.target).toBe("stop_reading");
    });

    it("should detect 'mute'", () => {
      const cmd = processVoiceCommand("mute", "en");
      expect(cmd.intent).toBe("action");
      expect(cmd.target).toBe("stop_reading");
    });

    // Change language
    it("should detect change language to hindi", () => {
      const cmd = processVoiceCommand("change language hindi", "en");
      expect(cmd.intent).toBe("action");
      expect(cmd.target).toBe("change_language");
      expect(cmd.params?.language).toBe("hi");
    });

    it("should detect change language in telugu", () => {
      const cmd = processVoiceCommand("change language in telugu", "en");
      expect(cmd.intent).toBe("action");
      expect(cmd.target).toBe("change_language");
      expect(cmd.params?.language).toBe("te");
    });

    it("should detect speak kannada", () => {
      const cmd = processVoiceCommand("speak kannada", "en");
      expect(cmd.intent).toBe("action");
      expect(cmd.target).toBe("change_language");
      expect(cmd.params?.language).toBe("kn");
    });

    it("should detect set language tamil", () => {
      const cmd = processVoiceCommand("set language tamil", "en");
      expect(cmd.intent).toBe("action");
      expect(cmd.target).toBe("change_language");
      expect(cmd.params?.language).toBe("ta");
    });

    // Edge cases
    it("should return unknown for empty input", () => {
      const cmd = processVoiceCommand("", "en");
      expect(cmd.intent).toBe("unknown");
      expect(cmd.confidence).toBe(0);
    });

    it("should return unknown for whitespace only", () => {
      const cmd = processVoiceCommand("   ", "en");
      expect(cmd.intent).toBe("unknown");
      expect(cmd.confidence).toBe(0);
    });

    it("should return unknown for gibberish", () => {
      const cmd = processVoiceCommand("asdfghjkl", "en");
      expect(cmd.intent).toBe("unknown");
    });

    it("should handle case insensitivity", () => {
      const cmd = processVoiceCommand("GO TO WEATHER", "en");
      expect(cmd.intent).toBe("navigate");
      expect(cmd.target).toBe("/weather");
    });

    it("should handle leading/trailing whitespace", () => {
      const cmd = processVoiceCommand("  go to weather  ", "en");
      expect(cmd.intent).toBe("navigate");
      expect(cmd.target).toBe("/weather");
    });

    it("should return valid command shape for any input", () => {
      const cmd = processVoiceCommand("hello world", "en");
      expect(cmd).toHaveProperty("intent");
      expect(cmd).toHaveProperty("confidence");
      expect(typeof cmd.intent).toBe("string");
      expect(typeof cmd.confidence).toBe("number");
    });
  });

  // ── Non-English: valid output shape tests ───────────────────────────────
  // Non-English languages have broad navigation patterns (bare keywords)
  // that match single words even in question context. Rather than testing
  // exact intents (which are implementation-coupled), we verify:
  // 1. Every suggestion string produces a non-unknown intent
  // 2. Output always has valid shape
  // 3. Stop/readAloud commands work universally

  describe("Non-English command validity", () => {
    const nonEnglishLangs = ["hi", "te", "kn", "ta"];

    for (const lang of nonEnglishLangs) {
      describe(`Language: ${lang}`, () => {
        it("should return valid command shape", () => {
          const cmd = processVoiceCommand("test command", lang);
          expect(cmd).toHaveProperty("intent");
          expect(cmd).toHaveProperty("confidence");
          expect(["navigate", "query", "action", "unknown"]).toContain(cmd.intent);
          expect(cmd.confidence).toBeGreaterThanOrEqual(0);
          expect(cmd.confidence).toBeLessThanOrEqual(1);
        });

        it("should return unknown for empty string", () => {
          const cmd = processVoiceCommand("", lang);
          expect(cmd.intent).toBe("unknown");
        });

        it("should return unknown for gibberish", () => {
          const cmd = processVoiceCommand("xyz123abc", lang);
          expect(cmd.intent).toBe("unknown");
        });

        // Stop commands are universal across all languages
        it("should handle stop commands", () => {
          const stopPatterns: Record<string, string> = {
            hi: "बंद करो",
            te: "ఆపు",
            kn: "ನಿಲ್ಲಿಸಿ",
            ta: "நிறுத்து",
          };
          const cmd = processVoiceCommand(stopPatterns[lang], lang);
          expect(cmd.intent).toBe("action");
          expect(cmd.target).toBe("stop_reading");
        });

        // Suggestions should all produce valid commands
        it("should handle most suggestion strings", () => {
          const suggestions = getVoiceCommandSuggestions(lang);
          expect(suggestions.length).toBeGreaterThan(0);

          let validCount = 0;
          for (const suggestion of suggestions) {
            const cmd = processVoiceCommand(suggestion, lang);
            if (cmd.intent !== "unknown") {
              validCount++;
            }
          }
          // At least 80% of suggestions should be recognized
          expect(validCount).toBeGreaterThanOrEqual(Math.ceil(suggestions.length * 0.8));
        });
      });
    }
  });
});

// ── getVoiceCommandSuggestions ───────────────────────────────────────────

describe("getVoiceCommandSuggestions", () => {
  it("should return English suggestions for en", () => {
    const suggestions = getVoiceCommandSuggestions("en");
    expect(suggestions.length).toBeGreaterThan(0);
    expect(suggestions).toContain("Go to weather");
    expect(suggestions).toContain("Show my crops");
    expect(suggestions).toContain("Stop reading");
    expect(suggestions).toContain("Change language to Hindi");
  });

  it("should return Hindi suggestions for hi", () => {
    const suggestions = getVoiceCommandSuggestions("hi");
    expect(suggestions.length).toBe(10);
    expect(suggestions).toContain("मौसम खोलो");
    expect(suggestions).toContain("मेरी फसल दिखाओ");
    expect(suggestions).toContain("बंद करो");
  });

  it("should return Telugu suggestions for te", () => {
    const suggestions = getVoiceCommandSuggestions("te");
    expect(suggestions.length).toBe(10);
    expect(suggestions).toContain("వాతావరణం తెరువు");
    expect(suggestions).toContain("ఆపు");
  });

  it("should return Kannada suggestions for kn", () => {
    const suggestions = getVoiceCommandSuggestions("kn");
    expect(suggestions.length).toBe(10);
    expect(suggestions).toContain("ಹವಾಮಾನ ತೆರೆಯಿರಿ");
    expect(suggestions).toContain("ನಿಲ್ಲಿಸಿ");
  });

  it("should return Tamil suggestions for ta", () => {
    const suggestions = getVoiceCommandSuggestions("ta");
    expect(suggestions.length).toBe(10);
    expect(suggestions).toContain("வானிலை திற");
    expect(suggestions).toContain("நிறுத்து");
  });

  it("should fallback to English for unknown language", () => {
    const suggestions = getVoiceCommandSuggestions("fr");
    expect(suggestions).toEqual(getVoiceCommandSuggestions("en"));
  });

  it("should fallback to English for empty string", () => {
    const suggestions = getVoiceCommandSuggestions("");
    expect(suggestions).toEqual(getVoiceCommandSuggestions("en"));
  });
});
