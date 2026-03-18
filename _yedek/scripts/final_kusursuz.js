const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');

const BASE_URL = 'https://www.yilmazmachine.com.tr';
const envanter = JSON.parse(fs.readFileSync('./scripts/makine_envanteri_master.json', 'utf8'));

const langPaths = {
    tr: '/urunler/', en: '/en/products/', ru: '/ru/товары/',
    fr: '/fr/produits/', es: '/es/productos/', pt: '/pt-pt/productos/',
    sr: '/sr/proizvodi/', it: '/it/prodotti/', ar: '/ar/products/'
};

function isimTemizle(slug, scrapedTitle) {
    const yasakli = ["ÜRÜN BİLGİSİ", "PRODUCT INFO", "ИНФОРМАЦИЯ О ПРОДУКТЕ", "INFORMACIÓN DEL PRODUCTO", "SEPETİM"];
    if (!scrapedTitle || yasakli.some(y => scrapedTitle.toUpperCase().includes(y))) {
        return slug.replace(/-/g, ' ').toUpperCase();
    }
    return scrapedTitle.split('—')[0].split('-')[0].trim(); // Gereksiz ekleri atar
}

async function derinSömür(slug) {
    let makineData = { slug: slug, diller: {} };

    for (let dil in langPaths) {
        try {
            const url = `${BASE_URL}${langPaths[dil]}${slug}/`;
            const res = await axios.get(url, { timeout: 12000 });
            const $ = cheerio.load(res.data);

            let data = {
                isim: isimTemizle(slug, $('.section-title').first().text().trim() || $('h1').text().trim()),
                aciklama: $('.product-info-text p').first().text().trim(),
                katalog: $('.pdf-list a').attr('href'),
                resimler: [],
                ozellik_gruplari: {},
                piktogramlar: {}
            };

            // 1. RESİM AVI (Hibrit & Lazy-Load Destekli)
            $('.product-images a, .owl-item a, .product-info-text + div a').each((i, el) => {
                const imgUrl = $(el).attr('href');
                if (imgUrl && imgUrl.includes('cloudfront') && !data.resimler.includes(imgUrl)) {
                    data.resimler.push(imgUrl);
                }
            });

            // 2. ÖZELLİK LİSTELERİ
            $('.col-md-4').each((i, el) => {
                const baslik = $(el).find('h3').text().trim();
                if (baslik) {
                    data.ozellik_gruplari[baslik] = [];
                    $(el).find('ul li').each((j, li) => {
                        data.ozellik_gruplari[baslik].push($(li).text().trim());
                    });
                }
            });

            // 3. PİKTOGRAM AVI (Senin Bulduğun Sınıflar)
            $('[class*="table-row-"]').each((i, el) => {
                const cls = $(el).attr('class');
                const match = cls.match(/table-row-([a-z_]+)/);
                if (match) {
                    const key = match[1];
                    const val = $(el).find('.text-row').text().trim().replace(/\s+/g, ' ');
                    if (val) data.piktogramlar[key] = val;
                }
            });

            makineData.diller[dil] = data;
            console.log(`   🎯 ${slug} [${dil.toUpperCase()}] ele geçirildi.`);

        } catch (err) {
            console.log(`   ⚠️ ${slug} [${dil.toUpperCase()}] bağlantı koptu.`);
        }
    }
    return makineData;
}

async function harekatiBaslat() {
    console.log("🚀 GENEL TAARRUZ BAŞLADI: 9 Dil, Tüm Envanter!");
    let toplamGanimet = [];
    let tumSlugs = [];
    for(let kat in envanter) {
        envanter[kat].makineler.forEach(m => {
            if(m.slug !== "urunler" && !tumSlugs.includes(m.slug)) tumSlugs.push(m.slug);
        });
    }

    for (let i = 0; i < tumSlugs.length; i++) {
        const mData = await derinSömür(tumSlugs[i]);
        toplamGanimet.push(mData);
        if (i % 5 === 0) fs.writeFileSync('./scripts/makine_verileri_KUSURSUZ_MASTER.json', JSON.stringify(toplamGanimet, null, 2));
    }

    fs.writeFileSync('./scripts/makine_verileri_KUSURSUZ_MASTER.json', JSON.stringify(toplamGanimet, null, 2));
    console.log("\n🏁 ZAFER BİZİMDİR DAYI! 'scripts/makine_verileri_KUSURSUZ_MASTER.json' hazır.");
}

harekatiBaslat();