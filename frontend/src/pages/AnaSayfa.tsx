import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useApi } from "../lib/hooks";
import { BosDurum, HataKutusu, Kart, OranBar, Spinner } from "../components/ui";
import { aileEtiket, tamSayi, tarih, yuzde } from "../lib/format";

const ISLEMLER = [
  { yol: "/kampanyalar", ad: "Finansmanları İncele", not: "Konut, taşıt, ihtiyaç finansmanı" },
  { yol: "/kampanyalar?tur=kampanya", ad: "Kampanyaları Keşfet", not: "Bankalara ve türe göre filtrele" },
  { yol: "/karsilastirma", ad: "Bankaları Karşılaştır", not: "Kâr payı, vade, ücret, ödül" },
  { yol: "/asistan", ad: "Katılım Bankacılığı Asistanına Sor", not: "Doğal dille soru sorun" },
];

function OzetKart({ baslik, deger, alt }: { baslik: string; deger: string; alt?: string }) {
  return (
    <Kart className="p-4">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-400">{baslik}</div>
      <div className="mt-1 text-2xl font-semibold text-slate-800">{deger}</div>
      {alt && <div className="mt-0.5 text-xs text-slate-400">{alt}</div>}
    </Kart>
  );
}

export default function AnaSayfa() {
  const { veri, yukleniyor, hata } = useApi(() => api.stats(), []);

  return (
    <div className="space-y-8">
      <section className="rounded-2xl bg-gradient-to-br from-brand-700 to-brand-500 px-6 py-10 text-white sm:px-10">
        <h1 className="text-3xl font-bold sm:text-4xl">Katılım Bankacılığı</h1>
        <p className="mt-3 max-w-2xl text-brand-50/90">
          Katılım bankalarının finansman ve kampanyalarını keşfedin, karşılaştırın ve size uygun
          seçenekleri değerlendirin. Dilerseniz tahmini finansman hesabı yapın veya asistana
          doğal dille sorun.
        </p>
        <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {ISLEMLER.map((i) => (
            <Link
              key={i.yol}
              to={i.yol}
              className="rounded-xl bg-white/10 px-4 py-3 backdrop-blur transition hover:bg-white/20"
            >
              <div className="font-medium">{i.ad}</div>
              <div className="text-xs text-brand-50/80">{i.not}</div>
            </Link>
          ))}
        </div>
      </section>

      {yukleniyor && <Spinner />}
      {hata && <HataKutusu mesaj={hata} />}

      {veri && (
        <>
          <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <OzetKart baslik="Toplam Banka" deger={tamSayi(veri.toplam_banka)} />
            <OzetKart
              baslik="Finansal Verili Kayıt"
              deger={tamSayi(veri.finansal_veri_olan_kayit)}
              alt={`${veri.toplam_kayit} kayıttan · ${veri.kuratorlu_kayit} küratörlü`}
            />
            <OzetKart baslik="Toplam Kampanya" deger={tamSayi(veri.toplam_kampanya)} />
            <OzetKart baslik="Aktif Kampanya" deger={tamSayi(veri.aktif_kampanya)} />
            <OzetKart
              baslik="En Düşük Finansman Kâr Payı"
              deger={yuzde(veri.finansman_kar_payi.min)}
              alt={`${veri.finansman_kar_payi.veri_olan_kayit} kayıtta veri var`}
            />
            <OzetKart
              baslik="Medyan Finansman Kâr Payı"
              deger={yuzde(veri.finansman_kar_payi.medyan)}
            />
            <OzetKart
              baslik="En Uzun Vade"
              deger={veri.vade_dagilimi_ay.max ? `${veri.vade_dagilimi_ay.max} ay` : "Belirtilmemiş"}
            />
            <OzetKart
              baslik="Son Veri Güncelleme"
              deger={tarih(veri.guncelleme_tarihi) || "—"}
            />
          </section>

          <section className="grid gap-4 lg:grid-cols-2">
            <Kart className="p-5">
              <h2 className="mb-4 font-semibold text-slate-800">Ürün Ailesine Göre Dağılım</h2>
              {veri.urun_ailesi_dagilimi.length ? (
                <OranBar
                  toplam={veri.toplam_kayit}
                  veriler={veri.urun_ailesi_dagilimi.map((d) => ({
                    etiket: aileEtiket(d.aile),
                    adet: d.adet,
                  }))}
                />
              ) : (
                <BosDurum mesaj="Veri yok" />
              )}
            </Kart>
            <Kart className="p-5">
              <h2 className="mb-4 font-semibold text-slate-800">Bankaya Göre Dağılım</h2>
              <OranBar
                toplam={veri.toplam_kayit}
                veriler={veri.banka_dagilimi.map((d) => ({ etiket: d.banka ?? "-", adet: d.adet }))}
              />
            </Kart>
          </section>

          <p className="text-xs text-slate-400">
            Tüm sayılar veri kümesinden anlık olarak hesaplanır. Finansman kâr payı istatistikleri
            yalnızca aylık kâr payı oranı verisi bulunan {veri.finansman_kar_payi.veri_olan_kayit}{" "}
            kayıt üzerinden çıkarılmıştır; ürün fiyatlaması bankaya göre değişir —{" "}
            <span className="font-medium">bu değerler bir teklif değildir</span>.
          </p>
        </>
      )}
    </div>
  );
}
