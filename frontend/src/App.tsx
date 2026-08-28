import { NavLink, Route, Routes } from "react-router-dom";
import AnaSayfa from "./pages/AnaSayfa";
import Kampanyalar from "./pages/Kampanyalar";
import KampanyaDetayi from "./pages/KampanyaDetayi";
import Hesaplama from "./pages/Hesaplama";
import Karsilastirma from "./pages/Karsilastirma";
import Asistan from "./pages/Asistan";

const NAV = [
  { yol: "/", ad: "Ana Sayfa", tam: true },
  { yol: "/kampanyalar", ad: "Finansman & Kampanyalar" },
  { yol: "/hesaplama", ad: "Finansman Hesaplama" },
  { yol: "/karsilastirma", ad: "Karşılaştırma" },
  { yol: "/asistan", ad: "Asistan" },
];

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-4">
          <div className="flex h-16 items-center justify-between">
            <NavLink to="/" className="flex items-center gap-2">
              <span className="grid h-9 w-9 place-items-center rounded-lg bg-brand-600 text-white font-bold">
                KB
              </span>
              <span className="font-semibold text-slate-800 hidden sm:block">
                Katılım Bankacılığı Platformu
              </span>
            </NavLink>
            <nav className="flex items-center gap-1 overflow-x-auto">
              {NAV.map((n) => (
                <NavLink
                  key={n.yol}
                  to={n.yol}
                  end={n.tam}
                  className={({ isActive }) =>
                    `whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium transition ${
                      isActive
                        ? "bg-brand-50 text-brand-700"
                        : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                    }`
                  }
                >
                  {n.ad}
                </NavLink>
              ))}
            </nav>
          </div>
        </div>
      </header>

      <main className="flex-1">
        <div className="mx-auto max-w-6xl px-4 py-8">
          <Routes>
            <Route path="/" element={<AnaSayfa />} />
            <Route path="/kampanyalar" element={<Kampanyalar />} />
            <Route path="/kampanya/:id" element={<KampanyaDetayi />} />
            <Route path="/hesaplama" element={<Hesaplama />} />
            <Route path="/karsilastirma" element={<Karsilastirma />} />
            <Route path="/asistan" element={<Asistan />} />
          </Routes>
        </div>
      </main>

      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-4 py-6 text-xs text-slate-400">
          Bu platform bilgilendirme amaçlıdır. Finansal kararlar için ilgili bankanın resmi
          kaynaklarını esas alın. Oranlar ve koşullar kaynak verinin alındığı tarihe aittir.
        </div>
      </footer>
    </div>
  );
}
