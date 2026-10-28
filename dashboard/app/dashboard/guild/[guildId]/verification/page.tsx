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

import React, { useState, useEffect } from "react";
import { Shield, Save, RefreshCcw, Power, Fingerprint, Bell, Hash, UserCheck, Info } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { cn } from "@/lib/utils";

export default function VerificationPage({ params }: { params: { guildId: string } }) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [channels, setChannels] = useState<any[]>([]);
  const [roles, setRoles] = useState<any[]>([]);
  const [config, setConfig] = useState<any>({
    verification_channel_id: null,
    verified_role_id: null,
    log_channel_id: null,
    verification_method: "both",
    enabled: true,
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [configData, channelsData, rolesData] = await Promise.all([
        api.getVerification(params.guildId),
        api.getChannels(params.guildId),
        api.getRoles(params.guildId),
      ]);
      setConfig(configData);
      setChannels(channelsData);
      setRoles(rolesData);
    } catch (error) {
      console.error("Failed to fetch verification data:", error);
      toast.error("No se pudo cargar la configuración de verificación");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [params.guildId]);

  const handleSave = async () => {
    setSaving(true);
    const promise = api.updateVerification(params.guildId, {
      verification_channel_id: config.verification_channel_id,
      verified_role_id: config.verified_role_id,
      log_channel_id: config.log_channel_id,
      verification_method: config.verification_method,
      enabled: config.enabled,
    });
    toast.promise(promise, {
      loading: 'Guardando la configuración de verificación...',
      success: '¡Ajustes de verificación guardados!',
      error: 'No se pudo guardar la configuración de verificación',
    });
    try { await promise; } catch {} finally { setSaving(false); }
  };

  const textChannels = channels.filter(c => c.type === "0" || c.type === 0);
  const filteredRoles = roles.filter(r => r.name !== "@everyone");

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <RefreshCcw className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Shield className="h-6 w-6 text-primary" />
            Verificación
          </h2>
          <p className="text-slate-400 mt-1">Configura un sistema de control para verificar a los nuevos miembros.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-3 space-y-6">
          <div className="bg-[#141B2D] border border-slate-800 rounded-3xl overflow-hidden shadow-xl p-8 space-y-8">
            
            {/* Enable/Disable Toggle */}
            <div className="flex items-center justify-between p-6 bg-slate-900/40 rounded-2xl border border-slate-800">
              <div className="flex items-center gap-4">
                <div className={cn("p-3 rounded-xl transition-colors", config.enabled ? "bg-emerald-500/20 text-emerald-500" : "bg-red-500/20 text-red-500")}>
                  <Power className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-black text-white">Estado del sistema</h3>
                  <p className="text-sm text-slate-400 mt-1">Activa o desactiva el módulo de verificación.</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="px-4 py-2 rounded-full bg-slate-900 border border-slate-800 flex items-center gap-2">
                  <div className={cn("w-2 h-2 rounded-full", config.enabled ? 'bg-emerald-500 animate-pulse' : 'bg-red-500')} />
                  <span className="text-xs font-bold uppercase text-slate-300">
                    {config.enabled ? 'Activo' : 'Inactivo'}
                  </span>
                </div>
                <Switch 
                  checked={config.enabled} 
                  onCheckedChange={(val) => setConfig({ ...config, enabled: val })}
                  className="scale-125 data-[state=checked]:bg-emerald-500"
                />
              </div>
            </div>

            {/* Selectors Grid */}
            <div className={cn("grid grid-cols-1 md:grid-cols-2 gap-6 transition-all duration-300", !config.enabled && "opacity-50 pointer-events-none")}>
              {/* Verification Channel */}
              <div className="p-6 bg-slate-900/40 border border-slate-800 rounded-2xl space-y-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-primary/20 text-primary rounded-xl"><Hash className="w-5 h-5" /></div>
                  <div>
                    <h4 className="font-bold text-white">Canal de verificación</h4>
                    <p className="text-xs text-slate-400 mt-1">Canal donde se realiza la verificación</p>
                  </div>
                </div>
                <Select
                  value={config.verification_channel_id || "none"}
                  onValueChange={(val) => setConfig({ ...config, verification_channel_id: val === "none" ? null : val })}
                >
                  <SelectTrigger className="w-full h-12 bg-slate-900 border-slate-800 font-medium">
                    <SelectValue placeholder="Selecciona un canal..." />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-800 max-h-[300px]">
                    <SelectItem value="none" className="text-slate-400 focus:bg-slate-800">Sin definir</SelectItem>
                    {textChannels.map((c) => (
                      <SelectItem key={c.id} value={c.id} className="focus:bg-slate-800">#{c.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Verified Role */}
              <div className="p-6 bg-slate-900/40 border border-slate-800 rounded-2xl space-y-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-emerald-500/20 text-emerald-500 rounded-xl"><UserCheck className="w-5 h-5" /></div>
                  <div>
                    <h4 className="font-bold text-white">Rol verificado</h4>
                    <p className="text-xs text-slate-400 mt-1">Rol que se otorga tras la verificación</p>
                  </div>
                </div>
                <Select
                  value={config.verified_role_id || "none"}
                  onValueChange={(val) => setConfig({ ...config, verified_role_id: val === "none" ? null : val })}
                >
                  <SelectTrigger className="w-full h-12 bg-slate-900 border-slate-800 font-medium">
                    <SelectValue placeholder="Selecciona un rol..." />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-800 max-h-[300px]">
                    <SelectItem value="none" className="text-slate-400 focus:bg-slate-800">Sin definir</SelectItem>
                    {filteredRoles.map((r) => (
                      <SelectItem key={r.id} value={r.id} className="focus:bg-slate-800">{r.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Verification Method */}
              <div className="p-6 bg-slate-900/40 border border-slate-800 rounded-2xl space-y-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-purple-500/20 text-purple-500 rounded-xl"><Fingerprint className="w-5 h-5" /></div>
                  <div>
                    <h4 className="font-bold text-white">Método de verificación</h4>
                    <p className="text-xs text-slate-400 mt-1">Cómo se verifican los usuarios</p>
                  </div>
                </div>
                <Select
                  value={config.verification_method || "both"}
                  onValueChange={(val) => setConfig({ ...config, verification_method: val })}
                >
                  <SelectTrigger className="w-full h-12 bg-slate-900 border-slate-800 font-medium">
                    <SelectValue placeholder="Selecciona un método..." />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-800">
                    <SelectItem value="button" className="focus:bg-slate-800">Clic en botón</SelectItem>
                    <SelectItem value="captcha" className="focus:bg-slate-800">Imagen CAPTCHA</SelectItem>
                    <SelectItem value="both" className="focus:bg-slate-800">Ambos (combinado)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Log Channel */}
              <div className="p-6 bg-slate-900/40 border border-slate-800 rounded-2xl space-y-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-blue-500/20 text-blue-500 rounded-xl"><Bell className="w-5 h-5" /></div>
                  <div>
                    <h4 className="font-bold text-white">Canal de registros</h4>
                    <p className="text-xs text-slate-400 mt-1">Dónde se envían los registros de verificación</p>
                  </div>
                </div>
                <Select
                  value={config.log_channel_id || "none"}
                  onValueChange={(val) => setConfig({ ...config, log_channel_id: val === "none" ? null : val })}
                >
                  <SelectTrigger className="w-full h-12 bg-slate-900 border-slate-800 font-medium">
                    <SelectValue placeholder="Selecciona un canal..." />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-800 max-h-[300px]">
                    <SelectItem value="none" className="text-slate-400 focus:bg-slate-800">Desactivado</SelectItem>
                    {textChannels.map((c) => (
                      <SelectItem key={c.id} value={c.id} className="focus:bg-slate-800">#{c.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Button onClick={handleSave} disabled={saving} className="w-full h-14 text-base font-bold gap-2">
              {saving ? <RefreshCcw className="h-5 w-5 animate-spin" /> : <Save className="h-5 w-5" />}
              Guardar configuración
            </Button>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-primary/10 to-transparent border border-primary/20 rounded-3xl p-6 relative overflow-hidden group">
            <div className="absolute -right-4 -top-4 opacity-[0.03] group-hover:scale-110 transition-transform">
              <Shield className="h-32 w-32 text-primary" />
            </div>
            <div className="flex items-center gap-2 mb-4">
              <Info className="h-4 w-4 text-primary" />
              <h3 className="text-sm font-bold text-white">Importante</h3>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Asegúrate de que @everyone NO tenga &quot;Enviar mensajes&quot; en los canales que no sean de verificación.
            </p>
            <ul className="text-xs text-slate-500 space-y-2">
              <li>• Asigna el rol verificado solo a los miembros que lo superen.</li>
              <li>• El rol del bot debe estar por encima del rol verificado.</li>
              <li>• El CAPTCHA ofrece una protección antibots más sólida.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
