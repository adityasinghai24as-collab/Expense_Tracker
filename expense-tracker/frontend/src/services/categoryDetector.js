/**
 * categoryDetector.js
 * Auto-detects an expense category + icon based on the description text.
 * Matches against a list of predefined category names (from DB seeds).
 */

// Category icons mirroring what the backend seeds (database.py)
export const CATEGORY_ICONS = {
  Food:            { icon: '🍔', color: '#EF4444' },
  Transport:       { icon: '🚗', color: '#3B82F6' },
  Utilities:       { icon: '🏠', color: '#EAB308' },
  Entertainment:   { icon: '🎬', color: '#A855F7' },
  Groceries:       { icon: '🛒', color: '#10B981' },
  Healthcare:      { icon: '🏥', color: '#EC4899' },
  Shopping:        { icon: '🛍️', color: '#F97316' },
  Travel:          { icon: '✈️', color: '#06B6D4' },
  Education:       { icon: '📚', color: '#8B5CF6' },
  Fitness:         { icon: '💪', color: '#84CC16' },
  Subscriptions:   { icon: '📱', color: '#6366F1' },
  Dining:          { icon: '🍽️', color: '#F43F5E' },
  Other:           { icon: '📌', color: '#6B7280' },
};

// Default icon for custom categories not in the list above
export const DEFAULT_ICON = '📌';
export const DEFAULT_COLOR = '#6B7280';

/**
 * Keyword rules: map keywords → category name.
 * Order matters — first match wins.
 */
const KEYWORD_RULES = [
  // Food & Dining
  { keywords: ['restaurant', 'cafe', 'coffee', 'lunch', 'dinner', 'breakfast', 'pizza', 'burger', 'sushi', 'taco', 'sandwich', 'snack', 'tea', 'chai', 'biryani', 'meal', 'eat', 'ate', 'food'], category: 'Food' },
  // Groceries
  { keywords: ['grocery', 'groceries', 'supermarket', 'vegetables', 'fruits', 'milk', 'bread', 'eggs', 'rice', 'dal', 'atta', 'flour', 'market', 'bazaar', 'kirana', 'provision'], category: 'Groceries' },
  // Transport
  { keywords: ['uber', 'ola', 'taxi', 'cab', 'bus', 'metro', 'train', 'petrol', 'diesel', 'fuel', 'parking', 'auto', 'rickshaw', 'toll', 'rapido', 'ride', 'commute', 'fare'], category: 'Transport' },
  // Utilities
  { keywords: ['electricity', 'electric', 'water bill', 'gas bill', 'internet', 'wifi', 'broadband', 'rent', 'maintenance', 'society', 'utilities', 'phone bill', 'recharge', 'bill'], category: 'Utilities' },
  // Entertainment
  { keywords: ['movie', 'cinema', 'netflix', 'prime', 'hotstar', 'hulu', 'youtube', 'game', 'gaming', 'concert', 'show', 'theatre', 'stream', 'spotify', 'music', 'amusement', 'park', 'fun'], category: 'Entertainment' },
  // Healthcare
  { keywords: ['doctor', 'hospital', 'clinic', 'medicine', 'pharmacy', 'medical', 'lab', 'test', 'health', 'dental', 'vision', 'eye', 'prescription', 'appointment', 'checkup', 'surgery'], category: 'Healthcare' },
  // Fitness
  { keywords: ['gym', 'fitness', 'yoga', 'workout', 'protein', 'supplement', 'cycling', 'running', 'sport', 'swim', 'membership'], category: 'Fitness' },
  // Shopping
  { keywords: ['amazon', 'flipkart', 'myntra', 'clothes', 'shirt', 'shoe', 'shopping', 'purchase', 'bought', 'buy', 'store', 'mall', 'gadget', 'electronics', 'appliance', 'furniture'], category: 'Shopping' },
  // Subscriptions
  { keywords: ['subscription', 'subscribe', 'annual plan', 'monthly plan', 'plan renewal', 'icloud', 'google one', 'microsoft', 'adobe', 'notion', 'figma'], category: 'Subscriptions' },
  // Travel
  { keywords: ['flight', 'hotel', 'airbnb', 'travel', 'trip', 'vacation', 'holiday', 'tour', 'booking', 'visa', 'airport', 'luggage', 'resort'], category: 'Travel' },
  // Education
  { keywords: ['course', 'book', 'udemy', 'coursera', 'tuition', 'school', 'college', 'fee', 'certification', 'exam', 'stationery', 'notebook', 'pen', 'textbook'], category: 'Education' },
];

/**
 * Detects the best matching category from the user's description.
 * Returns the category name or null if no match.
 *
 * @param {string} description - The expense description text
 * @param {Array}  categories  - Array of category objects from the API [{ id, name, icon, color }]
 * @returns {{ categoryId: number|null, categoryName: string|null, icon: string, color: string }}
 */
export function detectCategory(description, categories = []) {
  if (!description || description.trim().length < 2) {
    return { categoryId: null, categoryName: null, icon: DEFAULT_ICON, color: DEFAULT_COLOR };
  }

  const lower = description.toLowerCase();

  for (const rule of KEYWORD_RULES) {
    if (rule.keywords.some((kw) => lower.includes(kw))) {
      const matchedName = rule.category;

      // Find matching category from the backend list (case-insensitive)
      const found = categories.find(
        (c) => c.name.toLowerCase() === matchedName.toLowerCase()
      );

      const meta = CATEGORY_ICONS[matchedName] || { icon: DEFAULT_ICON, color: DEFAULT_COLOR };

      return {
        categoryId: found ? found.id : null,
        categoryName: found ? found.name : matchedName,
        icon: found?.icon || meta.icon,
        color: found?.color || meta.color,
      };
    }
  }

  return { categoryId: null, categoryName: null, icon: DEFAULT_ICON, color: DEFAULT_COLOR };
}

/**
 * Returns the icon and color for a known category name.
 * Used when creating new custom categories.
 *
 * @param {string} name - Category name
 * @returns {{ icon: string, color: string }}
 */
export function getIconForCategory(name) {
  if (!name) return { icon: DEFAULT_ICON, color: DEFAULT_COLOR };

  // Try exact match first
  const exact = CATEGORY_ICONS[name];
  if (exact) return exact;

  // Try case-insensitive match
  const lowerName = name.toLowerCase();
  const match = Object.entries(CATEGORY_ICONS).find(
    ([key]) => key.toLowerCase() === lowerName
  );
  if (match) return match[1];

  // Try keyword rules
  const lower = name.toLowerCase();
  for (const rule of KEYWORD_RULES) {
    if (rule.keywords.some((kw) => lower.includes(kw))) {
      return CATEGORY_ICONS[rule.category] || { icon: DEFAULT_ICON, color: DEFAULT_COLOR };
    }
  }

  return { icon: DEFAULT_ICON, color: DEFAULT_COLOR };
}
