import { ui, defaultLang } from './ui';

export function getLangFromUrl(url: URL) {
  const [, lang] = url.pathname.split('/');
  if (lang in ui) return lang as keyof typeof ui;
  return defaultLang;
}

export function useTranslations(lang: keyof typeof ui) {
  return function t(key: keyof typeof ui[typeof defaultLang]) {
    return ui[lang][key] || ui[defaultLang][key];
  }
}

export function getLanguagePaths() {
  return Object.keys(ui).map(lang => ({ params: { lang } }));
}

// Generate canonical URL for language switcher
export function getRelativeLocaleUrl(lang: string, path: string = '') {
  const normalizedPath = path.replace(/^\//, ''); // Baştaki slash'ı kaldır
  
  if (lang === defaultLang) {
    return `/${normalizedPath}`;
  }
  return `/${lang}/${normalizedPath}`;
}
