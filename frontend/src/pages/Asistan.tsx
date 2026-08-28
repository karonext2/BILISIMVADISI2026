import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiHata } from "../api/client";
import { Kart } from "../components/ui";
import { paraTL } from "../lib/format";
import type { ChatCevap } from "../api/types";

interface Mesaj {
  rol: "kullanici" | "asistan";
  metin: string;
  cevap?: ChatCevap;
}

const KARSILAMA =
  "Merhaba, ben Katılım Bankacılığı Asistanınız. Finansman ve kampanyaları bulmanıza, incelemenize ve karşılaştırmanıza yardımcı olabilirim.";

const ORNEKLER = [
  "Hangi bankada konut finansmanı daha avantajlı?",
  "120 aya kadar finansman sunan bankalar hangileri?",
  "500.000 TL taşıt finansmanını 48 ayda %3,2 ile alırsam aylık ödemem ne olur?",
];

export default function Asistan() {
  const [mesajlar, setMesajlar] = useState<Mesaj[]>([{ rol: "asistan", metin: KARSILAMA }]);
  const [girdi, setGirdi] = useState("");
  const [yukleniyor, setYukleniyor] = useState(false);
  const altRef = useRef<HTMLDivElement>(null);

  async function gonder(soru: string) {
    const s = soru.trim();
    if (!s || yukleniyor) return;
    setMesajlar((m) => [...m, { rol: "kullanici", metin: s }]);
    setGirdi("");
    setYukleniyor(true);
    try {
      const cevap = await api.chat({ soru: s, top_k: 5 });
      setMesajlar((m) => [...m, { rol: "asistan", metin: cevap.yanit, cevap }]);
    } catch (e) {
      setMesajlar((m) => [
        ...m,
        {
          rol: "asistan",
          metin:
            e instanceof ApiHata
              ? e.message
              : "Şu anda yanıt veremiyorum. Lütfen biraz sonra tekrar deneyin.",
        },
      ]);
    } finally {
      setYukleniyor(false);
      setTimeout(() => altRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Katılım Bankacılığı Asistanı</h1>
        <p className="text-sm text-slate-500">
          Yanıtlar yalnızca platformdaki verilere dayanır ve kaynak gösterilir.
        </p>
      </div>

      <div className="space-y-3">
        {mesajlar.map((m, i) => (
          <div key={i} className={m.rol === "kullanici" ? "flex justify-end" : ""}>
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                m.rol === "kullanici"
                  ? "bg-brand-600 text-white"
                  : "border border-slate-200 bg-white text-slate-700"
              }`}
            >
              <p className="whitespace-pre-wrap">{m.metin}</p>

              {m.cevap?.hesaplama && (
                <div className="mt-3 rounded-lg border border-amber-300 bg-amber-50 p-3 text-amber-900">
                  <div className="font-semibold">Tahmini Hesaplama</div>
                  <div className="mt-1 grid grid-cols-2 gap-1 text-xs">
                    <span>Aylık ödeme</span>
                    <span className="text-right font-medium">
                      {paraTL(m.cevap.hesaplama.aylik_odeme, true)}
                    </span>
                    <span>Toplam ödeme</span>
                    <span className="text-right font-medium">
                      {paraTL(m.cevap.hesaplama.toplam_odeme, true)}
                    </span>
                    <span>Toplam kâr payı</span>
                    <span className="text-right font-medium">
                      {paraTL(m.cevap.hesaplama.toplam_kar_payi, true)}
                    </span>
                  </div>
                  <div className="mt-1 text-[11px] text-amber-700">
                    Bankanın resmi teklifi değildir.
                  </div>
                </div>
              )}

              {m.cevap?.uyari && (
                <p className="mt-2 text-xs text-slate-500">{m.cevap.uyari}</p>
              )}

              {m.cevap?.kaynaklar && m.cevap.kaynaklar.length > 0 && (
                <div className="mt-3 border-t border-slate-100 pt-2">
                  <div className="text-[11px] font-medium uppercase text-slate-400">Kaynaklar</div>
                  <ul className="mt-1 space-y-1">
                    {m.cevap.kaynaklar.map((k) => (
                      <li key={k.record_id} className="text-xs">
                        <Link
                          to={`/kampanya/${k.record_id}`}
                          className="text-brand-700 hover:underline"
                        >
                          {k.banka} — {k.urun_adi}
                        </Link>
                        {k.veri_tarihi && (
                          <span className="text-slate-400"> · veri: {k.veri_tarihi}</span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
        {yukleniyor && (
          <div className="text-sm text-slate-400">Asistan yanıt hazırlıyor…</div>
        )}
        <div ref={altRef} />
      </div>

      {mesajlar.length <= 1 && (
        <div className="flex flex-wrap gap-2">
          {ORNEKLER.map((o) => (
            <button
              key={o}
              onClick={() => gonder(o)}
              className="rounded-full border border-slate-300 px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-50"
            >
              {o}
            </button>
          ))}
        </div>
      )}

      <Kart className="sticky bottom-4 flex items-center gap-2 p-2">
        <input
          className="flex-1 rounded-lg px-3 py-2 text-sm outline-none"
          placeholder="Sorunuzu yazın…"
          value={girdi}
          onChange={(e) => setGirdi(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && gonder(girdi)}
        />
        <button
          onClick={() => gonder(girdi)}
          disabled={yukleniyor || !girdi.trim()}
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
        >
          Gönder
        </button>
      </Kart>
    </div>
  );
}
