import { useState } from "react";
import { api, ApiHata } from "../api/client";
import { Buton, HataKutusu, Kart, Rozet, Spinner } from "../components/ui";
import { aileEtiket, yuzde } from "../lib/format";
import type { KampanyaOzet, KarsilastirmaSonucu } from "../api/types";

export default function Karsilastirma() {
  const [q, setQ] = useState("");
  const [aramaSonuc, setAramaSonuc] = useState<KampanyaOzet[]>([]);
  const [seciliMap, setSeciliMap] = useState<Record<string, KampanyaOzet>>({});
  const secili = Object.values(seciliMap);

  const [sonuc, setSonuc] = useState<KarsilastirmaSonucu | null>(null);
  const [yukleniyor, setYukleniyor] = useState(false);
  const [hata, setHata] = useState<string | null>(null);

  async function ara() {
    if (q.trim().length < 2) return;
    setHata(null);
    try {
      const r = await api.campaigns({ q, size: 8, sort: "banka" });
      setAramaSonuc(r.items);
    } catch (e) {
      setHata(e instanceof ApiHata ? e.message : "Arama yapılamadı.");
    }
  }

  function ekle(k: KampanyaOzet) {
    if (secili.length >= 8) return;
    setSeciliMap((m) => ({ ...m, [k.record_id]: k }));
  }
  function cikar(id: string) {
    setSeciliMap((m) => {
      const n = { ...m };
      delete n[id];
      return n;
    });
  }

  async function karsilastir() {
    if (secili.length < 2) return;
    setYukleniyor(true);
    setHata(null);
    try {
      const r = await api.compare({ record_idler: secili.map((s) => s.record_id) });
      setSonuc(r);
    } catch (e) {
      setHata(e instanceof ApiHata ? e.message : "Karşılaştırma yapılamadı.");
      setSonuc(null);
    } finally {
      setYukleniyor(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Karşılaştırma</h1>
        <p className="text-sm text-slate-500">
          İki veya daha fazla ürün / kampanya seçin; kâr payı, vade, ücret ve ödül kriterlerine
          göre karşılaştırın.
        </p>
      </div>

      <Kart className="p-4 space-y-3">
        <div className="flex gap-2">
          <input
            className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="Ürün / kampanya ara (örn. konut finansmanı)"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && ara()}
          />
          <Buton tur="ikincil" onClick={ara}>
            Ara
          </Buton>
        </div>
        {aramaSonuc.length > 0 && (
          <div className="grid gap-2 sm:grid-cols-2">
            {aramaSonuc.map((k) => (
              <button
                key={k.record_id}
                onClick={() => ekle(k)}
                disabled={Boolean(seciliMap[k.record_id]) || secili.length >= 8}
                className="rounded-lg border border-slate-200 px-3 py-2 text-left text-sm hover:border-brand-300 disabled:opacity-40"
              >
                <div className="font-medium text-slate-800">{k.urun_adi ?? k.baslik}</div>
                <div className="text-xs text-slate-400">
                  {k.banka} · {aileEtiket(k.urun_ailesi)}
                </div>
              </button>
            ))}
          </div>
        )}
      </Kart>

      {secili.length > 0 && (
        <div className="flex flex-wrap items-center gap-2">
          {secili.map((s) => (
            <span
              key={s.record_id}
              className="inline-flex items-center gap-2 rounded-full bg-brand-50 px-3 py-1 text-sm text-brand-800"
            >
              {s.banka} — {s.urun_adi ?? s.baslik}
              <button onClick={() => cikar(s.record_id)} className="text-brand-500 hover:text-brand-800">
                ×
              </button>
            </span>
          ))}
          <Buton onClick={karsilastir} disabled={secili.length < 2 || yukleniyor}>
            Karşılaştır ({secili.length})
          </Buton>
        </div>
      )}

      {yukleniyor && <Spinner />}
      {hata && <HataKutusu mesaj={hata} />}

      {sonuc && (
        <div className="space-y-4">
          {sonuc.uyari && (
            <div className="rounded-lg border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900">
              {sonuc.uyari}
            </div>
          )}

          {sonuc.kriterler.length > 0 && (
            <Kart className="p-5">
              <h2 className="mb-3 font-semibold text-slate-800">Kriter Bazında Öne Çıkanlar</h2>
              <ul className="space-y-2">
                {sonuc.kriterler.map((kr) => (
                  <li key={kr.kriter} className="flex flex-wrap items-baseline gap-2 text-sm">
                    <Rozet renk="yesil">{kr.kriter}</Rozet>
                    <span className="text-slate-600">{kr.aciklama}</span>
                  </li>
                ))}
              </ul>
              <p className="mt-3 border-t border-slate-100 pt-3 text-sm text-slate-500">
                <span className="font-medium text-slate-700">Neden bu sonuç? </span>
                {sonuc.neden}
              </p>
            </Kart>
          )}

          <Kart className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase text-slate-400">
                <tr>
                  <th className="px-4 py-2">Kriter</th>
                  {secili.map((s) => (
                    <th key={s.record_id} className="px-4 py-2">
                      {s.banka}
                      <div className="font-normal normal-case text-slate-400">
                        {s.urun_adi ?? s.baslik}
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {(
                  [
                    ["Kâr payı", (r: Record<string, unknown>) => fmtOran(r)],
                    ["Vade", (r: Record<string, unknown>) => fmtVade(r)],
                    ["Tahsis ücreti", (r: Record<string, unknown>) => fmtTL(r["tahsis_ucreti_tl"])],
                    ["Ödül", (r: Record<string, unknown>) => fmtTL(r["odul_miktari_tl"])],
                    ["Finansman tutarı", (r: Record<string, unknown>) => fmtTL(r["finansman_tutari_max"])],
                  ] as const
                ).map(([ad, fn]) => (
                  <tr key={ad} className="border-t border-slate-100">
                    <td className="px-4 py-2 font-medium text-slate-600">{ad}</td>
                    {secili.map((s) => {
                      const r = sonuc.kayitlar.find((x) => x["record_id"] === s.record_id) ?? {};
                      return (
                        <td key={s.record_id} className="px-4 py-2 text-slate-800">
                          {fn(r)}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </Kart>
        </div>
      )}
    </div>
  );
}

function fmtOran(r: Record<string, unknown>): string {
  const mn = r["kar_payi_orani_min"] as number | null;
  const mx = r["kar_payi_orani_max"] as number | null;
  if (mn === null || mn === undefined) return "Belirtilmemiş";
  return mx && mx !== mn ? `${yuzde(mn)} – ${yuzde(mx)}` : yuzde(mn);
}
function fmtVade(r: Record<string, unknown>): string {
  const v = r["vade_max_ay"] as number | null;
  return v ? `${v} ay` : "Belirtilmemiş";
}
function fmtTL(v: unknown): string {
  if (typeof v !== "number") return "Belirtilmemiş";
  return new Intl.NumberFormat("tr-TR", { style: "currency", currency: "TRY", maximumFractionDigits: 0 }).format(v);
}
