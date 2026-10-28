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
import { Search, Save, RefreshCcw, Bell } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

export default function TrackingPage({ params }: { params: { guildId: string } }) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [channels, setChannels] = useState<any[]>([]);
  const [config, setConfig] = useState<any>({
    channel_id: null,
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [configData, channelsData] = await Promise.all([
        api.getTracking(params.guildId),
        api.getChannels(params.guildId),
      ]);
      setConfig(configData);
      setChannels(channelsData);
    } catch (error) {
      console.error("Failed to fetch tracking data:", error);
      toast.error("No se pudo cargar la configuración de seguimiento");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [params.guildId]);

  const handleSave = async () => {
    try {
      setSaving(true);
      await api.updateTracking(params.guildId, config);
      toast.success("Configuración de seguimiento guardada correctamente");
    } catch (error) {
      console.error("Failed to save tracking config:", error);
      toast.error("No se pudo guardar la configuración de seguimiento");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <RefreshCcw className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Seguimiento de invitaciones</h2>
        <p className="text-muted-foreground">
          Configura dónde registra el bot la información de invitaciones cuando se une un miembro.
        </p>
      </div>

      <Card className="border-primary/20 bg-background/50 backdrop-blur-xl">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Search className="w-5 h-5 text-primary" />
            <CardTitle>Configuración de registros</CardTitle>
          </div>
          <CardDescription>
            Elige un canal para recibir notificaciones sobre invitaciones de miembros y las fuentes de ingreso.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label>Canal de registros</Label>
            <Select
              value={config.channel_id?.toString() || "none"}
              onValueChange={(val) => setConfig({ ...config, channel_id: val === "none" ? null : parseInt(val) })}
              options={[
                { value: "none", label: "Desactivado" },
                ...channels.map((chan) => ({ value: chan.id.toString(), label: `#${chan.name}` }))
              ]}
            />
          </div>

          <div className="flex justify-end pt-4">
            <Button onClick={handleSave} disabled={saving} className="gap-2">
              {saving ? <RefreshCcw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              Guardar cambios
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="border-yellow-500/20 bg-yellow-500/5">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-yellow-500" />
            <CardTitle className="text-yellow-500">Información</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            El módulo de seguimiento de invitaciones supervisa todos los eventos de ingreso e intenta identificar qué enlace de invitación se usó.
            Esta información se registra en el canal que elijas.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
