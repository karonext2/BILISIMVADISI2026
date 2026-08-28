import type {
  BankaListesi,
  ChatCevap,
  FiltreDegerleri,
  HesaplamaSonucu,
  Istatistik,
  KampanyaDetay,
  KampanyaListesi,
  KarsilastirmaSonucu,
} from "./types";

const BASE = "/api/v1";

export class ApiHata extends Error {
  errorId?: string;
  constructor(mesaj: string, errorId?: string) {
    super(mesaj);
    this.errorId = errorId;
  }
}

async function istek<T>(yol: string, opts?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE}${yol}`, {
      headers: { "Content-Type": "application/json" },
      ...opts,
    });
  } catch {
    throw new ApiHata("Sunucuya ulaşılamıyor. İnternet bağlantınızı kontrol edin.");
  }
  const govde = await res.json().catch(() => null);
  if (!res.ok) {
    const mesaj =
      (govde && (govde.mesaj as string)) ||
      "İşlem sırasında bir sorun oluştu. Lütfen tekrar deneyin.";
    throw new ApiHata(mesaj, govde?.error_id);
  }
  return govde as T;
}

export const api = {
  banks: () => istek<BankaListesi>("/banks"),
  filters: () => istek<FiltreDegerleri>("/filters"),
  stats: () => istek<Istatistik>("/stats"),

  campaigns: (params: Record<string, string | number | boolean | string[] | undefined>) => {
    const q = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) {
      if (v === undefined || v === "" || v === null) continue;
      if (Array.isArray(v)) v.forEach((x) => q.append(k, String(x)));
      else q.append(k, String(v));
    }
    return istek<KampanyaListesi>(`/campaigns?${q.toString()}`);
  },

  campaign: (id: string) => istek<KampanyaDetay>(`/campaigns/${encodeURIComponent(id)}`),

  calculate: (body: {
    finansman_tutari: number;
    vade_ay: number;
    kar_payi_orani: number;
    oran_periyodu: "aylik" | "yillik";
    tahsis_ucreti_tl?: number | null;
    tahsis_ucreti_orani?: number | null;
    odeme_plani_dahil_et?: boolean;
    kaynak_record_id?: string | null;
  }) => istek<HesaplamaSonucu>("/calculate", { method: "POST", body: JSON.stringify(body) }),

  compare: (body: { record_idler: string[]; urun_ailesi?: string | null }) =>
    istek<KarsilastirmaSonucu>("/compare", { method: "POST", body: JSON.stringify(body) }),

  chat: (body: {
    soru: string;
    top_k?: number;
    bankalar?: string[] | null;
    urun_ailesi?: string | null;
    kayit_idleri?: string[] | null;
  }) => istek<ChatCevap>("/chat", { method: "POST", body: JSON.stringify(body) }),
};
