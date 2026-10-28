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
import { Mic, Save, RefreshCcw, Settings2, Headset, Power } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { cn } from "@/lib/utils";

interface J2CFormProps {
  initialConfig: any;
  channels: any[];
  guildId: string;
}

export function J2CForm({ initialConfig, channels, guildId }: J2CFormProps) {
  const [config, setConfig] = useState<any>(initialConfig);
  const [isEnabled, setIsEnabled] = useState<boolean>(initialConfig.join_channel_id !== null);
  const [saving, setSaving] = useState(false);

  // Handle various Discord channel types:
  // 0: Text, 2: Voice, 4: Category, 5: Announcement, 13: Stage
  const voiceChannels = channels.filter(c => ["2", "13", 2, 13].includes(c.type));
  const textChannels = channels.filter(c => ["0", "5", 0, 5].includes(c.type));
  const categoryChannels = channels.filter(c => ["4", 4].includes(c.type));

  const handleSave = async () => {
    setSaving(true);
    const payload = isEnabled 
      ? { 
          join_channel_id: config.join_channel_id, 
          control_channel_id: config.control_channel_id,
          category_id: config.category_id 
        }
      : { 
          join_channel_id: null, 
          control_channel_id: null,
          category_id: null
        };

    const promise = api.updateJ2C(guildId, payload);

    toast.promise(promise, {
      loading: 'Guardando la configuración de Join to Create...',
      success: '¡Configuración de Join to Create guardada correctamente!',
      error: 'No se pudo actualizar la configuración de Join to Create',
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
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
      <div className="lg:col-span-3 space-y-6">
        <div className="bg-[#141B2D] border border-slate-800 rounded-3xl shadow-xl p-8 space-y-8">
          
          <div className="flex items-center justify-between p-6 bg-slate-900/40 rounded-2xl border border-slate-800">
            <div className="flex items-center gap-4">
              <div className={cn("p-3 rounded-xl transition-colors", isEnabled ? "bg-emerald-500/20 text-emerald-500" : "bg-red-500/20 text-red-500")}>
                <Power className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-lg font-black text-white">Estado del sistema</h3>
                <p className="text-sm text-slate-400 mt-1">Activa o desactiva el módulo Join to Create.</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="px-4 py-2 rounded-full bg-slate-900 border border-slate-800 flex items-center gap-2">
                <div className={cn("w-2 h-2 rounded-full", isEnabled ? 'bg-emerald-500 animate-pulse' : 'bg-red-500')} />
                <span className="text-xs font-bold uppercase track-wider text-slate-300">
                  {isEnabled ? 'Activo' : 'Inactivo'}
                </span>
              </div>
              <Switch 
                checked={isEnabled} 
                onCheckedChange={setIsEnabled}
                className="scale-125 data-[state=checked]:bg-emerald-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className={cn("p-6 bg-slate-900/40 border border-slate-800 rounded-2xl space-y-4 transition-all duration-300", !isEnabled && "opacity-50 pointer-events-none")}>
              <div className="flex items-center gap-3">
                <div className="p-3 bg-primary/20 text-primary rounded-xl">
                  <Mic className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-bold text-white">Canal de entrada</h4>
                  <p className="text-xs text-slate-400 mt-1">Canal de voz al que se unen los usuarios para crear uno</p>
                </div>
              </div>
              
              <Select
                value={config.join_channel_id ? config.join_channel_id : "none"}
                onValueChange={(val) => setConfig({ ...config, join_channel_id: val === "none" ? null : val })}
              >
                <SelectTrigger className="w-full h-12 bg-slate-900 border-slate-800 font-medium">
                  <SelectValue placeholder="Selecciona un canal de voz..." />
                </SelectTrigger>
                <SelectContent className="bg-slate-900 border-slate-800 max-h-[300px]">
                  <SelectItem value="none" className="text-slate-400 focus:bg-slate-800">Sin definir</SelectItem>
                  {voiceChannels.map((c) => (
                    <SelectItem key={c.id} value={c.id.toString()} className="focus:bg-slate-800">
                      {c.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className={cn("p-6 bg-slate-900/40 border border-slate-800 rounded-2xl space-y-4 transition-all duration-300", !isEnabled && "opacity-50 pointer-events-none")}>
              <div className="flex items-center gap-3">
                <div className="p-3 bg-blue-500/20 text-blue-500 rounded-xl">
                  <Headset className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-bold text-white">Canal del panel de control</h4>
                  <p className="text-xs text-slate-400 mt-1">Canal donde los usuarios gestionan sus canales de voz privados</p>
                </div>
              </div>
              
              <Select
                value={config.control_channel_id ? config.control_channel_id : "none"}
                onValueChange={(val) => setConfig({ ...config, control_channel_id: val === "none" ? null : val })}
              >
                <SelectTrigger className="w-full h-12 bg-slate-900 border-slate-800 font-medium">
                  <SelectValue placeholder="Selecciona un canal de texto..." />
                </SelectTrigger>
                <SelectContent className="bg-slate-900 border-slate-800 max-h-[300px]">
                  <SelectItem value="none" className="text-slate-400 focus:bg-slate-800">Sin definir</SelectItem>
                  {textChannels.map((c) => (
                    <SelectItem key={c.id} value={c.id.toString()} className="focus:bg-slate-800">
                      {c.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className={cn("p-6 bg-slate-900/40 border border-slate-800 rounded-2xl space-y-4 transition-all duration-300", !isEnabled && "opacity-50 pointer-events-none")}>
              <div className="flex items-center gap-3">
                <div className="p-3 bg-purple-500/20 text-purple-500 rounded-xl">
                  <Settings2 className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-bold text-white">Categoría de destino</h4>
                  <p className="text-xs text-slate-400 mt-1">Categoría donde se crean los canales de voz temporales</p>
                </div>
              </div>
              
              <Select
                value={config.category_id ? config.category_id : "none"}
                onValueChange={(val) => setConfig({ ...config, category_id: val === "none" ? null : val })}
              >
                <SelectTrigger className="w-full h-12 bg-slate-900 border-slate-800 font-medium">
                  <SelectValue placeholder="Automático (igual que el canal de entrada)..." />
                </SelectTrigger>
                <SelectContent className="bg-slate-900 border-slate-800 max-h-[300px]">
                  <SelectItem value="none" className="text-slate-400 focus:bg-slate-800">Automático (igual que el canal de entrada)</SelectItem>
                  {categoryChannels.map((c) => (
                    <SelectItem key={c.id} value={c.id.toString()} className="focus:bg-slate-800">
                      {c.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <Button 
            onClick={handleSave}
            disabled={saving || (isEnabled && !config.join_channel_id)}
            className="w-full h-14 text-base font-bold gap-2"
          >
            {saving ? <RefreshCcw className="h-5 w-5 animate-spin" /> : <Save className="h-5 w-5" />}
            {isEnabled && !config.join_channel_id ? 'Selecciona un canal para guardar' : 'Guardar configuración'}
          </Button>
        </div>
      </div>

      <div className="space-y-6">
        <div className="bg-gradient-to-br from-primary/10 to-transparent border border-primary/20 rounded-3xl p-6 relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 opacity-[0.03] group-hover:scale-110 transition-transform">
            <Headset className="h-32 w-32 text-primary" />
          </div>
          <h3 className="text-sm font-bold text-primary mb-2">Cómo funciona</h3>
          <p className="text-xs text-slate-400 leading-relaxed mb-4">
            Join to Create crea al instante un canal de voz privado y temporal para cualquier usuario que se conecte al canal de entrada principal.
          </p>
          <ul className="text-xs text-slate-500 space-y-2">
             <li>• El canal de voz pertenece a quien lo crea.</li>
             <li>• Cuando sale la última persona, el canal se elimina automáticamente.</li>
             <li>• El panel de control permite a los dueños bloquear, desbloquear, limitar miembros y expulsar usuarios.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
