import labelsData from '../data/subcategory_labels.json';

type SupportedLang = 'bg' | 'en' | 'ru';

interface LabelEntry {
  key: string;
  bg: string;
  en: string;
  ru: string;
}

const labels = labelsData.labels as LabelEntry[];

/**
 * Returns the translated display label for a subcategory key.
 * Falls back: lang → en → key itself (never blank).
 */
export function getSubcategoryLabel(key: string, lang: string): string {
  const entry = labels.find((l) => l.key === key);
  if (!entry) return key;
  const l = lang as SupportedLang;
  return entry[l] || entry.en || key;
}
