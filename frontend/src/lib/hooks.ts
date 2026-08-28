import { useCallback, useEffect, useRef, useState } from "react";
import { ApiHata } from "../api/client";

export function useApi<T>(fn: () => Promise<T>, deps: unknown[] = []) {
  const [veri, setVeri] = useState<T | null>(null);
  const [yukleniyor, setYukleniyor] = useState(true);
  const [hata, setHata] = useState<string | null>(null);
  const fnRef = useRef(fn);
  fnRef.current = fn;

  const calistir = useCallback(() => {
    setYukleniyor(true);
    setHata(null);
    fnRef
      .current()
      .then(setVeri)
      .catch((e: unknown) => setHata(e instanceof ApiHata ? e.message : "Bir sorun oluştu."))
      .finally(() => setYukleniyor(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(calistir, [calistir]);
  return { veri, yukleniyor, hata, yenile: calistir };
}
