"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { SUPPORTED_LANGUAGES } from "@/lib/constants";
import { isValidIndianPhone } from "@/lib/utils";

const INDIAN_STATES = [
  "Andhra Pradesh",
  "Arunachal Pradesh",
  "Assam",
  "Bihar",
  "Chhattisgarh",
  "Goa",
  "Gujarat",
  "Haryana",
  "Himachal Pradesh",
  "Jharkhand",
  "Karnataka",
  "Kerala",
  "Madhya Pradesh",
  "Maharashtra",
  "Manipur",
  "Meghalaya",
  "Mizoram",
  "Nagaland",
  "Odisha",
  "Punjab",
  "Rajasthan",
  "Sikkim",
  "Tamil Nadu",
  "Telangana",
  "Tripura",
  "Uttar Pradesh",
  "Uttarakhand",
  "West Bengal",
];

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [form, setForm] = useState({
    name: "",
    phone: "",
    email: "",
    city: "",
    state: "",
    language: "en",
  });

  const handleChange = useCallback(
    (field: string, value: string) => {
      setForm((prev) => ({ ...prev, [field]: value }));
    },
    []
  );

  const handleSubmit = useCallback(async () => {
    if (!form.name.trim()) {
      toast.error("Please enter your name");
      return;
    }
    if (!isValidIndianPhone(form.phone)) {
      toast.error("Please enter a valid 10-digit phone number");
      return;
    }
    if (!form.city.trim()) {
      toast.error("Please enter your city");
      return;
    }
    if (!form.state) {
      toast.error("Please select your state");
      return;
    }

    setIsLoading(true);
    const success = await register({
      name: form.name.trim(),
      phone: form.phone,
      email: form.email.trim() || undefined,
      city: form.city.trim(),
      state: form.state,
      language: form.language,
    });
    setIsLoading(false);

    if (success) {
      router.push("/");
    }
  }, [form, register, router]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl bg-white p-8 shadow-xl max-h-[90vh] overflow-y-auto"
    >
      {/* Logo */}
      <div className="mb-6 text-center">
        <div className="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-xl bg-mithrava-500 text-2xl">
          🌾
        </div>
        <h1 className="text-xl font-bold text-gray-900">Join Mithrava</h1>
        <p className="text-sm text-gray-500 mt-1">
          Create your free account
        </p>
      </div>

      <div className="space-y-4">
        {/* Name */}
        <div>
          <Label htmlFor="name">Full Name *</Label>
          <Input
            id="name"
            placeholder="Enter your name"
            value={form.name}
            onChange={(e) => handleChange("name", e.target.value)}
            className="mt-1.5"
          />
        </div>

        {/* Phone */}
        <div>
          <Label htmlFor="phone">Phone Number *</Label>
          <div className="flex mt-1.5">
            <div className="flex h-12 items-center rounded-l-md border border-r-0 bg-gray-50 px-3 text-sm font-medium">
              +91
            </div>
            <Input
              id="phone"
              type="tel"
              placeholder="10-digit phone number"
              value={form.phone}
              onChange={(e) =>
                handleChange("phone", e.target.value.replace(/\D/g, "").slice(0, 10))
              }
              maxLength={10}
              className="rounded-l-none"
            />
          </div>
        </div>

        {/* Email */}
        <div>
          <Label htmlFor="email">Email (Optional)</Label>
          <Input
            id="email"
            type="email"
            placeholder="Enter email"
            value={form.email}
            onChange={(e) => handleChange("email", e.target.value)}
            className="mt-1.5"
          />
        </div>

        {/* City */}
        <div>
          <Label htmlFor="city">City / Town *</Label>
          <Input
            id="city"
            placeholder="Enter your city"
            value={form.city}
            onChange={(e) => handleChange("city", e.target.value)}
            className="mt-1.5"
          />
        </div>

        {/* State */}
        <div>
          <Label>State *</Label>
          <Select
            value={form.state}
            onValueChange={(value) => handleChange("state", value)}
          >
            <SelectTrigger className="mt-1.5">
              <SelectValue placeholder="Select your state" />
            </SelectTrigger>
            <SelectContent>
              {INDIAN_STATES.map((state) => (
                <SelectItem key={state} value={state}>
                  {state}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Language */}
        <div>
          <Label>Preferred Language</Label>
          <Select
            value={form.language}
            onValueChange={(value) => handleChange("language", value)}
          >
            <SelectTrigger className="mt-1.5">
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
        </div>

        <Button
          onClick={handleSubmit}
          disabled={isLoading}
          className="w-full"
        >
          {isLoading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            "Register"
          )}
        </Button>
      </div>

      {/* Login Link */}
      <div className="mt-6 text-center">
        <p className="text-sm text-gray-500">
          Already registered?{" "}
          <Link
            href="/login"
            className="font-medium text-mithrava-500 hover:text-mithrava-600"
          >
            Login now
          </Link>
        </p>
      </div>
    </motion.div>
  );
}
