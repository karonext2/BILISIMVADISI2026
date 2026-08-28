import { useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api, ApiHata } from "../api/client";
import { Buton, HataKutusu, Kart, Spinner, TahminiUyari } from "../components/ui";
import { paraTL } from "../lib/format";
import type { HesaplamaSonucu } from "../api/types";

function AlanKaydirici({
  etiket,
  deger,
  ayarla,
  min,
  max,
  adim,
  birim,
  bicim,
}: {
  etiket: string;
  deger: number;
  ayarla: (v: number) => void;
  min: number;
  max: number;
  adim: number;
  birim: string;
  bicim?: (v: number) => string;
}) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between">
        <label className="text-sm font-medium text-slate-600">{etiket}</label>
        <div className="flex items-center gap-1">
          <input
            type="number"
            className="w-32 rounded-lg border border-slate-300 px-2 py-1 text-right text-sm"
            value={deger}
            min={min}
            max={max}
            step={adim}
            onChange={(e) => ayarla(Number(e.target.value))}
          />
          <span className="text-sm text-slate-400">{birim}</span>
        </div>
      </div>
      <input
        type="range"
        className="w-full"
        min={min}
        max={max}
        step={adim}
        value={Math.min(Math.max(deger, min), max)}
        onChange={(e) => ayarla(Number(e.target.value))}
      />
      <div className="mt-1 flex justify-between text-xs text-slate-400">
        <span>{bicim ? bicim(min) : `${min} ${birim}`}</span>
        <span>{bicim ? bicim(max) : `${max} ${birim}`}</span>
      </div>
    </div>
  );
}

export default function Hesaplama() {
  const [sp] = useSearchParams();

  const [tutar, setTutar] = useState(Number(sp.get("tutar")) || 500_000);
  const [vade, setVade] = useState(Number(sp.get("vade")) || 60);
  const [oran, setOran] = useState(Number(sp.get("oran")) || 2.99);
  const [periyot, setPeriyot] = useState<"aylik" | "yillik">(
    sp.get("periyot") === "yillik" ? "yillik" : "aylik"
  );
  const [tahsisOrani, setTahsisOrani] = useState(0);
  const kaynakId = sp.get("record_id");

  const [sonuc, setSonuc] = useState<HesaplamaSonucu | null>(null);
  const [yukleniyor, setYukleniyor] = useState(false);
  const [hata, setHata] = useState<string | null>(null);
  const [planAcik, setPlanAcik] = useState(false);

  const onDolduruldu = useMemo(
    () => Boolean(sp.get("tutar") || sp.get("vade") || sp.get("oran")),
    [sp]
  );

  async function hesapla() {
    setYukleniyor(true);
    setHata(null);
    try {
      const r = await api.calculate({
        finansman_tutari: tutar,
        vade_ay: Math.round(vade),
        kar_payi_orani: oran,
        oran_periyodu: periyot,
        tahsis_ucreti_orani: tahsisOrani || null,
        odeme_plani_dahil_et: true,
        kaynak_record_id: kaynakId,
      });
      setSonuc(r);
    } catch (e) {
      setHata(e instanceof ApiHata ? e.message : "Hesaplama yapılamadı.");
      setSonuc(null);
    } finally {
      setYukleniyor(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Finansman Hesaplama</h1>
        <p className="text-sm text-slate-500">
          Değerleri elle girin veya kaydırıcıları kullanın. Sonuç, girdiğiniz parametrelere göre
          tahmini olarak hesaplanır.
        </p>
      </div>

      {onDolduruldu && (
        <div className="rounded-lg border border-sky-200 bg-sky-50 px-4 py-2 text-sm text-sky-800">
          Alanlar seçtiğiniz kampanyanın verileriyle ön-dolduruldu. İstediğiniz gibi
          değiştirebilirsiniz.
        </div>
      )}

      <Kart className="space-y-6 p-6">
        <AlanKaydirici
          etiket="Finansman Tutarı"
          deger={tutar}
          ayarla={setTutar}
          min={10_000}
          max={5_000_000}
          adim={10_000}
          birim="TL"
          bicim={(v) => paraTL(v)}
        />
        <AlanKaydirici
          etiket="Vade"
          deger={vade}
          ayarla={setVade}
          min={1}
          max={120}
          adim={1}
          birim="ay"
        />
        <div>
          <div className="mb-1 flex items-center justify-between">
            <label className="text-sm font-medium text-slate-600">Kâr Payı Oranı</label>
            <div className="flex items-center gap-2">
              <div className="flex overflow-hidden rounded-lg border border-slate-300 text-xs">
                {(["aylik", "yillik"] as const).map((p) => (
                  <button
                    key={p}
                    onClick={() => setPeriyot(p)}
                    className={`px-2.5 py-1 ${periyot === p ? "bg-brand-600 text-white" : "bg-white text-slate-600"}`}
                  >
                    {p === "aylik" ? "Aylık" : "Yıllık"}
                  </button>
                ))}
              </div>
              <input
                type="number"
                className="w-24 rounded-lg border border-slate-300 px-2 py-1 text-right text-sm"
                value={oran}
                min={0}
                max={100}
                step={0.01}
                onChange={(e) => setOran(Number(e.target.value))}
              />
              <span className="text-sm text-slate-400">%</span>
            </div>
          </div>
          <input
            type="range"
            className="w-full"
            min={0}
            max={periyot === "aylik" ? 10 : 100}
            step={0.01}
            value={Math.min(oran, periyot === "aylik" ? 10 : 100)}
            onChange={(e) => setOran(Number(e.target.value))}
          />
        </div>

        <AlanKaydirici
          etiket="Tahsis Ücreti Oranı (opsiyonel)"
          deger={tahsisOrani}
          ayarla={setTahsisOrani}
          min={0}
          max={5}
          adim={0.05}
          birim="%"
        />

        <Buton type="button" onClick={hesapla} disabled={yukleniyor} className="w-full sm:w-auto">
          {yukleniyor ? "Hesaplanıyor…" : "Hesapla"}
        </Buton>
      </Kart>

      {yukleniyor && <Spinner label="Hesaplanıyor…" />}
      {hata && <HataKutusu mesaj={hata} />}

      {sonuc && !yukleniyor && (
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-3">
            <Kart className="p-4">
              <div className="text-xs uppercase tracking-wide text-slate-400">Tahmini Aylık Ödeme</div>
              <div className="mt-1 text-2xl font-bold text-brand-700">
                {paraTL(sonuc.aylik_odeme, true)}
              </div>
            </Kart>
            <Kart className="p-4">
              <div className="text-xs uppercase tracking-wide text-slate-400">Toplam Geri Ödeme</div>
              <div className="mt-1 text-2xl font-bold text-slate-800">
                {paraTL(sonuc.toplam_odeme, true)}
              </div>
            </Kart>
            <Kart className="p-4">
              <div className="text-xs uppercase tracking-wide text-slate-400">Toplam Kâr Payı</div>
              <div className="mt-1 text-2xl font-bold text-slate-800">
                {paraTL(sonuc.toplam_kar_payi, true)}
              </div>
            </Kart>
          </div>

          {sonuc.tahsis_ucreti_tl > 0 && (
            <div className="text-sm text-slate-500">
              Tahsis ücreti dahil toplam maliyet:{" "}
              <span className="font-medium text-slate-700">{paraTL(sonuc.toplam_maliyet, true)}</span>
            </div>
          )}

          <TahminiUyari aciklama={sonuc.aciklama} />

          {sonuc.odeme_plani && (
            <Kart className="overflow-hidden">
              <button
                onClick={() => setPlanAcik((a) => !a)}
                className="flex w-full items-center justify-between px-5 py-3 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                Ödeme Planı ({sonuc.odeme_plani.length} taksit)
                <span>{planAcik ? "−" : "+"}</span>
              </button>
              {planAcik && (
                <div className="max-h-96 overflow-auto border-t border-slate-100">
                  <table className="w-full text-sm">
                    <thead className="sticky top-0 bg-slate-50 text-left text-xs uppercase text-slate-400">
                      <tr>
                        <th className="px-4 py-2">Taksit</th>
                        <th className="px-4 py-2 text-right">Tutar</th>
                        <th className="px-4 py-2 text-right">Kâr payı</th>
                        <th className="px-4 py-2 text-right">Anapara</th>
                        <th className="px-4 py-2 text-right">Kalan</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sonuc.odeme_plani.map((t) => (
                        <tr key={t.taksit_no} className="border-t border-slate-50">
                          <td className="px-4 py-1.5">{t.taksit_no}</td>
                          <td className="px-4 py-1.5 text-right">{paraTL(t.taksit_tutari, true)}</td>
                          <td className="px-4 py-1.5 text-right text-slate-500">
                            {paraTL(t.kar_payi, true)}
                          </td>
                          <td className="px-4 py-1.5 text-right text-slate-500">
                            {paraTL(t.anapara, true)}
                          </td>
                          <td className="px-4 py-1.5 text-right">{paraTL(t.kalan_anapara, true)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Kart>
          )}
        </div>
      )}
    </div>
  );
}
