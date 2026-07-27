import type { VoiceCommand } from "@/stores/voiceStore";

// ─── Navigation page mapping ──────────────────────────────────────────────────

const PAGE_MAP: Record<string, string> = {
  // English
  home: "/",
  crops: "/crops",
  mycrops: "/crops",
  "my crops": "/crops",
  weather: "/weather",
  market: "/market",
  "market prices": "/market",
  finance: "/finance",
  diseases: "/diseases",
  disease: "/diseases",
  "disease detection": "/diseases",
  knowledge: "/knowledge",
  forum: "/forum",
  community: "/forum",
  support: "/support",
  "expert support": "/support",
  profile: "/profile",
  admin: "/admin",
  notifications: "/notifications",
  mitra: "/mitra",
  chat: "/mitra",
  vendors: "/vendors",
  more: "/more",
  "add crop": "/crops/add",
  "add new crop": "/crops/add",
};

// ─── Multilingual command patterns ────────────────────────────────────────────

interface LanguagePatterns {
  navigation: RegExp[];
  query: RegExp[];
  action: RegExp[];
  readAloud: RegExp[];
  stopReading: RegExp[];
  changeLanguage: RegExp[];
}

const LANGUAGE_PATTERNS: Record<string, LanguagePatterns> = {
  en: {
    navigation: [
      /(?:go\s+to|open|show|navigate\s+to|take\s+me\s+to|display)\s+(.+)/i,
    ],
    query: [
      /(?:what(?:'s| is)\s+(?:the\s+)?(?:weather|forecast)|how(?:'s| is)\s+(?:the\s+)?weather)/i,
      /(?:show|what\s+are|what(?:'s| is))\s+(?:my\s+)?(?:crop|crops)/i,
      /(?:what\s+are|show|check)\s+(?:tomato|wheat|rice|cotton|onion|potato|chilli|maize|groundnut|soybean|sugarcane)\s+prices?/i,
      /(?:show|what\s+are)\s+(?:today'?s?\s+)?(?:market\s+)?prices?/i,
      /(?:show|what\s+are|check)\s+(?:my\s+)?(?:expenses|finance|spending)/i,
    ],
    action: [
      /(?:add|create|new)\s+(?:a\s+)?(?:new\s+)?crop/i,
      /(?:scan|detect|check)\s+(?:for\s+)?(?:a\s+)?disease/i,
      /(?:start|open)\s+(?:a\s+)?chat\s+(?:with\s+)?mitra/i,
      /(?:search|look\s+up|find)\s+(?:for\s+)?(.+)/i,
    ],
    readAloud: [
      /(?:read|speak|tell\s+me|say)\s+(?:this|aloud|out\s+loud|the\s+summary)/i,
      /read\s+aloud/i,
    ],
    stopReading: [
      /(?:stop|pause|quiet|silence|mute|cancel)\s*(?:reading|speaking|tts|talking)?/i,
    ],
    changeLanguage: [
      /(?:speak|talk|change\s+(?:language|lang)|set\s+language)\s+(?:in\s+)?(?:hindi|telugu|kannada|tamil|english)/i,
    ],
  },
  hi: {
    navigation: [
      /(?:जाओ|खोलो|दिखाओ|ले चलो|नेविगेट)\s+(.+)/i,
      /(मौसम|बाज़ार|फसल|होम|प्रोफ़ाइल|सहायता|मंच|वित्त|रोग|ज्ञान|विक्रेता|मित्र)/i,
    ],
    query: [
      /(?:मौसम\s+(?:कैसा|क्या|बताओ)|आज\s+मौसम)/i,
      /(?:मेरी|दिखाओ)\s+फसल/i,
      /(?:टमाटर|गेहूँ|चावल|कपास|प्याज|आलू|मिर्च|मक्का)\s+(?:का\s+)?(?:भाव|दाम|मूल्य)/i,
      /(?:बाज़ार\s+)?(?:भाव|दाम|मूल्य)\s+(?:दिखाओ|बताओ|क्या)/i,
    ],
    action: [
      /(?:नई|नया)\s+फसल\s+(?:जोड़ो|add|बनाओ)/i,
      /(?:रोग\s+)?(?:स्कैन|जाँच|पहचान)/i,
      /मित्र\s+(?:से\s+)?(?:बात|chat)/i,
    ],
    readAloud: [
      /(?:पढ़ो|बोलो|सुनाओ|पढ़कर\s+सुनाओ)/i,
    ],
    stopReading: [
      /(?:बंद|रोको|चुप|म्यूट)\s*(?:करो|बात)?/i,
    ],
    changeLanguage: [
      /(?:बोलो|भाषा)\s+(?:हिंदी|तेलुगु|कन्नड़|तमिल|अंग्रेज़ी)/i,
    ],
  },
  te: {
    navigation: [
      /(?:వెళ్ళు|తెరువు|చూపించు|నావిగేట్)\s+(.+)/i,
      /(?:వాతావరణం|మార్కెట్|పంటలు|హోమ్|ప్రొఫైల్|మద్దతు|ఫోరం|ఆర్థిక|వ్యాధి|మిత్ర|విక్రేతలు)/i,
    ],
    query: [
      /(?:వాతావరణం|వాతావరణ)\s+(?:ఎలా|ఏమిటి|చెప్పు)/i,
      /(?:నా)\s+పంటలు/i,
      /(?:టమాటా|గోధుమ|బియ్యం|పత్తి|ఉల్లి|బంగాళాదుంప|మిర్చి|మొక్కజొన్న)\s+ధరలు/i,
    ],
    action: [
      /(?:కొత్త)\s+పంట\s+జోడించు/i,
      /(?:వ్యాధి)\s+స్కాన్/i,
      /మిత్రతో\s+చాట్/i,
    ],
    readAloud: [
      /(?:చదువు|మాట్లాడు|చెప్పు)\s*(?:చూపించు|అన్ని)?/i,
    ],
    stopReading: [
      /(?:ఆపు|మూసి|నిశ్శబ్దం)\s*(?:మాట్లాడటం|చదవడం)?/i,
    ],
    changeLanguage: [
      /(?:మాట్లాడు|భాష)\s+(?:తెలుగు|హిందీ|కన్నడ|తమిళం|ఆంగ్లం)/i,
    ],
  },
  kn: {
    navigation: [
      /(?:ಹೋಗಿ|ತೆರೆಯಿರಿ|ತೋರಿಸಿ|ನಾವಿಗೇಟ್)\s+(.+)/i,
      /(?:ಹವಾಮಾನ|ಮಾರುಕಟ್ಟೆ|ಬೆಳೆಗಳು|ಹೋಮ್|ಪ್ರೊಫೈಲ್|ಬೆಂಬಲ|ವೇದಿಕೆ|ಹಣಕಾಸು|ರೋಗ|ಮಿತ್ರ|ಮಾರಾಟಗಾರರು)/i,
    ],
    query: [
      /(?:ಹವಾಮಾನ)\s+(?:ಹೇಗೆ|ಏನು|ಹೇಳಿ)/i,
      /(?:ನನ್ನ)\s+ಬೆಳೆಗಳು/i,
      /(?:ಟೊಮೇಟೊ|ಗೋಧಿ|ಅಕ್ಕಿ|ಹತ್ತಿ|ಈರುಳ್ಳಿ|ಆಲೂಗಡ್ಡೆ|ಮೆಣಸು|ಜೋಳ)\s+ಬೆಲೆಗಳು/i,
    ],
    action: [
      /(?:ಹೊಸ)\s+ಬೆಳೆ\s+ಸೇರಿಸಿ/i,
      /(?:ರೋಗ)\s+ಸ್ಕ್ಯಾನ್/i,
      /ಮಿತ್ರನೊಂದಿಗೆ\s+ಚಾಟ್/i,
    ],
    readAloud: [
      /(?:ಓದಿ|ಮಾತನಾಡಿ|ಹೇಳಿ)/i,
    ],
    stopReading: [
      /(?:ನಿಲ್ಲಿಸಿ|ಮುಚ್ಚಿ|ಮೌನ)\s*(?:ಮಾತನಾಡುವುದು|ಓದುವುದು)?/i,
    ],
    changeLanguage: [
      /(?:ಮಾತನಾಡಿ|ಭಾಷೆ)\s+(?:ಕನ್ನಡ|ಹಿಂದಿ|ತೆಲುಗು|ತಮಿಳು|ಇಂಗ್ಲಿಷ್)/i,
    ],
  },
  ta: {
    navigation: [
      /(?:செல்|திற|காட்டு|நாவிகேட்)\s+(.+)/i,
      /(?:வானிலை|சந்தை|பயிர்கள்|முகப்பு|சுயவிவரம்|ஆதரவு|மன்றம்|நிதி|நோய்|மித்ரா|விற்பனையாளர்கள்)/i,
    ],
    query: [
      /(?:வானிலை)\s+(?:எப்படி|என்ன|சொல்)/i,
      /(?:என்)\s+பயிர்கள்/i,
      /(?:தக்காளி|கோதுமை|அரிசி|பருத்தி|வெங்காயம்|உருளைக்கிழங்கு|மிளகாய்|சோளம்)\s+விலைகள்/i,
    ],
    action: [
      /(?:புதிய)\s+பயிர்\s+சேர்/i,
      /(?:நோய்)\s+ஸ்கேன்/i,
      /மித்ராவுடன்\s+அரட்டை/i,
    ],
    readAloud: [
      /(?:படியும்|பேசும்|சொல்)/i,
    ],
    stopReading: [
      /(?:நிறுத்து|மூடு|அமைதி)\s*(?:பேசுதல்|படித்தல்)?/i,
    ],
    changeLanguage: [
      /(?:பேசு|மொழி)\s+(?:தமிழ்|ஹிந்தி|தெலுங்கு|கன்னடம்|ஆங்கிலம்)/i,
    ],
  },
};

// ─── Language code aliases ────────────────────────────────────────────────────

const LANG_ALIASES: Record<string, string> = {
  hindi: "hi",
  telugu: "te",
  kannada: "kn",
  tamil: "ta",
  english: "en",
  "हिंदी": "hi",
  "तेलुगु": "te",
  "తెలుగు": "te",
  "ಕನ್ನಡ": "kn",
  "तमिऴ்": "ta",
  "தமிழ்": "ta",
  "अंग्रेज़ी": "en",
  "ఆంగ్లం": "en",
  "ಇಂಗ್ಲಿಷ್": "en",
  "ஆங்கிலம்": "en",
};

// ─── Page name aliases per language ───────────────────────────────────────────

const PAGE_ALIASES: Record<string, Record<string, string>> = {
  hi: {
    "होम": "home",
    "घर": "home",
    "फसल": "crops",
    "फसलें": "crops",
    "मौसम": "weather",
    "बाज़ार": "market",
    "बाजार": "market",
    "वित्त": "finance",
    "रोग": "diseases",
    "ज्ञान": "knowledge",
    "मंच": "forum",
    "सहायता": "support",
    "प्रोफ़ाइल": "profile",
    "प्रशासन": "admin",
    "विक्रेता": "vendors",
    "मित्र": "mitra",
  },
  te: {
    "వాతావరణం": "weather",
    "మార్కెట్": "market",
    "పంటలు": "crops",
    "హోమ్": "home",
    "ప్రొఫైల్": "profile",
    "మద్దతు": "support",
    "ఫోరం": "forum",
    "ఆర్థిక": "finance",
    "వ్యాధి": "diseases",
    "మిత్ర": "mitra",
    "విక్రేతలు": "vendors",
  },
  kn: {
    "ಹವಾಮಾನ": "weather",
    "ಮಾರುಕಟ್ಟೆ": "market",
    "ಬೆಳೆಗಳು": "crops",
    "ಹೋಮ್": "home",
    "ಪ್ರೊಫೈಲ್": "profile",
    "ಬೆಂಬಲ": "support",
    "ವೇದಿಕೆ": "forum",
    "ಹಣಕಾಸು": "finance",
    "ರೋಗ": "diseases",
    "ಮಿತ್ರ": "mitra",
    "ಮಾರಾಟಗಾರರು": "vendors",
  },
  ta: {
    "வானிலை": "weather",
    "சந்தை": "market",
    "பயிர்கள்": "crops",
    "முகப்பு": "home",
    "சுயவிவரம்": "profile",
    "ஆதரவு": "support",
    "மன்றம்": "forum",
    "நிதி": "finance",
    "நோய்": "diseases",
    "மித்ரா": "mitra",
    "விற்பனையாளர்கள்": "vendors",
  },
};

// ─── Suggestion templates per language ────────────────────────────────────────

const SUGGESTIONS: Record<string, string[]> = {
  en: [
    "Go to weather",
    "Show my crops",
    "What are tomato prices?",
    "Open market",
    "Chat with Mitra",
    "Add new crop",
    "Scan for disease",
    "Read this aloud",
    "Stop reading",
    "Change language to Hindi",
  ],
  hi: [
    "मौसम खोलो",
    "मेरी फसल दिखाओ",
    "टमाटर का भाव बताओ",
    "बाज़ार खोलो",
    "मित्र से बात करो",
    "नई फसल जोड़ो",
    "रोग स्कैन करो",
    "पढ़कर सुनाओ",
    "बंद करो",
    "हिंदी में बोलो",
  ],
  te: [
    "వాతావరణం తెరువు",
    "నా పంటలు చూపించు",
    "టమాటా ధరలు చెప్పు",
    "మార్కెట్ తెరువు",
    "మిత్రతో చాట్",
    "కొత్త పంట జోడించు",
    "వ్యాధి స్కాన్",
    "చదువు చూపించు",
    "ఆపు",
    "తెలుగులో మాట్లాడు",
  ],
  kn: [
    "ಹವಾಮಾನ ತೆರೆಯಿರಿ",
    "ನನ್ನ ಬೆಳೆಗಳು ತೋರಿಸಿ",
    "ಟೊಮೇಟೊ ಬೆಲೆ ಹೇಳಿ",
    "ಮಾರುಕಟ್ಟೆ ತೆರೆಯಿರಿ",
    "ಮಿತ್ರನೊಂದಿಗೆ ಚಾಟ್",
    "ಹೊಸ ಬೆಳೆ ಸೇರಿಸಿ",
    "ರೋಗ ಸ್ಕ್ಯಾನ್",
    "ಓದಿ ಹೇಳಿ",
    "ನಿಲ್ಲಿಸಿ",
    "ಕನ್ನಡದಲ್ಲಿ ಮಾತನಾಡಿ",
  ],
  ta: [
    "வானிலை திற",
    "என் பயிர்கள் காட்டு",
    "தக்காளி விலை சொல்",
    "சந்தை திற",
    "மித்ராவுடன் அரட்டை",
    "புதிய பயிர் சேர்",
    "நோய் ஸ்கேன்",
    "படியும் சொல்",
    "நிறுத்து",
    "தமிழில் பேசு",
  ],
};

// ─── Public API ───────────────────────────────────────────────────────────────

/**
 * Process a voice transcript into a structured VoiceCommand.
 *
 * @param transcript - The raw speech-to-text output from the user
 * @param language   - Current app language code (en, hi, te, kn, ta)
 * @returns A VoiceCommand with intent, target, and confidence
 */
export function processVoiceCommand(
  transcript: string,
  language: string
): VoiceCommand {
  const normalizedTranscript = transcript.trim().toLowerCase();
  if (!normalizedTranscript) {
    return { intent: "unknown", confidence: 0 };
  }

  const patterns = LANGUAGE_PATTERNS[language] || LANGUAGE_PATTERNS.en;
  const pageAliases = PAGE_ALIASES[language] || {};

  // ── 1. Check stop-reading commands (highest priority) ──
  for (const regex of patterns.stopReading) {
    if (regex.test(normalizedTranscript)) {
      return {
        intent: "action",
        target: "stop_reading",
        confidence: 0.95,
      };
    }
  }

  // ── 2. Check read-aloud commands ──
  for (const regex of patterns.readAloud) {
    if (regex.test(normalizedTranscript)) {
      return {
        intent: "action",
        target: "read_aloud",
        confidence: 0.9,
      };
    }
  }

  // ── 3. Check change-language commands ──
  for (const regex of patterns.changeLanguage) {
    const match = normalizedTranscript.match(regex);
    if (match) {
      // Extract the language name from the transcript
      const langWords = [
        "hindi", "telugu", "kannada", "tamil", "english",
        "हिंदी", "तेलुगु", "తెలుగు", "ಕನ್ನಡ", "தமிழ்", "অंग্রেজী",
        "हिंदी", "తెలుగు", "ಕನ್ನಡ", "தமிழ்", "अंग्रेज़ी",
        "आंग्ल", "ఆంగ్లం", "ಇಂಗ್ಲಿಷ್", "ஆங்கிலம்",
      ];
      let detectedLang = "en";
      for (const word of langWords) {
        if (normalizedTranscript.includes(word.toLowerCase())) {
          const alias = LANG_ALIASES[word] || LANG_ALIASES[word.toLowerCase()];
          if (alias) {
            detectedLang = alias;
            break;
          }
        }
      }
      return {
        intent: "action",
        target: "change_language",
        params: { language: detectedLang },
        confidence: 0.9,
      };
    }
  }

  // ── 4. Check navigation commands ──
  for (const regex of patterns.navigation) {
    const match = normalizedTranscript.match(regex);
    if (match) {
      const target = match[1]?.trim().toLowerCase() || "";
      const pageSlug = target.replace(/\s+/g, "").replace(/[^a-z0-9\u0900-\u097f\u0c00-\u0c7f\u0b80-\u0bff]/gi, "");

      // Try direct match in English page map
      let path = PAGE_MAP[target] || PAGE_MAP[pageSlug];

      // Try language-specific aliases
      if (!path) {
        for (const [alias, slug] of Object.entries(pageAliases)) {
          if (target.includes(alias.toLowerCase()) || alias.toLowerCase().includes(target)) {
            path = PAGE_MAP[slug] || `/${slug}`;
            break;
          }
        }
      }

      // Try fuzzy match in page map
      if (!path) {
        for (const [key, val] of Object.entries(PAGE_MAP)) {
          if (target.includes(key) || key.includes(target)) {
            path = val;
            break;
          }
        }
      }

      if (path) {
        return {
          intent: "navigate",
          target: path,
          confidence: 0.85,
        };
      }
    }
  }

  // ── 5. Check query commands ──
  for (const regex of patterns.query) {
    if (regex.test(normalizedTranscript)) {
      let target = "general_query";
      let params: Record<string, string> = {};

      // Weather query
      if (/weather|मौसम|వాతావరణం|ಹವಾಮಾನ|வானிலை/i.test(normalizedTranscript)) {
        target = "weather_query";
      }
      // Crop query
      else if (/crop|fasal|పంట|ಬೆಳೆ|பயிர்/i.test(normalizedTranscript)) {
        target = "crop_query";
      }
      // Price query
      else if (/pric|price|bhav|dam|ధర|ಬೆಲೆ|விலை/i.test(normalizedTranscript)) {
        target = "price_query";
        // Detect crop name in the query
        const cropNames = [
          "tomato", "wheat", "rice", "cotton", "onion", "potato", "chilli", "maize", "groundnut", "soybean",
          "टमाटर", "गेहूँ", "चावल", "कपास", "प्याज", "आलू", "मिर्च", "मक्का",
          "టమాటా", "గోధుమ", "బియ్యం", "పత్తి", "ఉల్లి", "బంగాళాదుంప", "మిర్చి", "మొక్కజొన్న",
          "ಟೊಮೇಟೊ", "ಗೋಧಿ", "ಅಕ್ಕಿ", "ಹತ್ತಿ", "ಈರುಳ್ಳಿ", "ಆಲೂಗಡ್ಡೆ", "ಮೆಣಸು", "ಜೋಳ",
          "தக்காளி", "கோதுமை", "அரிசி", "பருத்தி", "வெங்காயம்", "உருளைக்கிழங்கு", "மிளகாய்", "சோளம்",
        ];
        for (const crop of cropNames) {
          if (normalizedTranscript.includes(crop)) {
            params.crop = crop;
            break;
          }
        }
      }
      // Expense / finance query
      else if (/expense|finance|spend|खर्च|वित्त|ఖర్చు|ಆರ್ಥಿಕ|நிதி|செலவு/i.test(normalizedTranscript)) {
        target = "finance_query";
      }

      return {
        intent: "query",
        target,
        params,
        confidence: 0.8,
      };
    }
  }

  // ── 6. Check action commands ──
  for (const regex of patterns.action) {
    if (regex.test(normalizedTranscript)) {
      let target = "general_action";
      const params: Record<string, string> = {};

      if (/add|create|new|जोड़|జోడించು|ಸೇರಿಸ|சேர்/i.test(normalizedTranscript) && /crop|fasal|పంట|ಬೆಳೆ|பயிர்/i.test(normalizedTranscript)) {
        target = "add_crop";
      }
      else if (/scan|detect|check|स्कैन|జాచు|ಸ್ಕ್ಯಾನ್|ஸ்கேன்/i.test(normalizedTranscript) && /disease|rog|వ్యాధి|ರೋಗ|நோய்/i.test(normalizedTranscript)) {
        target = "scan_disease";
      }
      else if (/chat|mitra|मित्र|మిత్ర|ಮಿತ್ರ|மித்ரா/i.test(normalizedTranscript)) {
        target = "open_mitra";
      }
      else if (/search|look\s+up|find|खोज|शोध|ಹುಡುಕ|தேடு/i.test(normalizedTranscript)) {
        target = "search";
        const searchMatch = normalizedTranscript.match(
          /(?:search|look\s+up|find|खोज|शोध|ಹುಡುಕ|தேடு)\s+(?:for\s+)?(.+)/i
        );
        if (searchMatch?.[1]) {
          params.query = searchMatch[1].trim();
        }
      }

      return {
        intent: "action",
        target,
        params,
        confidence: 0.75,
      };
    }
  }

  // ── 7. No pattern matched — return unknown ──
  return {
    intent: "unknown",
    confidence: 0.2,
  };
}

/**
 * Get voice command suggestions for the given language.
 *
 * @param language - Current language code
 * @returns Array of suggestion strings
 */
export function getVoiceCommandSuggestions(language: string): string[] {
  return SUGGESTIONS[language] || SUGGESTIONS.en;
}

/**
 * Check if Web Speech API is available in the current browser.
 */
export function isSpeechRecognitionSupported(): boolean {
  return (
    typeof window !== "undefined" &&
    ("SpeechRecognition" in window || "webkitSpeechRecognition" in window)
  );
}

/**
 * Get the SpeechRecognition constructor (cross-browser).
 */
export function getSpeechRecognitionConstructor():
  | SpeechRecognitionConstructor
  | null {
  if (typeof window === "undefined") return null;
  if ("SpeechRecognition" in window) {
    return window.SpeechRecognition ?? null;
  }
  if ("webkitSpeechRecognition" in window) {
    return (window.webkitSpeechRecognition as unknown as SpeechRecognitionConstructor) ?? null;
  }
  return null;
}

/**
 * Map language code to BCP-47 speech recognition language tag.
 */
export function getSpeechRecognitionLang(language: string): string {
  const langMap: Record<string, string> = {
    en: "en-IN",
    hi: "hi-IN",
    te: "te-IN",
    kn: "kn-IN",
    ta: "ta-IN",
  };
  return langMap[language] || "en-IN";
}
