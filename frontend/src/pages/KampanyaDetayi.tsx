import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../api/client";
import { useApi } from "../lib/hooks";
import { Buton, HataKutusu, Kart, Rozet, Spinner } from "../components/ui";
import { aileEtiket, ay, bosDegilse, paraTL, tarih, yuzde } from "../lib/format";

function Satir({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex justify-between gap-4 border-b border-slate-100 py-2 text-sm last:border-0">
      <dt className="text-slate-500">{k}</dt>
      <dd className="text-right font-medium text-slate-800">{v}</dd>
    </div>
  );
}

export default function KampanyaDetayi() {
  const { id = "" } = useParams();
  const nav = useNavigate();
  const { veri: k, yukleniyor, hata } = useApi(() => api.campaign(id), [id]);

  if (yukleniyor) return <Spinner />;
  if (hata) return <HataKutusu mesaj={hata} />;
  if (!k) return null;

  const on = k.hesaplama_on_degerler;
  function hesaplamayaGit() {
    const q = new URLSearchParams({ record_id: k!.record_id });
    if (on?.finansman_tutari) q.set("tutar", String(on.finansman_tutari));
    if (on?.vade_ay) q.set("vade", String(on.vade_ay));
    if (on?.kar_payi_orani) q.set("oran", String(on.kar_payi_orani));
    if (on?.oran_periyodu) q.set("periyot", on.oran_periyodu);
    nav(`/hesaplama?${q.toString()}`);
  }

  const karPayi =
    k.kar_payi_orani_min === null
      ? "Belirtilmemiş"
      : k.kar_payi_orani_max && k.kar_payi_orani_max !== k.kar_payi_orani_min
        ? `${yuzde(k.kar_payi_orani_min)} – ${yuzde(k.kar_payi_orani_max)}`
        : yuzde(k.kar_payi_orani_min);

  return (
    <div className="space-y-6">
      <Link to="/kampanyalar" className="text-sm text-brand-700 hover:underline">
        ← Listeye dön
      </Link>

      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="text-sm font-medium text-slate-400">{k.banka}</div>
          <h1 className="text-2xl font-bold text-slate-800">{bosDegilse(k.urun_adi ?? k.baslik)}</h1>
          <div className="mt-2 flex flex-wrap gap-1.5">
            <Rozet renk="mavi">{aileEtiket(k.urun_ailesi)}</Rozet>
            {k.kampanya_turu !== "Kampanya Değil" && <Rozet>{k.kampanya_turu}</Rozet>}
            <Rozet renk={k.aktif_mi ? "yesil" : "slate"}>
              {k.aktif_mi ? "Aktif" : "Süresi geçmiş"}
            </Rozet>
          </div>
        </div>
        {k.urun_ailesi === "finansman" && (
          <Buton onClick={hesaplamayaGit}>Bu kampanya için tahmini hesapla</Buton>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Kart className="p-5">
          <h2 className="mb-2 font-semibold text-slate-800">Finansal Bilgiler</h2>
          <dl>
            <Satir k="Kâr payı oranı" v={karPayi} />
            <Satir k="Kâr payı türü" v={k.kar_payi_turu === "bilinmiyor" ? "Belirtilmemiş" : k.kar_payi_turu} />
            <Satir k="Ham ifade" v={bosDegilse(k.kar_payi_orani_raw)} />
            <Satir
              k="Vade"
              v={k.vade_max_ay ? (k.vade_min_ay && k.vade_min_ay !== k.vade_max_ay ? `${k.vade_min_ay} – ${k.vade_max_ay} ay` : ay(k.vade_max_ay)) : bosDegilse(k.vade_raw)}
            />
            <Satir k="Taksit sayısı" v={k.taksit_sayisi ? String(k.taksit_sayisi) : "Belirtilmemiş"} />
            <Satir
              k="Finansman tutarı"
              v={k.finansman_tutari_max ? `${paraTL(k.finansman_tutari_max)}'ye kadar` : bosDegilse(k.finansman_tutari_raw)}
            />
            <Satir k="Finansman oranı" v={k.finansman_orani ? yuzde(k.finansman_orani) : "Belirtilmemiş"} />
            <Satir
              k="Tahsis ücreti"
              v={bosDegilse(k.tahsis_ucreti_raw) === "Belirtilmemiş" ? (k.tahsis_ucreti_tl ? paraTL(k.tahsis_ucreti_tl, true) : "Belirtilmemiş") : k.tahsis_ucreti_raw!}
            />
            <Satir k="Masraf bilgisi" v={bosDegilse(k.masraf_bilgisi)} />
            <Satir k="Ödül" v={bosDegilse(k.odul_miktari_raw)} />
            <Satir k="Alışveriş puanı" v={bosDegilse(k.alisveris_puani_raw)} />
            <Satir k="İndirim oranı" v={bosDegilse(k.indirim_orani_raw)} />
          </dl>
        </Kart>

        <div className="space-y-6">
          <Kart className="p-5">
            <h2 className="mb-2 font-semibold text-slate-800">Kampanya Bilgileri</h2>
            <dl>
              <Satir k="Başlangıç tarihi" v={bosDegilse(k.kampanya_baslangic_tarihi)} />
              <Satir k="Bitiş tarihi" v={bosDegilse(k.kampanya_bitis_tarihi)} />
            </dl>
            {k.hedef_kitle.length > 0 && (
              <div className="mt-3">
                <div className="text-xs font-medium uppercase text-slate-400">Hedef kitle</div>
                <ul className="mt-1 list-inside list-disc text-sm text-slate-700">
                  {k.hedef_kitle.map((h, i) => (
                    <li key={i}>{h}</li>
                  ))}
                </ul>
              </div>
            )}
            {k.avantajlar.length > 0 && (
              <div className="mt-3">
                <div className="text-xs font-medium uppercase text-slate-400">Avantajlar</div>
                <ul className="mt-1 list-inside list-disc text-sm text-slate-700">
                  {k.avantajlar.map((h, i) => (
                    <li key={i}>{h}</li>
                  ))}
                </ul>
              </div>
            )}
            {k.kampanya_kosullari.length > 0 && (
              <div className="mt-3">
                <div className="text-xs font-medium uppercase text-slate-400">Kampanya koşulları</div>
                <ul className="mt-1 list-inside list-disc text-sm text-slate-700">
                  {k.kampanya_kosullari.map((h, i) => (
                    <li key={i}>{h}</li>
                  ))}
                </ul>
              </div>
            )}
          </Kart>

          <Kart className="p-5">
            <h2 className="mb-2 font-semibold text-slate-800">Kaynak</h2>
            <dl>
              <Satir k="Banka" v={k.kaynak_bilgisi.banka} />
              <Satir k="Veri tarihi" v={tarih(k.kaynak_bilgisi.veri_tarihi)} />
            </dl>
            {k.kaynak_bilgisi.url && (
              <a
                href={k.kaynak_bilgisi.url}
                target="_blank"
                rel="noreferrer"
                className="mt-2 inline-block break-all text-sm text-brand-700 hover:underline"
              >
                {k.kaynak_bilgisi.url}
              </a>
            )}
          </Kart>
        </div>
      </div>

      {k.metin && (
        <Kart className="p-5">
          <h2 className="mb-2 font-semibold text-slate-800">Kaynak Metni</h2>
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-600">
            {k.metin.length > 1500 ? k.metin.slice(0, 1500) + "…" : k.metin}
          </p>
        </Kart>
      )}
    </div>
  );
}
