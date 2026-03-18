const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');

const BASE_URL = 'https://www.yilmazmachine.com.tr';
const envanter = JSON.parse(fs.readFileSync('./scripts/makine_envanteri_master.json', 'utf8'));

const langPaths = {
    tr: '/urunler/', en: '/en/products/', ru: '/ru/товары/',
    fr: '/fr/produits/', es: '/es/productos/', pt: '/pt-pt/productos/',
    sr: '/sr/proizvodi/', it: '/it/prodotti/', ar: '/ar/products/' // Arapça yolu dile göre değişebilir
};

async function makineDetayCek(slug) {
    let makineData = { slug: slug, diller: {} };

    for (let dil in langPaths) {
        try {
            const url = `${BASE_URL}${langPaths[dil]}${slug}/`;
            const res = await axios.get(url, { timeout: 8000 });
            const $ = cheerio.load(res.data);

            let data = {
                isim: $('.section-title').first().text().trim() || $('title').text().split('|')[0].trim(),
                aciklama: $('.product-info-text p').first().text().trim(),
                katalog: $('.pdf-list a').attr('href'),
                resimler: [],
                listeler: {},
                teknik_tablo: {}
            };

            // 1. Resimleri topla (Cloudfront linkleri)
            $('.owl-item a').each((i, el) => {
                const img = $(el).attr('href');
                if (img && !data.resimler.includes(img)) data.resimler.push(img);
            });

            // 2. Özellikler ve Aksesuarlar (Senin bulduğun col-md-4 yapısı)
            $('.col-md-4').each((i, el) => {
                const baslik = $(el).find('h3').text().trim();
                if (baslik) {
                    data.listeler[baslik] = [];
                    $(el).find('ul li').each((j, li) => {
                        data.listeler[baslik].push($(li).text().trim());
                    });
                }
            });

            // 3. Teknik Tablo (Piktogramlar - Elektrik, Basınç, Ağırlık...)
            $('.custom-col').each((i, el) => {
                const className = $(el).attr('class');
                const key = className.split('table-row-')[1] || `spec_${i}`;
                const val = $(el).find('.text-row').text().trim().replace(/\s+/g, ' ');
                if (val) data.teknik_tablo[key] = val;
            });

            makineData.diller[dil] = data;
            console.log(`   ✅ ${slug} [${dil.toUpperCase()}] sömürüldü.`);

        } catch (err) {
            console.log(`   ⚠️ ${slug} [${dil.toUpperCase()}] dilde eksik veya hata.`);
        }
    }
    return makineData;
}

async function operasyonBaslat() {
    console.log("🚀 KOMPLE OPERASYON BAŞLADI: Hedef 9 Dil!");
    let finalVeri = [];
    
    // Dayı, mobil veri yanmasın diye şimdilik ilk 3 makineyi alıyoruz
    const makineListesi = [];
    for(let kat in envanter) makineListesi.push(...envanter[kat].makineler);
    const testListesi = makineListesi.slice(0, 3); 

    for (let m of testListesi) {
        if(m.slug === "urunler") continue;
        const sonuc = await makineDetayCek(m.slug);
        finalVeri.push(sonuc);
    }

    fs.writeFileSync('./scripts/makine_verileri_KUSURSUZ_FINAL.json', JSON.stringify(finalVeri, null, 2));
    console.log("\n🏁 BİTTİ DAYI! 'scripts/makine_verileri_KUSURSUZ_FINAL.json' dosyasını kontrol et.");
}

operasyonBaslat();