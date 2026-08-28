import { useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import { useApi } from "../lib/hooks";
import { BosDurum, Buton, HataKutusu, Kart, Rozet, Spinner } from "../components/ui";
import { aileEtiket, ay, bosDegilse, paraTL, yuzde } from "../lib/format";
import type { KampanyaOzet } from "../api/types";

const SIRALAMA = [
  { v: "banka", ad: "Bankaya göre" },
  { v: "kar_payi_artan", ad: "Kâr payı (artan)" },
  { v: "kar_payi_azalan", ad: "Kâr payı (azalan)" },
  { v: "vade_azalan", ad: "Vade (uzun → kısa)" },
  { v: "vade_artan", ad: "Vade (kısa → uzun)" },
];

function KarPayiEtiket(k: KampanyaOzet) {
  if (k.kar_payi_orani_min === null) return "Belirtilmemiş";
  const per = k.kar_payi_turu === "aylik" ? " (aylık)" : k.kar_payi_turu === "yillik" ? " (yıllık)" : "";
  if (k.kar_payi_orani_max && k.kar_payi_orani_max !== k.kar_payi_orani_min)
    return `${yuzde(k.kar_payi_orani_min)} – ${yuzde(k.kar_payi_orani_max)}${per}`;
  return `${yuzde(k.kar_payi_orani_min)}${per}`;
}

export default function Kampanyalar() {
  const [sp] = useSearchParams();
  const { veri: filtreler } = useApi(() => api.filters(), []);

  const [banka, setBanka] = useState<string[]>([]);
  const [aile, setAile] = useState("");
  const [tur, setTur] = useState("");
  const [sadeceAktif, setSadeceAktif] = useState(false);
  const [karPayiVar, setKarPayiVar] = useState(false);
  const [kurumsalGoster, setKurumsalGoster] = useState(false);
  const [q, setQ] = useState("");
  const [sort, setSort] = useState("banka");
  const [page, setPage] = useState(1);

  const params = useMemo(
    () => ({
      banka,
      urun_ailesi: aile || undefined,
      kampanya_turu: tur || undefined,
      aktif_mi: sadeceAktif || undefined,
      has_kar_payi: karPayiVar || undefined,
      has_finansal_veri: kurumsalGoster ? undefined : true,
      q: q || undefined,
      sort,
      page,
      size: 12,
    }),
    [banka, aile, tur, sadeceAktif, karPayiVar, kurumsalGoster, q, sort, page]
  );

  const { veri, yukleniyor, hata } = useApi(() => api.campaigns(params), [JSON.stringify(params)]);

  const kampanyaModu = sp.get("tur") === "kampanya";

  function bankaToggle(b: string) {
    setPage(1);
    setBanka((mevcut) => (mevcut.includes(b) ? mevcut.filter((x) => x !== b) : [...mevcut, b]));
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">
          {kampanyaModu ? "Kampanyalar" : "Finansman & Kampanyalar"}
        </h1>
        <p className="text-sm text-slate-500">
          Gerçek veri kümesinde bulunan ürün ve kampanyaları filtreleyin.
        </p>
      </div>

      <Kart className="p-4 space-y-4">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <label className="text-sm">
            <span className="mb-1 block font-medium text-slate-600">Ürün ailesi</span>
            <select
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
              value={aile}
              onChange={(e) => {
                setPage(1);
                setAile(e.target.value);
              }}
            >
              <option value="">Tümü</option>
              {filtreler?.urun_aileleri.map((a) => (
                <option key={a} value={a}>
                  {aileEtiket(a)}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm">
            <span className="mb-1 block font-medium text-slate-600">Kampanya türü</span>
            <select
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
              value={tur}
              onChange={(e) => {
                setPage(1);
                setTur(e.target.value);
              }}
            >
              <option value="">Tümü</option>
              {filtreler?.kampanya_turleri.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm">
            <span className="mb-1 block font-medium text-slate-600">Sıralama</span>
            <select
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
              value={sort}
              onChange={(e) => setSort(e.target.value)}
            >
              {SIRALAMA.map((s) => (
                <option key={s.v} value={s.v}>
                  {s.ad}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm">
            <span className="mb-1 block font-medium text-slate-600">Ara</span>
            <input
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
              placeholder="ürün / başlık"
              value={q}
              onChange={(e) => {
                setPage(1);
                setQ(e.target.value);
              }}
            />
          </label>
        </div>

        <div className="flex flex-wrap gap-2">
          {filtreler?.bankalar.map((b) => (
            <button
              key={b}
              onClick={() => bankaToggle(b)}
              className={`rounded-full border px-3 py-1 text-xs font-medium transition ${
                banka.includes(b)
                  ? "border-brand-600 bg-brand-50 text-brand-700"
                  : "border-slate-300 text-slate-600 hover:bg-slate-50"
              }`}
            >
              {b}
            </button>
          ))}
        </div>

        <div className="flex flex-wrap gap-4 text-sm text-slate-600">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={sadeceAktif}
              onChange={(e) => {
                setPage(1);
                setSadeceAktif(e.target.checked);
              }}
            />
            Yalnızca aktif kampanyalar
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={karPayiVar}
              onChange={(e) => {
                setPage(1);
                setKarPayiVar(e.target.checked);
              }}
            />
            Kâr payı oranı belirtilmiş olanlar
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={kurumsalGoster}
              onChange={(e) => {
                setPage(1);
                setKurumsalGoster(e.target.checked);
              }}
            />
            Kurumsal / bilgilendirme sayfalarını da göster
          </label>
        </div>
      </Kart>

      {yukleniyor && <Spinner />}
      {hata && <HataKutusu mesaj={hata} />}

      {veri && (
        <>
          <div className="text-sm text-slate-500">{veri.toplam} sonuç</div>
          {veri.items.length === 0 ? (
            <BosDurum mesaj="Seçtiğiniz filtrelere uyan kayıt bulunamadı." />
          ) : (
            <div className="grid gap-3 md:grid-cols-2">
              {veri.items.map((k) => (
                <Link key={k.record_id} to={`/kampanya/${k.record_id}`}>
                  <Kart className="h-full p-4 transition hover:border-brand-300 hover:shadow-md">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="text-xs font-medium text-slate-400">{k.banka}</div>
                        <div className="font-semibold text-slate-800">
                          {bosDegilse(k.urun_adi ?? k.baslik)}
                        </div>
                      </div>
                      <Rozet renk={k.aktif_mi ? "yesil" : "slate"}>
                        {k.aktif_mi ? "Aktif" : "Süresi geçmiş"}
                      </Rozet>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-1.5">
                      <Rozet renk="mavi">{aileEtiket(k.urun_ailesi)}</Rozet>
                      {k.kampanya_turu !== "Kampanya Değil" && <Rozet>{k.kampanya_turu}</Rozet>}
                    </div>
                    <dl className="mt-3 grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
                      <dt className="text-slate-400">Kâr payı</dt>
                      <dd className="text-slate-700">{KarPayiEtiket(k)}</dd>
                      <dt className="text-slate-400">Vade</dt>
                      <dd className="text-slate-700">
                        {k.vade_max_ay ? ay(k.vade_max_ay) : "Belirtilmemiş"}
                      </dd>
                      <dt className="text-slate-400">Finansman tutarı</dt>
                      <dd className="text-slate-700">
                        {k.finansman_tutari_max ? `${paraTL(k.finansman_tutari_max)}'ye kadar` : "Belirtilmemiş"}
                      </dd>
                    </dl>
                  </Kart>
                </Link>
              ))}
            </div>
          )}

          {veri.toplam_sayfa > 1 && (
            <div className="flex items-center justify-center gap-3 pt-2">
              <Buton tur="ikincil" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                Önceki
              </Buton>
              <span className="text-sm text-slate-500">
                Sayfa {veri.page} / {veri.toplam_sayfa}
              </span>
              <Buton
                tur="ikincil"
                disabled={page >= veri.toplam_sayfa}
                onClick={() => setPage((p) => p + 1)}
              >
                Sonraki
              </Buton>
            </div>
          )}
        </>
      )}
    </div>
  );
}
