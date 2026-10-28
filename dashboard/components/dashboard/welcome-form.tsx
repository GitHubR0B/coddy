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
  MessageSquare,
  Type,
  LayoutTemplate,
  RefreshCcw
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { WelcomeConfig, DiscordChannel } from "@/types/api";

interface WelcomeFormProps {
  initialConfig: WelcomeConfig;
  channels: DiscordChannel[];
  guildId: string;
}

export function WelcomeForm({ initialConfig, channels, guildId }: WelcomeFormProps) {
  const [config, setConfig] = useState<WelcomeConfig>(initialConfig);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    const promise = api.updateWelcome(guildId, config);

    toast.promise(promise, {
      loading: 'Guardando la configuración de bienvenida...',
      success: '¡Configuración de bienvenida guardada correctamente!',
      error: 'No se pudo actualizar la configuración de bienvenida',
    });

    try {
      await promise;
    } catch (err: any) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const channelOptions = channels.map(c => ({
    value: c.id.toString(),
    label: `#${c.name}`
  }));

  const typeOptions = [
    { value: "simple", label: "Mensaje de texto simple" },
    { value: "embed", label: "Mensaje embed enriquecido" }
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="lg:col-span-2 space-y-6">
        <div className="bg-[#141B2D] border border-slate-800 rounded-3xl shadow-xl p-8 space-y-6">
          <div className="space-y-4">
            <div>
              <label className="text-xs font-black uppercase text-slate-500 tracking-widest pl-1">Tipo de respuesta</label>
              <Select 
                value={config.welcome_type || "simple"}
                onValueChange={(val) => setConfig({ ...config, welcome_type: val })}
                options={typeOptions}
                className="mt-2"
              />
            </div>

            <div>
              <label className="text-xs font-black uppercase text-slate-500 tracking-widest pl-1">Canal de bienvenida</label>
              <Select 
                value={config.channel_id || ""}
                onValueChange={(val) => setConfig({ ...config, channel_id: val })}
                options={channelOptions}
                placeholder="Selecciona un canal..."
                className="mt-2"
              />
            </div>

            {config.welcome_type === "simple" && (
              <div>
                <label className="text-xs font-black uppercase text-slate-500 tracking-widest pl-1">Contenido del mensaje</label>
                <textarea 
                  value={config.welcome_message || ""}
                  onChange={(e) => setConfig({ ...config, welcome_message: e.target.value })}
                  placeholder="¡Bienvenido {user} a {server_name}!"
                  className="w-full mt-2 bg-[#0f172a] border border-slate-800 rounded-xl p-4 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 text-white min-h-[120px]"
                />
              </div>
            )}

            {config.welcome_type === "embed" && (
              <div className="space-y-4 pt-4 border-t border-slate-800/50">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-black uppercase text-slate-500 tracking-widest pl-1">Título del embed</label>
                    <input 
                      type="text"
                      value={config.embed_data?.title || ""}
                      onChange={(e) => setConfig({ ...config, embed_data: { ...config.embed_data, title: e.target.value }})}
                      className="w-full mt-2 bg-[#0f172a] border border-slate-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 text-white"
                      placeholder="¡Bienvenido al servidor!"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-black uppercase text-slate-500 tracking-widest pl-1">Color del embed (hex)</label>
                    <input 
                      type="text"
                      value={config.embed_data?.color || ""}
                      onChange={(e) => setConfig({ ...config, embed_data: { ...config.embed_data, color: e.target.value }})}
                      className="w-full mt-2 bg-[#0f172a] border border-slate-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 text-white"
                      placeholder="#3498db"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="text-xs font-black uppercase text-slate-500 tracking-widest pl-1">Descripción del embed</label>
                  <textarea 
                    value={config.embed_data?.description || ""}
                    onChange={(e) => setConfig({ ...config, embed_data: { ...config.embed_data, description: e.target.value }})}
                    placeholder="¡Nos alegra tenerte aquí, {user}!"
                    className="w-full mt-2 bg-[#0f172a] border border-slate-800 rounded-xl p-4 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 text-white min-h-[100px]"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-black uppercase text-slate-500 tracking-widest pl-1">URL de la miniatura</label>
                    <input 
                      type="text"
                      value={config.embed_data?.thumbnail || ""}
                      onChange={(e) => setConfig({ ...config, embed_data: { ...config.embed_data, thumbnail: e.target.value }})}
                      className="w-full mt-2 bg-[#0f172a] border border-slate-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 text-white"
                      placeholder="{user_avatar} o https://..."
                    />
                  </div>
                  <div>
                    <label className="text-xs font-black uppercase text-slate-500 tracking-widest pl-1">URL de la imagen</label>
                    <input 
                      type="text"
                      value={config.embed_data?.image || ""}
                      onChange={(e) => setConfig({ ...config, embed_data: { ...config.embed_data, image: e.target.value }})}
                      className="w-full mt-2 bg-[#0f172a] border border-slate-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 text-white"
                      placeholder="https://..."
                    />
                  </div>
                </div>
              </div>
            )}
          </div>

          <Button 
            onClick={handleSave}
            disabled={saving}
            className="w-full h-14 text-base font-bold gap-2"
          >
            {saving ? <RefreshCcw className="h-5 w-5 animate-spin" /> : <Save className="h-5 w-5" />}
            Guardar configuración
          </Button>
        </div>
      </div>

      <div className="space-y-6">
         <div className="bg-[#141B2D] border border-slate-800 rounded-3xl p-6 shadow-xl">
            <h3 className="text-sm font-black uppercase text-slate-500 tracking-widest mb-4">Variables</h3>
            <div className="space-y-2 text-xs text-slate-400 font-mono bg-slate-900/50 p-4 rounded-2xl border border-white/5">
               <p className="flex justify-between hover:text-white transition-colors"><span>{'{user}'}</span> <span>@Nombre de usuario</span></p>
               <p className="flex justify-between hover:text-white transition-colors"><span>{'{user_name}'}</span> <span>Nombre de usuario</span></p>
               <p className="flex justify-between hover:text-white transition-colors"><span>{'{server_name}'}</span> <span>Nombre del servidor</span></p>
               <p className="flex justify-between hover:text-white transition-colors"><span>{'{server_membercount}'}</span> <span>Miembros totales</span></p>
               <p className="border-t border-slate-800 my-2 pt-2 flex justify-between hover:text-white transition-colors"><span>{'{user_avatar}'}</span> <span>Imagen de avatar</span></p>
               <p className="flex justify-between hover:text-white transition-colors"><span>{'{server_icon}'}</span> <span>Logo del servidor</span></p>
            </div>
            <p className="text-[10px] text-slate-500 italic text-center mt-4">Puedes usar estas variables tanto en el contenido del mensaje como en los embeds para personalizar las bienvenidas.</p>
         </div>
         
         <div className="bg-[#141B2D] border border-slate-800 rounded-3xl p-6 shadow-xl">
            <h3 className="text-sm font-black uppercase text-slate-500 tracking-widest mb-4">Configuración automática</h3>
            <Button onClick={() => setConfig({
                ...config,
                welcome_type: "embed",
                embed_data: {
                  ...config.embed_data,
                  title: "¡Bienvenido a {server_name}!",
                  description: "¡Hola {user}, nos alegra que te hayas unido! Eres el miembro #{server_membercount}.",
                  color: "2f3136",
                  thumbnail: "{user_avatar}"
                }
              })} 
              variant="outline" 
              className="w-full border-primary/50 hover:bg-primary/20 text-primary"
            >
              <LayoutTemplate className="w-4 h-4 mr-2" />
              Aplicar plantilla predeterminada
            </Button>
         </div>
      </div>
    </div>
  );
}
