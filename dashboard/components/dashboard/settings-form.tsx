/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║                                                                  ║
 * ║   ░█▀▀░█▀█░█▀▄░█▀▀░█░█   ░█▀▄░█▀▀░█░█░█▀▀                     ║
 * ║   ░█░░░█░█░█░█░█▀▀░▄▀▄   ░█░█░█▀▀░▀▄▀░▀▀█                     ║
 * ║   ░▀▀▀░▀▀▀░▀▀░░▀▀▀░▀░▀   ░▀▀░░▀▀▀░░▀░░▀▀▀                     ║
 * ║                                                                  ║
 * ║           © 2026 CodeX Devs — All Rights Reserved               ║
 * ║                                                                  ║
 * ║   discord  ──  https://discord.gg/codexdev                      ║
 * ║   youtube  ──  https://youtube.com/@CodeXDevs                   ║
 * ║   github   ──  https://github.com/RayExo                        ║
 * ║                                                                  ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

"use client";

import React, { useState } from "react";
import { 
  Save, 
  RefreshCcw, 
  Command,
  Info
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface SettingsFormProps {
  initialPrefix: string;
  guildId: string;
}

export function SettingsForm({ initialPrefix, guildId }: SettingsFormProps) {
  const [prefix, setPrefix] = useState(initialPrefix);
  const [saving, setSaving] = useState(false);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prefix || prefix.length > 10) {
      toast.error("El prefijo debe tener entre 1 y 10 caracteres.");
      return;
    }

    setSaving(true);
    const promise = api.updatePrefix(guildId, prefix);

    toast.promise(promise, {
      loading: 'Actualizando el prefijo...',
      success: '¡Prefijo actualizado correctamente!',
      error: (err) => err.message || 'No se pudo actualizar el prefijo',
    });

    try {
      await promise;
    } catch (err: any) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="lg:col-span-2 space-y-6">
        <div className="bg-[#141B2D] border border-slate-800 rounded-3xl overflow-hidden shadow-xl shadow-black/20">
          <div className="p-8 space-y-6">
            <form onSubmit={handleSave} className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-black uppercase text-slate-500 tracking-widest flex items-center gap-2">
                  <Command className="h-4 w-4" />
                  Prefijo de comandos
                </label>
                <div className="relative group">
                  <Input 
                    value={prefix}
                    onChange={(e) => setPrefix(e.target.value)}
                    placeholder="p. ej. !, ?, >>"
                    maxLength={10}
                    className="text-lg font-bold pr-20 py-7"
                  />
                  <div className="absolute right-4 top-1/2 -translate-y-1/2 text-xs font-mono text-slate-600 group-focus-within:text-primary transition-colors">
                    {prefix.length}/10
                  </div>
                </div>
                <p className="text-xs text-slate-500 italic">Este carácter activa los comandos del bot (p. ej. {prefix || ">"}help)</p>
              </div>

              <Button 
                type="submit" 
                disabled={saving || !prefix}
                className="w-full h-14 text-base font-bold gap-2 shadow-primary/20"
              >
                {saving ? <RefreshCcw className="h-5 w-5 animate-spin" /> : <Save className="h-5 w-5" />}
                {saving ? "Guardando cambios..." : "Guardar configuración"}
              </Button>
            </form>
          </div>
          
          <div className="bg-slate-800/30 px-8 py-4 border-t border-slate-800 flex items-center justify-between">
             <span className="text-xs text-slate-500 font-medium">Última sincronización: hace un momento</span>
             <button className="text-xs text-primary hover:underline font-bold">Actualizar caché</button>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <div className="bg-[#141B2D] border border-slate-800 rounded-3xl p-6 relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 opacity-[0.03] group-hover:scale-110 transition-transform">
            <Info className="h-32 w-32 text-white" />
          </div>
          <h3 className="text-sm font-black uppercase text-slate-500 tracking-widest mb-4 flex items-center gap-2">
            <Info className="h-4 w-4" />
            Información
          </h3>
          <div className="space-y-4 text-sm leading-relaxed text-slate-400">
            <p>El <span className="text-white font-bold italic">Prefijo</span> es un identificador único que le indica al bot que procese el texto como un comando.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
