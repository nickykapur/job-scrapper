/**
 * Extract country name from location string
 */
export function getCountryFromLocation(location: string): string {
  if (!location) {
    return "Unknown";
  }

  const locationLower = location.toLowerCase();

  // Check for actively scraped cities and countries
  if (locationLower.includes("dublin") || locationLower.includes("ireland")) {
    return "Ireland";
  } else if (locationLower.includes("barcelona") || locationLower.includes("madrid") || locationLower.includes("spain")) {
    return "Spain";
  } else if (locationLower.includes("berlin") || locationLower.includes("germany")) {
    return "Germany";
  } else if (locationLower.includes("london") || locationLower.includes("united kingdom") || locationLower.includes("england") || locationLower.includes("scotland")) {
    return "United Kingdom";
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
  } else if (locationLower.includes("berlin")) {
    return "Berlin";
  } else if (locationLower.includes("london")) {
    return "London";
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
    'Germany': '🇩🇪',
    'United Kingdom': '🇬🇧',
  };
  return flags[country] || '🏳️';
}