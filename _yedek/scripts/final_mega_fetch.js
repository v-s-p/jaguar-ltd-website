const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');

const BASE_URL = 'https://www.yilmazmachine.com.tr';
// Önceki adımda seninle oluşturduğumuz o dev envanter
const envanter = JSON.parse(fs.readFileSync('./scripts/makine_envanteri_master.json', 'utf8'));

const langPaths = {
    tr: '/urunler/', en: '/en/products/', ru: '/ru/товары/',
    fr: '/fr/produits/', es: '/es/productos/', pt: '/pt-pt/productos/',
    sr: '/sr/proizvodi/', it: '/it/prodotti/', ar: '/ar/products/'
};

// Model ismini slug'dan temizleme fonksiyonu (Rasyonel İsimlendirme)
function modelIsmiDuzelt(slug, scrapedTitle) {
    const yasakli = ["ÜRÜN BİLGİSİ", "PRODUCT INFO", "ИНФОРМАЦИЯ О ПРОДУКТЕ", "INFORMATION SUR LE PRODUIT"];
    if (yasakli.some(y => scrapedTitle.toUpperCase().includes(y))) {
        return slug.replace(/-/g, ' ').toUpperCase();
    }
    return scrapedTitle;
}

async function derinSömür(slug) {
    let makineData = { slug: slug, diller: {} };

    for (let dil in langPaths) {
        try {
            const url = `${BASE_URL}${langPaths[dil]}${slug}/`;
            const res = await axios.get(url, { timeout: 10000 });
            const $ = cheerio.load(res.data);

            let rawTitle = $('.section-title').first().text().trim() || $('h1').text().trim();
            
            let data = {
                isim: modelIsmiDuzelt(slug, rawTitle),
                aciklama: $('.product-info-text p').first().text().trim(),
                katalog: $('.pdf-list a').attr('href'),
                resimler: [],
                ozellik_gruplari: {},
                piktogramlar: {}
            };

            // 1. Resimleri yakala
            $('.owl-item a').each((i, el) => {
                const img = $(el).attr('href');
                if (img && img.includes('cloudfront') && !data.resimler.includes(img)) {
                    data.resimler.push(img);
                }
            });

            // 2. Özellik/Aksesuar Listeleri
            $('.col-md-4').each((i, el) => {
                const baslik = $(el).find('h3').text().trim();
                if (baslik) {
                    data.ozellik_gruplari[baslik] = [];
                    $(el).find('ul li').each((j, li) => {
                        data.ozellik_gruplari[baslik].push($(li).text().trim());
                    });
                }
            });

            // 3. Teknik Piktogramlar (Senin o efsane 'table-row' tespitin!)
            $('.custom-col').each((i, el) => {
                const classes = $(el).attr('class').split(' ');
                const targetClass = classes.find(c => c.startsWith('table-row-'));
                if (targetClass) {
                    const key = targetClass.replace('table-row-', '');
                    const val = $(el).find('.text-row').text().trim().replace(/\s+/g, ' ');
                    data.piktogramlar[key] = val;
                }
            });

            makineData.diller[dil] = data;
            console.log(`   📡 ${slug} [${dil.toUpperCase()}] sızıldı.`);

        } catch (err) {
            console.log(`   ⚠️ ${slug} [${dil.toUpperCase()}] atlandı (Sayfa yok).`);
        }
    }
    return makineData;
}

async function anaGorev() {
    console.log("🚢 AMİRAL GEMİSİ HAREKETE GEÇTİ!");
    let toplamGanimet = [];
    
    // Tüm envanteri düz listeye çeviriyoruz
    let tumSlugs = [];
    for(let kat in envanter) {
        envanter[kat].makineler.forEach(m => {
            if(m.slug !== "urunler" && !tumSlugs.includes(m.slug)) tumSlugs.push(m.slug);
        });
    }

    console.log(`🎯 Hedef: ${tumSlugs.length} benzersiz makine.`);

    // Dayı, her seferinde 5 makineyi paralel çekerek hızlanıyoruz (Rasyonel Hız)
    for (let i = 0; i < tumSlugs.length; i++) {
        const mData = await derinSömür(tumSlugs[i]);
        toplamGanimet.push(mData);
        
        // Her 10 makinede bir dosyayı güncelle (Emniyet Kilidi)
        if (i % 10 === 0) {
            fs.writeFileSync('./scripts/makine_verileri_GLOBAL_MASTER.json', JSON.stringify(toplamGanimet, null, 2));
        }
    }

    fs.writeFileSync('./scripts/makine_verileri_GLOBAL_MASTER.json', JSON.stringify(toplamGanimet, null, 2));
    console.log("\n🏁 ZAFER DAYI! 'scripts/makine_verileri_GLOBAL_MASTER.json' tıka basa dolu.");
}

anaGorev();