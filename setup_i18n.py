import os

routes = [
    ('index.astro', 'HomePage'),
    ('about.astro', 'AboutPage'),
    ('contact.astro', 'ContactPage'),
    ('gdpr.astro', 'GdprPage'),
]

dynamic_routes = [
    ('kategori/[slug].astro', 'KategoriPage'),
    ('machines/[slug].astro', 'MachinePage')
]

# Base Routes
for filename, comp in routes:
    path = os.path.join('src', 'pages', filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f'---\nimport Component from \"../components/pages/{comp}.astro\";\n---\n<Component />\n')

for filename, comp in dynamic_routes:
    path = os.path.join('src', 'pages', filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f'---\nimport Component from \"../../components/pages/{comp}.astro\";\n')
        f.write('export { getStaticPaths } from \"../../components/pages/' + comp + '.astro\";\n')
        f.write('---\n<Component />\n')

# Localized Routes
lang_dir = os.path.join('src', 'pages', '[lang]')
for filename, comp in routes:
    path = os.path.join(lang_dir, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f'---\nimport Component from \"../../components/pages/{comp}.astro\";\n')
        f.write('export { getLanguagePaths as getStaticPaths } from \"../../i18n/utils\";\n')
        f.write('---\n<Component />\n')

for filename, comp in dynamic_routes:
    path = os.path.join(lang_dir, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f'---\nimport Component from \"../../../components/pages/{comp}.astro\";\n')
        f.write('import { getLanguagePaths } from \"../../../i18n/utils\";\n')
        f.write(f'import {{ getStaticPaths as getComponentPaths }} from \"../../../components/pages/{comp}.astro\";\n')
        f.write('export async function getStaticPaths() {\n')
        f.write('  const componentPaths = await getComponentPaths();\n')
        f.write('  const langs = getLanguagePaths();\n')
        f.write('  return langs.flatMap(l => componentPaths.map(p => ({ params: { lang: l.params.lang, slug: p.params.slug }, props: p.props })));\n')
        f.write('}\n')
        f.write('---\n<Component />\n')

