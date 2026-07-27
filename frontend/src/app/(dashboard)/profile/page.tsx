"use client";

import { useState, useCallback, useRef } from "react";
import { motion } from "framer-motion";
import {
  Camera,
  Phone,
  Mail,
  MapPin,
  Globe,
  Bell,
  Volume2,
  LogOut,
  Moon,
  Sun,
  Save,
  Loader2,
  Info,
} from "lucide-react";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAuth } from "@/hooks/useAuth";
import { useLanguage } from "@/hooks/useLanguage";
import { useUpdateProfile } from "@/hooks/useProfile";
import { farmerService } from "@/services/farmerService";
import { SUPPORTED_LANGUAGES } from "@/lib/constants";
import { getInitials, cn } from "@/lib/utils";

export default function ProfilePage() {
  const { user, logout, updateUser } = useAuth();
  const { t, language, setLanguage } = useLanguage();
  const updateProfile = useUpdateProfile();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [isSaving, setIsSaving] = useState(false);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
  const [notifications, setNotifications] = useState(true);
  const [voiceEnabled, setVoiceEnabled] = useState(user?.voiceEnabled ?? true);
  const [darkMode, setDarkMode] = useState(false);

  const [form, setForm] = useState({
    name: user?.name || "Raju Kumar",
    email: user?.email || "",
    city: user?.city || "Hyderabad",
    state: user?.state || "Telangana",
  });

  const handleChange = useCallback((field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  }, []);

  const handleAvatarClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleAvatarChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        if (file.size > 5 * 1024 * 1024) {
          toast.error("Image must be less than 5MB");
          return;
        }
        const reader = new FileReader();
        reader.onload = (event) => {
          setAvatarPreview(event.target?.result as string);
        };
        reader.readAsDataURL(file);
      }
    },
    []
  );

  const handleSave = useCallback(async () => {
    if (!form.name.trim()) {
      toast.error("Name is required");
      return;
    }
    setIsSaving(true);
    try {
      await farmerService.updateProfile({
        name: form.name,
        email: form.email || undefined,
        city: form.city,
        state: form.state,
      });
      updateUser({ name: form.name, email: form.email, city: form.city, state: form.state });
      toast.success("Profile updated successfully!");
    } catch {
      toast.error("Failed to update profile. Please try again.");
    } finally {
      setIsSaving(false);
    }
  }, [form, updateUser]);

  const handleLogout = useCallback(() => {
    if (confirm("Are you sure you want to log out?")) {
      logout();
    }
  }, [logout]);

  return (
    <div className="p-4 space-y-4 pb-8">
      <h1 className="text-2xl font-bold">{t("nav.profile")}</h1>

      {/* ── Profile Avatar Card ── */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Card className="border-gray-200">
          <CardContent className="p-6">
            {/* Avatar with camera overlay */}
            <div className="flex items-center gap-5 mb-6">
              <div className="relative cursor-pointer group" onClick={handleAvatarClick}>
                <Avatar className="h-24 w-24 border-4 border-mithrava-100">
                  <AvatarImage
                    src={avatarPreview || user?.avatar}
                    alt={user?.name}
                  />
                  <AvatarFallback className="text-3xl bg-mithrava-100 text-mithrava-600 font-bold">
                    {user?.name ? getInitials(user.name) : "R"}
                  </AvatarFallback>
                </Avatar>
                {/* Camera overlay */}
                <div className="absolute inset-0 rounded-full bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <Camera className="h-6 w-6 text-white" />
                </div>
                {/* Camera badge */}
                <div className="absolute bottom-0 right-0 h-8 w-8 rounded-full bg-mithrava-500 flex items-center justify-center border-2 border-white shadow-sm">
                  <Camera className="h-3.5 w-3.5 text-white" />
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleAvatarChange}
                  className="hidden"
                />
              </div>
              <div>
                <h2 className="text-xl font-bold">{form.name}</h2>
                <p className="text-sm text-gray-500 flex items-center gap-1">
                  <Phone className="h-3 w-3" />
                  {user?.phone || "+91 98765 43210"}
                </p>
                <p className="text-sm text-gray-500 flex items-center gap-1 mt-0.5">
                  <MapPin className="h-3 w-3" />
                  {form.city}, {form.state}
                </p>
              </div>
            </div>

            {/* Form Fields */}
            <div className="space-y-4">
              <div>
                <Label className="text-sm font-medium">{t("auth.nameLabel")}</Label>
                <Input
                  value={form.name}
                  onChange={(e) => handleChange("name", e.target.value)}
                  className="mt-1.5"
                  placeholder="Enter your name"
                />
              </div>
              <div>
                <Label className="text-sm font-medium">{t("auth.phoneLabel")}</Label>
                <Input
                  value={user?.phone || "+91 98765 43210"}
                  disabled
                  className="mt-1.5 bg-gray-50"
                />
                <p className="text-[10px] text-gray-400 mt-1 flex items-center gap-1">
                  <Info className="h-3 w-3" />
                  Phone number cannot be changed
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium">{t("auth.emailLabel")}</Label>
                <Input
                  value={form.email}
                  onChange={(e) => handleChange("email", e.target.value)}
                  className="mt-1.5"
                  placeholder="Enter email (optional)"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium">{t("auth.cityLabel")}</Label>
                  <Input
                    value={form.city}
                    onChange={(e) => handleChange("city", e.target.value)}
                    className="mt-1.5"
                  />
                </div>
                <div>
                  <Label className="text-sm font-medium">{t("auth.stateLabel")}</Label>
                  <Input
                    value={form.state}
                    onChange={(e) => handleChange("state", e.target.value)}
                    className="mt-1.5"
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* ── Language Preference ── */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
        <Card className="border-gray-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Globe className="h-5 w-5 text-mithrava-500" />
              {t("auth.languageLabel")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Select
              value={language}
              onValueChange={(v) => setLanguage(v as "en" | "hi" | "te" | "kn" | "ta")}
            >
              <SelectTrigger className="min-h-[48px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {SUPPORTED_LANGUAGES.map((lang) => (
                  <SelectItem key={lang.code} value={lang.code}>
                    {lang.flag} {lang.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CardContent>
        </Card>
      </motion.div>

      {/* ── Settings ── */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
        <Card className="border-gray-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Settings</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1">
            {/* Voice Settings */}
            <div className="flex items-center justify-between py-3 border-b border-gray-100">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-50">
                  <Volume2 className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <p className="text-sm font-medium">Voice Input</p>
                  <p className="text-xs text-gray-500">Enable voice commands in Mitra</p>
                </div>
              </div>
              <button
                onClick={() => {
                  const newValue = !voiceEnabled;
                  setVoiceEnabled(newValue);
                  updateProfile.mutate(
                    { voiceEnabled: newValue },
                    {
                      onError: () => {
                        // Revert on failure
                        setVoiceEnabled(!newValue);
                        toast.error("Failed to update voice setting");
                      },
                    }
                  );
                }}
                className="relative h-7 w-12 rounded-full transition-colors min-h-[44px] min-w-[44px] flex items-center"
                role="switch"
                aria-checked={voiceEnabled}
              >
                <span
                  className={cn(
                    "absolute h-5 w-5 rounded-full bg-white shadow-sm transition-transform",
                    voiceEnabled ? "translate-x-6 bg-mithrava-500" : "translate-x-1"
                  )}
                />
              </button>
            </div>

            {/* Notification Settings */}
            <div className="flex items-center justify-between py-3 border-b border-gray-100">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-50">
                  <Bell className="h-5 w-5 text-amber-600" />
                </div>
                <div>
                  <p className="text-sm font-medium">Notifications</p>
                  <p className="text-xs text-gray-500">Receive push notifications</p>
                </div>
              </div>
              <button
                onClick={() => setNotifications(!notifications)}
                className="relative h-7 w-12 rounded-full transition-colors min-h-[44px] min-w-[44px] flex items-center"
                role="switch"
                aria-checked={notifications}
              >
                <span
                  className={cn(
                    "absolute h-5 w-5 rounded-full bg-white shadow-sm transition-transform",
                    notifications ? "translate-x-6 bg-mithrava-500" : "translate-x-1"
                  )}
                />
              </button>
            </div>

            {/* Theme Toggle */}
            <div className="flex items-center justify-between py-3">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100">
                  {darkMode ? (
                    <Moon className="h-5 w-5 text-gray-600" />
                  ) : (
                    <Sun className="h-5 w-5 text-gray-600" />
                  )}
                </div>
                <div>
                  <p className="text-sm font-medium">Theme</p>
                  <p className="text-xs text-gray-500">{darkMode ? "Dark mode" : "Light mode"}</p>
                </div>
              </div>
              <button
                onClick={() => setDarkMode(!darkMode)}
                className="relative h-7 w-12 rounded-full transition-colors min-h-[44px] min-w-[44px] flex items-center"
                role="switch"
                aria-checked={darkMode}
              >
                <span
                  className={cn(
                    "absolute h-5 w-5 rounded-full bg-white shadow-sm transition-transform",
                    darkMode ? "translate-x-6 bg-mithrava-500" : "translate-x-1"
                  )}
                />
              </button>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* ── App Info ── */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
        <Card className="border-gray-200">
          <CardContent className="p-4 flex items-center justify-between">
            <span className="text-sm text-gray-500">App Version</span>
            <span className="text-sm font-medium text-gray-700">1.0.0 (Sprint 8)</span>
          </CardContent>
        </Card>
      </motion.div>

      {/* ── Save Button ── */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
        <Button onClick={handleSave} disabled={isSaving} className="w-full gap-2">
          {isSaving ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <Save className="h-5 w-5" />
          )}
          {isSaving ? "Saving..." : "Edit Profile"}
        </Button>
      </motion.div>

      {/* ── Logout ── */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
        <Button
          variant="outline"
          className="w-full text-red-500 border-red-200 hover:bg-red-50 gap-2"
          onClick={handleLogout}
        >
          <LogOut className="h-5 w-5" />
          {t("nav.logout")}
        </Button>
      </motion.div>
    </div>
  );
}


