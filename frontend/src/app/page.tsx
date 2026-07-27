"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Mic, Globe, Camera, Cloud, TrendingUp, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { LanguageSwitcher } from "@/components/shared/LanguageSwitcher";
import { useAuth } from "@/hooks/useAuth";
import { DashboardShell } from "@/components/layout/DashboardShell";
import { DashboardHome } from "@/components/dashboard/DashboardHome";

const features = [
  {
    icon: <Mic className="h-8 w-8" />,
    title: "Voice-First",
    description: "Ask questions in your language using voice commands",
  },
  {
    icon: <Globe className="h-8 w-8" />,
    title: "Multilingual",
    description: "Available in English, Hindi, Telugu, Kannada, and Tamil",
  },
  {
    icon: <Camera className="h-8 w-8" />,
    title: "Disease Detection",
    description: "Take a photo to detect crop diseases instantly",
  },
  {
    icon: <Cloud className="h-8 w-8" />,
    title: "Weather Alerts",
    description: "Get personalized weather forecasts for your farm",
  },
  {
    icon: <TrendingUp className="h-8 w-8" />,
    title: "Market Prices",
    description: "Real-time market prices and selling recommendations",
  },
];

export default function RootPage() {
  const { isAuthenticated } = useAuth();

  // Authenticated users see the dashboard directly at "/"
  if (isAuthenticated) {
    return (
      <DashboardShell>
        <DashboardHome />
      </DashboardShell>
    );
  }

  // Unauthenticated users see the landing page
  return (
    <div className="min-h-screen bg-gradient-to-b from-mithrava-600 via-mithrava-500 to-mithrava-600">
      {/* Language Switcher */}
      <div className="absolute top-4 right-4 z-10">
        <LanguageSwitcher />
      </div>

      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center px-4 pt-24 pb-16 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="mb-6 flex justify-center">
            <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-white/20 text-4xl backdrop-blur-sm">
              🌾
            </div>
          </div>

          <h1 className="mb-4 text-4xl sm:text-5xl md:text-6xl font-bold text-white">
            Mithrava
          </h1>
          <p className="mb-2 text-xl sm:text-2xl font-medium text-white/90">
            Your AI Farming Companion
          </p>
          <p className="mb-8 max-w-md text-base text-white/70">
            Empowering Indian farmers with voice-first AI technology in your local language
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/login">
              <Button
                size="lg"
                className="bg-white text-mithrava-600 hover:bg-gray-100 font-bold text-lg px-8 min-h-[56px]"
              >
                Get Started
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link href="/register">
              <Button
                size="lg"
                variant="outline"
                className="border-white text-white hover:bg-white/10 font-bold text-lg px-8 min-h-[56px]"
              >
                Register Now
              </Button>
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="bg-white px-4 py-16">
        <div className="mx-auto max-w-4xl">
          <motion.h2
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="mb-12 text-center text-2xl sm:text-3xl font-bold text-gray-900"
          >
            Everything You Need
          </motion.h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="flex flex-col items-center rounded-xl border border-gray-200 p-6 text-center hover:shadow-lg transition-shadow"
              >
                <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-mithrava-50 text-mithrava-500">
                  {feature.icon}
                </div>
                <h3 className="mb-2 text-lg font-semibold text-gray-900">
                  {feature.title}
                </h3>
                <p className="text-sm text-gray-500">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-mithrava-50 px-4 py-16 text-center">
        <div className="mx-auto max-w-lg">
          <h2 className="mb-4 text-2xl sm:text-3xl font-bold text-gray-900">
            Start Farming Smarter
          </h2>
          <p className="mb-8 text-gray-600">
            Join thousands of farmers who are already using Mithrava to improve their yields and profits.
          </p>
          <Link href="/register">
            <Button size="lg" className="text-lg px-8 min-h-[56px]">
              Join Mithrava Free
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-mithrava-600 px-4 py-8 text-center text-sm text-white/60">
        <p>&copy; {new Date().getFullYear()} Mithrava. Made with ❤️ for Indian Farmers.</p>
      </footer>
    </div>
  );
}
