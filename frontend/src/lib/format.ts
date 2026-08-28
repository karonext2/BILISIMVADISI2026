const tl = new Intl.NumberFormat("tr-TR", {
  style: "currency",
  currency: "TRY",
  maximumFractionDigits: 0,
});

const tlKurus = new Intl.NumberFormat("tr-TR", {
  style: "currency",
  currency: "TRY",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const sayi = new Intl.NumberFormat("tr-TR");

export function paraTL(v: number | null | undefined, kurus = false): string {
  if (v === null || v === undefined || Number.isNaN(v)) return "Belirtilmemiş";
  return (kurus ? tlKurus : tl).format(v);
}

export function yuzde(v: number | null | undefined): string {
  if (v === null || v === undefined || Number.isNaN(v)) return "Belirtilmemiş";
  return `%${v.toLocaleString("tr-TR", { maximumFractionDigits: 2 })}`;
}

export function ay(v: number | null | undefined): string {
  if (v === null || v === undefined) return "Belirtilmemiş";
  return `${v} ay`;
}

export function tamSayi(v: number | null | undefined): string {
  if (v === null || v === undefined) return "0";
  return sayi.format(v);
}

export function bosDegilse(v: string | null | undefined): string {
  return v && v.trim() ? v : "Belirtilmemiş";
}

export function tarih(iso: string | null | undefined): string {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleDateString("tr-TR", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });
  } catch {
    return iso;
  }
}

export const AILE_ETIKET: Record<string, string> = {
  finansman: "Finansman",
  mevduat: "Katılma Hesabı",
  kart: "Kart",
  yatirim: "Yatırım",
  diger: "Diğer",
};

export function aileEtiket(a: string | null | undefined): string {
  if (!a) return "Diğer";
  return AILE_ETIKET[a] ?? a;
}
