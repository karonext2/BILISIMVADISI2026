import type { ReactNode } from "react";

export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 text-slate-500 py-8 justify-center">
      <span className="h-4 w-4 rounded-full border-2 border-slate-300 border-t-brand-600 animate-spin" />
      <span className="text-sm">{label ?? "Yükleniyor…"}</span>
    </div>
  );
}

export function HataKutusu({ mesaj }: { mesaj: string }) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 text-red-800 px-4 py-3 text-sm">
      {mesaj}
    </div>
  );
}

export function BosDurum({ mesaj }: { mesaj: string }) {
  return (
    <div className="rounded-lg border border-dashed border-slate-300 bg-white px-4 py-10 text-center text-slate-500 text-sm">
      {mesaj}
    </div>
  );
}

export function Kart({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`rounded-xl border border-slate-200 bg-white shadow-sm ${className}`}>
      {children}
    </div>
  );
}

export function Rozet({
  children,
  renk = "slate",
}: {
  children: ReactNode;
  renk?: "slate" | "yesil" | "sari" | "mavi" | "kirmizi";
}) {
  const renkler: Record<string, string> = {
    slate: "bg-slate-100 text-slate-700",
    yesil: "bg-emerald-100 text-emerald-800",
    sari: "bg-amber-100 text-amber-800",
    mavi: "bg-sky-100 text-sky-800",
    kirmizi: "bg-red-100 text-red-800",
  };
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${renkler[renk]}`}>
      {children}
    </span>
  );
}

export function Buton({
  children,
  onClick,
  tur = "birincil",
  disabled,
  type = "button",
  className = "",
}: {
  children: ReactNode;
  onClick?: () => void;
  tur?: "birincil" | "ikincil" | "sade";
  disabled?: boolean;
  type?: "button" | "submit";
  className?: string;
}) {
  const stiller: Record<string, string> = {
    birincil: "bg-brand-600 text-white hover:bg-brand-700 disabled:opacity-50",
    ikincil: "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50",
    sade: "text-brand-700 hover:underline",
  };
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium transition ${stiller[tur]} ${className}`}
    >
      {children}
    </button>
  );
}

export function TahminiUyari({ aciklama }: { aciklama: string }) {
  return (
    <div className="rounded-lg border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      <div className="font-semibold mb-1">Tahmini Hesaplama — bankanın resmi teklifi değildir</div>
      <p className="text-amber-800 leading-relaxed">{aciklama}</p>
    </div>
  );
}

export function OranBar({
  veriler,
  toplam,
}: {
  veriler: { etiket: string; adet: number }[];
  toplam: number;
}) {
  const enBuyuk = Math.max(...veriler.map((v) => v.adet), 1);
  return (
    <div className="space-y-2">
      {veriler.map((v) => (
        <div key={v.etiket} className="flex items-center gap-3 text-sm">
          <span className="w-40 shrink-0 truncate text-slate-600" title={v.etiket}>
            {v.etiket}
          </span>
          <div className="flex-1 h-2.5 rounded-full bg-slate-100 overflow-hidden">
            <div
              className="h-full rounded-full bg-brand-500"
              style={{ width: `${(v.adet / enBuyuk) * 100}%` }}
            />
          </div>
          <span className="w-10 text-right tabular-nums text-slate-500">{v.adet}</span>
        </div>
      ))}
      <div className="text-xs text-slate-400 pt-1">Toplam {toplam} kayıt</div>
    </div>
  );
}
