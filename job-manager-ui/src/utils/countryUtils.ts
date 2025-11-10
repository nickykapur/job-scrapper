/**
 * Extract country name from location string
 */
export function getCountryFromLocation(location: string): string {
  if (!location) {
    return "Unknown";
  }

  const locationLower = location.toLowerCase();

  // Check for all 10 actively scraped cities and countries
  if (locationLower.includes("dublin") || locationLower.includes("ireland")) {
    return "Ireland";
  } else if (locationLower.includes("barcelona") || locationLower.includes("madrid") || locationLower.includes("spain")) {
    return "Spain";
  } else if (locationLower.includes("panama")) {
    return "Panama";
  } else if (locationLower.includes("santiago") || locationLower.includes("chile")) {
    return "Chile";
  } else if (locationLower.includes("amsterdam") || locationLower.includes("netherlands") || locationLower.includes("holland")) {
    return "Netherlands";
  } else if (locationLower.includes("berlin") || locationLower.includes("germany") || locationLower.includes("deutschland")) {
    return "Germany";
  } else if (locationLower.includes("stockholm") || locationLower.includes("sweden") || locationLower.includes("sverige")) {
    return "Sweden";
  } else if (locationLower.includes("brussels") || locationLower.includes("belgium") || locationLower.includes("belgique")) {
    return "Belgium";
  } else if (locationLower.includes("copenhagen") || locationLower.includes("denmark") || locationLower.includes("danmark")) {
    return "Denmark";
  } else if (locationLower.includes("luxembourg")) {
    return "Luxembourg";
  } else {
    return "Unknown";
  }
}

/**
 * Extract city name from location string for display purposes
 */
export function getCityFromLocation(location: string): string {
  if (!location) {
    return "Unknown";
  }

  const locationLower = location.toLowerCase();

  if (locationLower.includes("dublin")) {
    return "Dublin";
  } else if (locationLower.includes("barcelona")) {
    return "Barcelona";
  } else if (locationLower.includes("madrid")) {
    return "Madrid";
  } else if (locationLower.includes("panama")) {
    return "Panama City";
  } else if (locationLower.includes("santiago")) {
    return "Santiago";
  } else if (locationLower.includes("amsterdam")) {
    return "Amsterdam";
  } else if (locationLower.includes("berlin")) {
    return "Berlin";
  } else if (locationLower.includes("stockholm")) {
    return "Stockholm";
  } else if (locationLower.includes("brussels")) {
    return "Brussels";
  } else if (locationLower.includes("copenhagen")) {
    return "Copenhagen";
  } else if (locationLower.includes("luxembourg")) {
    return "Luxembourg City";
  } else {
    // Try to extract first part of location as city
    const parts = location.split(',');
    return parts[0].trim() || "Unknown";
  }
}

/**
 * Get country flag emoji for a country name
 */
export function getCountryFlag(country: string): string {
  const flags: Record<string, string> = {
    'Ireland': '🇮🇪',
    'Spain': '🇪🇸',
    'Panama': '🇵🇦',
    'Chile': '🇨🇱',
    'Netherlands': '🇳🇱',
    'Germany': '🇩🇪',
    'Sweden': '🇸🇪',
    'Belgium': '🇧🇪',
    'Denmark': '🇩🇰',
    'Luxembourg': '🇱🇺',
  };
  return flags[country] || '🏳️';
}