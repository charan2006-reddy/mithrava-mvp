// ---------------------------------------------------------------------------
// Raw types matching the backend snake_case responses
// ---------------------------------------------------------------------------

/** Raw current weather from backend (snake_case) */
export interface RawWeatherData {
  city: string;
  country: string;
  temperature: number;
  feels_like: number;
  humidity: number;
  pressure: number;
  wind_speed: number;
  wind_direction: number;
  visibility: number;
  description: string;
  icon: string;
  clouds: number;
  sunrise: string;
  sunset: string;
  timestamp: string;
  alerts?: string[];
}

/** Raw daily forecast from backend (snake_case) */
export interface RawForecastDay {
  date: string;
  temperature_min: number;
  temperature_max: number;
  humidity: number;
  description: string;
  icon: string;
  rain_chance: number;
  wind_speed: number;
}

/** Raw forecast API response data */
export interface RawForecastResponse {
  city: string;
  days: number;
  forecast: RawForecastDay[];
}

/** Raw farming advice API response data */
export interface RawFarmingAdviceResponse {
  city: string;
  weather: RawWeatherData;
  advice: string;
  alerts: string[];
}

// ---------------------------------------------------------------------------
// Frontend types (camelCase) used by UI components
// ---------------------------------------------------------------------------

/** Current weather data */
export interface WeatherData {
  city: string;
  country: string;
  temperature: number;
  feelsLike: number;
  humidity: number;
  pressure: number;
  windSpeed: number;
  windDirection: number;
  visibility: number;
  description: string;
  icon: string;
  clouds: number;
  sunrise: string;
  sunset: string;
  timestamp: string;
  alerts: string[];
}

/** Daily forecast */
export interface ForecastDay {
  date: string;
  tempMin: number;
  tempMax: number;
  humidity: number;
  description: string;
  icon: string;
  rainChance: number;
  windSpeed: number;
}

/** Weather forecast (mapped) */
export interface WeatherForecast {
  city: string;
  days: ForecastDay[];
}

/** Farming weather advice (mapped) */
export interface FarmingAdvice {
  city: string;
  advice: string;
  alerts: string[];
  riskLevel: "low" | "medium" | "high";
}

// ---------------------------------------------------------------------------
// Mapping functions
// ---------------------------------------------------------------------------

/** Map raw weather data to frontend camelCase */
export function mapWeatherData(raw: RawWeatherData): WeatherData {
  return {
    city: raw.city,
    country: raw.country,
    temperature: raw.temperature,
    feelsLike: raw.feels_like,
    humidity: raw.humidity,
    pressure: raw.pressure,
    windSpeed: raw.wind_speed,
    windDirection: raw.wind_direction,
    visibility: raw.visibility,
    description: raw.description,
    icon: raw.icon,
    clouds: raw.clouds ?? 0,
    sunrise: raw.sunrise,
    sunset: raw.sunset,
    timestamp: raw.timestamp,
    alerts: raw.alerts ?? [],
  };
}

/** Map raw forecast day to frontend camelCase */
export function mapForecastDay(raw: RawForecastDay): ForecastDay {
  return {
    date: raw.date,
    tempMin: raw.temperature_min,
    tempMax: raw.temperature_max,
    humidity: raw.humidity,
    description: raw.description,
    icon: raw.icon,
    rainChance: raw.rain_chance,
    windSpeed: raw.wind_speed,
  };
}

/** Map raw forecast response to frontend WeatherForecast */
export function mapForecastResponse(raw: RawForecastResponse): WeatherForecast {
  return {
    city: raw.city,
    days: raw.forecast.map(mapForecastDay),
  };
}

/** Map raw farming advice response to frontend FarmingAdvice */
export function mapFarmingAdvice(raw: RawFarmingAdviceResponse): FarmingAdvice {
  // Determine risk level from alerts
  let riskLevel: "low" | "medium" | "high" = "low";
  if (raw.alerts?.length > 0) {
    const hasRed = raw.alerts.some((a) => a.startsWith("🔴"));
    riskLevel = hasRed ? "high" : "medium";
  }

  return {
    city: raw.city,
    advice: raw.advice,
    alerts: raw.alerts ?? [],
    riskLevel,
  };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Get weather emoji from OpenWeatherMap icon code */
export function getWeatherEmoji(iconCode: string): string {
  const map: Record<string, string> = {
    "01d": "☀️", "01n": "🌙",
    "02d": "⛅", "02n": "☁️",
    "03d": "☁️", "03n": "☁️",
    "04d": "☁️", "04n": "☁️",
    "09d": "🌧️", "09n": "🌧️",
    "10d": "🌦️", "10n": "🌧️",
    "11d": "⛈️", "11n": "⛈️",
    "13d": "❄️", "13n": "❄️",
    "50d": "🌫️", "50n": "🌫️",
  };
  return map[iconCode] || "🌤️";
}

/** Get weather gradient class from condition */
export function getWeatherGradient(description: string): string {
  const desc = description.toLowerCase();
  if (desc.includes("rain") || desc.includes("drizzle") || desc.includes("shower")) {
    return "from-blue-500 to-blue-700";
  }
  if (desc.includes("cloud") || desc.includes("overcast")) {
    return "from-gray-400 to-blue-500";
  }
  if (desc.includes("storm") || desc.includes("thunder")) {
    return "from-gray-600 to-purple-700";
  }
  if (desc.includes("clear") || desc.includes("sunny")) {
    return "from-amber-400 to-orange-500";
  }
  if (desc.includes("haze") || desc.includes("mist") || desc.includes("fog")) {
    return "from-gray-300 to-gray-500";
  }
  return "from-blue-400 to-blue-600";
}

/** Get day name from date string */
export function getDayName(dateStr: string): string {
  const date = new Date(dateStr + "T00:00:00");
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  if (date.getTime() === today.getTime()) return "Today";
  if (date.getTime() === tomorrow.getTime()) return "Tmrw";

  return date.toLocaleDateString("en-IN", { weekday: "short" });
}
