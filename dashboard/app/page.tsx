"use client";

import Link from "next/link";
import { signIn } from "next-auth/react";
import {
  ShieldAlert, ShieldCheck, Gavel, TrendingUp, Ticket, HandMetal, ScrollText, Mic2,
  UserPlus, Link2, SmilePlus, MailOpen, BadgeCheck, Crown, Users, ArrowRight, Check,
} from "lucide-react";

const login = () => signIn("discord", { callbackUrl: "/dashboard" });
const invite = process.env.NEXT_PUBLIC_INVITE_URL || "/dashboard";
const support = process.env.NEXT_PUBLIC_SUPPORT_URL || "#";

const modules = [
  { n: "Anti-Nuke", i: ShieldAlert }, { n: "Automod", i: Gavel }, { n: "Niveles", i: TrendingUp },
  { n: "Tickets", i: Ticket }, { n: "Bienvenida", i: HandMetal }, { n: "Logs", i: ScrollText },
  { n: "Voces temporales", i: Mic2 }, { n: "Autorole", i: UserPlus }, { n: "Roles por reacción", i: SmilePlus },
  { n: "Verificación", i: BadgeCheck }, { n: "Roles vanity", i: Crown }, { n: "Roles propios", i: Users },
  { n: "Invitaciones", i: Link2 }, { n: "DM de entrada", i: MailOpen },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen text-[#fbf1e4]">
      {/* Navegación */}
      <header className="fixed top-0 inset-x-0 z-50 border-b border-white/[0.06] bg-[#150c06]/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-5">
          <Link href="/" className="flex items-center gap-3">
            <img src="/logo.png" alt="" className="h-9 w-9 rounded-lg" />
            <span className="font-outfit text-xl font-extrabold tracking-tight">Coddy</span>
          </Link>
          <nav className="hidden items-center gap-8 text-sm font-medium text-slate-300 md:flex">
            <a href="#modulos" className="hover:text-orange-400">Módulos</a>
            <a href="#panel" className="hover:text-orange-400">Panel</a>
            <a href="#empezar" className="hover:text-orange-400">Empezar</a>
            <Link href="/docs" className="hover:text-orange-400">Docs</Link>
          </nav>
          <button onClick={login} className="rounded-full coddy-gradient px-5 py-2 text-sm font-bold text-[#1d0e04] shadow-lg shadow-orange-500/20 transition hover:brightness-110">
            Entrar al panel
          </button>
        </div>
      </header>

      {/* Hero */}
      <section className="relative mx-auto grid max-w-6xl items-center gap-10 px-5 pb-24 pt-36 lg:grid-cols-[1.15fr_.85fr]">
        <div>
          <h1 className="hero-rise font-outfit text-5xl font-extrabold leading-[1.02] tracking-tight text-balance sm:text-7xl">
            Un bot que cuida tu servidor mientras tú lo haces crecer.
          </h1>
          <p className="hero-rise-2 mt-6 max-w-xl text-lg leading-relaxed text-slate-300">
            Coddy junta moderación, niveles, tickets y bienvenidas en un solo bot, y lo controlas todo desde un panel web sin escribir comandos.
          </p>
          <div className="hero-rise-3 mt-9 flex flex-wrap items-center gap-4">
            <a href={invite} className="inline-flex items-center gap-2 rounded-full coddy-gradient px-7 py-3.5 font-bold text-[#1d0e04] shadow-xl shadow-orange-500/25 transition hover:-translate-y-0.5">
              Añadir a Discord <ArrowRight className="h-4 w-4" />
            </a>
            <button onClick={login} className="rounded-full border border-white/15 px-7 py-3.5 font-semibold text-slate-100 transition hover:border-orange-400/60 hover:bg-white/[0.04]">
              Abrir el panel
            </button>
          </div>
        </div>

        <div className="relative mx-auto aspect-square w-full max-w-md">
          <div className="halftone absolute inset-0 rounded-[3rem] opacity-40 [mask-image:radial-gradient(circle,black_30%,transparent_70%)]" />
          <div className="absolute inset-8 rounded-full bg-orange-500/25 blur-[90px]" />
          <img src="/logo.png" alt="Logo de Coddy" className="logo-bob relative h-full w-full rounded-[3rem] object-cover shadow-2xl shadow-orange-900/50 ring-1 ring-white/10" />
        </div>
      </section>

      {/* Módulos: bento con jerarquía real */}
      <section id="modulos" className="mx-auto max-w-6xl px-5 py-20">
        <h2 className="font-outfit text-4xl font-extrabold tracking-tight sm:text-5xl">Todo lo que tu comunidad necesita</h2>
        <p className="mt-3 max-w-xl text-slate-300">Cada módulo se activa y se ajusta desde el panel, servidor por servidor.</p>

        <div className="mt-12 grid gap-4 md:grid-cols-6">
          <article className="relative overflow-hidden rounded-[2rem] bg-gradient-to-br from-orange-500 to-orange-700 p-8 text-[#1d0e04] md:col-span-4 md:row-span-2">
            <div className="halftone absolute inset-0 opacity-30" />
            <ShieldAlert className="relative h-10 w-10" />
            <h3 className="relative mt-24 font-outfit text-4xl font-extrabold">Anti-Nuke</h3>
            <p className="relative mt-3 max-w-md font-medium leading-relaxed">
              Si alguien borra canales, banea en masa o toca roles sin permiso, Coddy actúa antes de que el daño sea irreversible y te lo registra.
            </p>
          </article>

          <article className="rounded-[2rem] border border-white/10 bg-white/[0.03] p-6 md:col-span-2">
            <Gavel className="h-7 w-7 text-orange-400" />
            <h3 className="mt-5 font-outfit text-2xl font-bold">Automod</h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-300">Filtra spam, enlaces e insultos con reglas que tú defines.</p>
          </article>

          <article className="relative overflow-hidden rounded-[2rem] bg-[#d6de3a] p-6 text-[#1f2204] md:col-span-2">
            <div className="halftone-lime absolute inset-0 opacity-30" />
            <TrendingUp className="relative h-7 w-7" />
            <h3 className="relative mt-5 font-outfit text-2xl font-bold">Niveles</h3>
            <p className="relative mt-2 text-sm font-medium leading-relaxed">XP, ranking y roles por nivel para premiar a los más activos.</p>
          </article>

          <article className="rounded-[2rem] border border-white/10 bg-white/[0.03] p-6 md:col-span-3">
            <Ticket className="h-7 w-7 text-orange-400" />
            <h3 className="mt-5 font-outfit text-2xl font-bold">Tickets</h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-300">Paneles de soporte con categorías, transcripciones y roles de staff.</p>
          </article>

          <article className="rounded-[2rem] border border-white/10 bg-white/[0.03] p-6 md:col-span-3">
            <HandMetal className="h-7 w-7 text-lime" />
            <h3 className="mt-5 font-outfit text-2xl font-bold">Bienvenidas</h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-300">Mensajes de entrada y despedida con tu propio estilo, más autorole y verificación.</p>
          </article>
        </div>

        <ul className="mt-10 flex flex-wrap gap-2.5">
          {modules.map(({ n, i: Icon }) => (
            <li key={n} className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-4 py-2 text-sm text-slate-200">
              <Icon className="h-4 w-4 text-orange-400" /> {n}
            </li>
          ))}
        </ul>
      </section>

      {/* Vista previa del panel */}
      <section id="panel" className="mx-auto max-w-6xl px-5 py-20">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <div>
            <h2 className="font-outfit text-4xl font-extrabold tracking-tight sm:text-5xl">Cambia un ajuste y listo</h2>
            <p className="mt-4 max-w-md leading-relaxed text-slate-300">
              Elige tu servidor, abre un módulo y activa lo que necesites. Los cambios se aplican en el bot al guardar, sin reiniciar nada.
            </p>
            <ul className="mt-6 space-y-3 text-slate-200">
              {["Inicio de sesión con Discord", "Solo ves los servidores donde eres administrador", "Un formulario claro por cada módulo"].map((t) => (
                <li key={t} className="flex items-center gap-3"><Check className="h-5 w-5 text-lime" /> {t}</li>
              ))}
            </ul>
          </div>

          <div className="rounded-[2rem] border border-white/10 bg-[#1c110a] p-5 shadow-2xl shadow-black/50">
            <div className="flex items-center gap-2 border-b border-white/10 pb-4">
              <span className="h-3 w-3 rounded-full bg-orange-500" /><span className="h-3 w-3 rounded-full bg-[#d6de3a]" /><span className="h-3 w-3 rounded-full bg-slate-600" />
              <span className="ml-3 text-sm text-slate-400">Mi servidor / Seguridad</span>
            </div>
            {[
              ["Anti-Nuke", "Protege canales, roles y baneos masivos", true],
              ["Automod", "Filtra spam, enlaces e insultos", true],
              ["Verificación", "Pide confirmar a los nuevos miembros", false],
            ].map(([t, d, on]) => (
              <div key={t as string} className="flex items-center justify-between gap-4 border-b border-white/[0.06] py-4 last:border-0">
                <div>
                  <p className="font-semibold">{t}</p>
                  <p className="text-sm text-slate-400">{d}</p>
                </div>
                <span className={`flex h-7 w-12 shrink-0 items-center rounded-full p-1 ${on ? "bg-orange-500 justify-end" : "bg-slate-700 justify-start"}`}>
                  <span className="h-5 w-5 rounded-full bg-white" />
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Empezar: secuencia real */}
      <section id="empezar" className="mx-auto max-w-6xl px-5 py-20">
        <h2 className="font-outfit text-4xl font-extrabold tracking-tight sm:text-5xl">Listo en tres pasos</h2>
        <ol className="mt-12 grid gap-6 md:grid-cols-3">
          {[
            ["Invita a Coddy", "Añádelo a tu servidor con los permisos que te pide."],
            ["Entra con Discord", "Inicia sesión en el panel y elige tu servidor."],
            ["Activa lo que necesites", "Configura cada módulo y guarda."],
          ].map(([t, d], k) => (
            <li key={t} className="flex gap-4">
              <span className="coddy-gradient flex h-11 w-11 shrink-0 items-center justify-center rounded-xl font-outfit text-xl font-extrabold text-[#1d0e04]">{k + 1}</span>
              <div>
                <h3 className="font-outfit text-xl font-bold">{t}</h3>
                <p className="mt-1 text-slate-300">{d}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      {/* Cierre */}
      <section className="mx-auto max-w-6xl px-5 pb-24">
        <div className="relative overflow-hidden rounded-[2.5rem] bg-gradient-to-br from-orange-500 via-orange-600 to-orange-800 px-8 py-16 text-center text-[#1d0e04] sm:px-16">
          <div className="halftone absolute inset-0 opacity-25" />
          <h2 className="relative font-outfit text-4xl font-extrabold tracking-tight text-balance sm:text-5xl">Dale a tu servidor el cuidado que merece</h2>
          <div className="relative mt-8 flex flex-wrap justify-center gap-4">
            <a href={invite} className="rounded-full bg-[#150c06] px-8 py-3.5 font-bold text-orange-100 transition hover:-translate-y-0.5">Añadir Coddy</a>
            <a href={support} className="rounded-full border-2 border-[#150c06]/60 px-8 py-3.5 font-bold transition hover:bg-[#150c06]/10">Unirme al soporte</a>
          </div>
        </div>
      </section>

      <footer className="border-t border-white/[0.06] py-10">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-5 text-sm text-slate-400">
          <span className="flex items-center gap-2"><img src="/logo.png" alt="" className="h-6 w-6 rounded" /> © 2026 Coddy</span>
          <nav className="flex gap-6">
            <Link href="/docs" className="hover:text-orange-400">Docs</Link>
            <Link href="/privacy" className="hover:text-orange-400">Privacidad</Link>
            <Link href="/terms" className="hover:text-orange-400">Términos</Link>
          </nav>
        </div>
      </footer>
    </div>
  );
}
