/**
 * Extract country name from location string
 */
export function getCountryFromLocation(location: string): string {
  if (!location) {
    return "Unknown";
  }

  const locationLower = location.toLowerCase();

  // Check for country names in location string
  if (locationLower.includes("ireland")) {
    return "Ireland";
  } else if (locationLower.includes("spain")) {
    return "Spain";
  } else if (locationLower.includes("germany")) {
    return "Germany";
  } else if (locationLower.includes("switzerland")) {
    return "Switzerland";
  } else if (locationLower.includes("united kingdom") || locationLower.includes("england") || locationLower.includes("scotland")) {
    return "United Kingdom";
  } else if (locationLower.includes("netherlands")) {
    return "Netherlands";
  } else if (locationLower.includes("france")) {
    return "France";
  } else if (locationLower.includes("italy")) {
    return "Italy";
  } else {
    return "Unknown";
  }
}

/**
 * Get country flag emoji for a country name
 */
export function getCountryFlag(country: string): string {
  const flags: Record<string, string> = {
    'Ireland': '🇮🇪',
    'Spain': '🇪🇸',
    'Germany': '🇩🇪',
    'Switzerland': '🇨🇭',
    'United Kingdom': '🇬🇧',
    'Netherlands': '🇳🇱',
    'France': '🇫🇷',
    'Italy': '🇮🇹',
  };
  return flags[country] || '🏳️';
}