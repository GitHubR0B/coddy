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
import { MessageSquare, Save, RefreshCcw, Send } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

export default function JoinDMPage({ params }: { params: { guildId: string } }) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [config, setConfig] = useState<any>({
    message: "",
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const configData = await api.getJoinDM(params.guildId);
      setConfig(configData);
    } catch (error) {
      console.error("Failed to fetch JoinDM data:", error);
      toast.error("No se pudo cargar la configuración del MD de bienvenida");
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
      await api.updateJoinDM(params.guildId, config);
      toast.success("Configuración del MD de bienvenida guardada correctamente");
    } catch (error) {
      console.error("Failed to save JoinDM config:", error);
      toast.error("No se pudo guardar la configuración del MD de bienvenida");
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
        <h2 className="text-3xl font-bold tracking-tight">MD de bienvenida</h2>
        <p className="text-muted-foreground">
          Envía un mensaje privado a los nuevos miembros cuando se unan a tu servidor.
        </p>
      </div>

      <Card className="border-primary/20 bg-background/50 backdrop-blur-xl">
        <CardHeader>
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-primary" />
            <CardTitle>Mensaje de bienvenida</CardTitle>
          </div>
          <CardDescription>
            Este mensaje se enviará a los MD del usuario. Puedes usar texto para darle la bienvenida.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Contenido del mensaje</Label>
            <Textarea
              placeholder="¡Bienvenido al servidor! Asegúrate de leer las reglas..."
              className="min-h-[200px]"
              value={config.message || ""}
              onChange={(e) => setConfig({ ...config, message: e.target.value })}
            />
          </div>

          <div className="flex justify-end pt-4">
            <Button onClick={handleSave} disabled={saving} className="gap-2">
              {saving ? <RefreshCcw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              Guardar mensaje
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="border-blue-500/20 bg-blue-500/5">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Send className="w-5 h-5 text-blue-500" />
            <CardTitle className="text-blue-500 text-base">Nota de uso</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            El bot añadirá automáticamente &quot;Enviado desde [Nombre del servidor]&quot; al final de tu mensaje. 
            Asegúrate de que tu bot tenga permisos para enviar MD a los miembros (normalmente estando en el mismo servidor y sin haber sido bloqueado).
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
