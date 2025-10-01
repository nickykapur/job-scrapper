/**
 * Extract country name from location string
 */
export function getCountryFromLocation(location: string): string {
  if (!location) {
    return "Unknown";
  }

  const locationLower = location.toLowerCase();

  // Check for actively scraped country names in location string
  if (locationLower.includes("ireland")) {
    return "Ireland";
  } else if (locationLower.includes("spain")) {
    return "Spain";
  } else if (locationLower.includes("germany")) {
    return "Germany";
  } else if (locationLower.includes("united kingdom") || locationLower.includes("england") || locationLower.includes("scotland")) {
    return "United Kingdom";
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
    'United Kingdom': '🇬🇧',
  };
  return flags[country] || '🏳️';
}