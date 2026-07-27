"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { isValidIndianPhone } from "@/lib/utils";

export default function LoginPage() {
  const router = useRouter();
  const { sendOtp, verifyOtp, isAuthenticated } = useAuth();
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const otpRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push("/");
    }
  }, [isAuthenticated, router]);

  // Countdown timer for resend OTP
  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  const handleSendOtp = useCallback(async () => {
    if (!isValidIndianPhone(phone)) {
      toast.error("Please enter a valid 10-digit phone number");
      return;
    }

    setIsLoading(true);
    const success = await sendOtp(phone);
    setIsLoading(false);

    if (success) {
      setStep("otp");
      setCountdown(60);
      toast.success("OTP sent to your phone");
      setTimeout(() => otpRefs.current[0]?.focus(), 100);
    }
  }, [phone, sendOtp]);

  const handleVerifyOtp = useCallback(async () => {
    const otpString = otp.join("");
    if (otpString.length !== 6) {
      toast.error("Please enter the complete 6-digit OTP");
      return;
    }

    setIsLoading(true);
    const success = await verifyOtp(phone, otpString);
    setIsLoading(false);

    if (success) {
      router.push("/");
    }
  }, [otp, phone, verifyOtp, router]);

  const handleOtpChange = useCallback(
    (index: number, value: string) => {
      if (value.length > 1) return;
      const newOtp = [...otp];
      newOtp[index] = value;
      setOtp(newOtp);

      // Auto-focus next input
      if (value && index < 5) {
        otpRefs.current[index + 1]?.focus();
      }

      // Auto-verify when all digits entered
      if (value && index === 5) {
        const fullOtp = newOtp.join("");
        if (fullOtp.length === 6) {
          setTimeout(() => handleVerifyOtp(), 100);
        }
      }
    },
    [otp, handleVerifyOtp]
  );

  const handleOtpKeyDown = useCallback(
    (index: number, e: React.KeyboardEvent) => {
      if (e.key === "Backspace" && !otp[index] && index > 0) {
        otpRefs.current[index - 1]?.focus();
      }
    },
    [otp]
  );

  const handleResendOtp = useCallback(async () => {
    setIsResending(true);
    const success = await sendOtp(phone);
    setIsResending(false);
    if (success) {
      setCountdown(60);
      toast.success("OTP resent");
    }
  }, [phone, sendOtp]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl bg-white p-8 shadow-xl"
    >
      {/* Back Button */}
      {step === "otp" && (
        <button
          onClick={() => {
            setStep("phone");
            setOtp(["", "", "", "", "", ""]);
          }}
          className="mb-6 flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </button>
      )}

      {/* Logo */}
      <div className="mb-6 text-center">
        <div className="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-xl bg-mithrava-500 text-2xl">
          🌾
        </div>
        <h1 className="text-xl font-bold text-gray-900">Login to Mithrava</h1>
        <p className="text-sm text-gray-500 mt-1">
          Your AI farming companion
        </p>
      </div>

      {step === "phone" ? (
        /* Phone Number Step */
        <div className="space-y-4">
          <div>
            <Label htmlFor="phone">Phone Number</Label>
            <div className="flex mt-1.5">
              <div className="flex h-12 items-center rounded-l-md border border-r-0 bg-gray-50 px-3 text-sm font-medium">
                +91
              </div>
              <Input
                id="phone"
                type="tel"
                placeholder="Enter 10-digit phone number"
                value={phone}
                onChange={(e) => setPhone(e.target.value.replace(/\D/g, "").slice(0, 10))}
                maxLength={10}
                className="rounded-l-none"
              />
            </div>
          </div>

          <Button
            onClick={handleSendOtp}
            disabled={phone.length !== 10 || isLoading}
            className="w-full"
          >
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              "Send OTP"
            )}
          </Button>

          {/* Demo Mode Indicator */}
          <div className="rounded-lg bg-amber-50 border border-amber-200 p-3 text-center">
            <p className="text-xs text-amber-700">
              🧪 <strong>Demo Mode:</strong> Enter any 10-digit number and OTP 123456
            </p>
          </div>
        </div>
      ) : (
        /* OTP Step */
        <div className="space-y-4">
          <div>
            <Label>Enter OTP</Label>
            <p className="text-xs text-gray-500 mt-1">
              OTP sent to +91{phone}
            </p>
            <div className="flex justify-center gap-2 mt-3">
              {otp.map((digit, index) => (
                <input
                  key={index}
                  ref={(el) => { otpRefs.current[index] = el; }}
                  type="tel"
                  maxLength={1}
                  value={digit}
                  onChange={(e) => handleOtpChange(index, e.target.value.replace(/\D/g, ""))}
                  onKeyDown={(e) => handleOtpKeyDown(index, e)}
                  className={cn(
                    "h-12 w-12 rounded-lg border text-center text-lg font-semibold",
                    "focus:outline-none focus:ring-2 focus:ring-mithrava-500 focus:border-mithrava-500",
                    digit ? "border-mithrava-500 bg-mithrava-50" : "border-gray-200"
                  )}
                />
              ))}
            </div>
          </div>

          <Button
            onClick={handleVerifyOtp}
            disabled={otp.join("").length !== 6 || isLoading}
            className="w-full"
          >
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              "Verify & Login"
            )}
          </Button>

          <div className="text-center">
            {countdown > 0 ? (
              <p className="text-sm text-gray-500">
                Resend OTP in {countdown}s
              </p>
            ) : (
              <button
                onClick={handleResendOtp}
                disabled={isResending}
                className="text-sm font-medium text-mithrava-500 hover:text-mithrava-600"
              >
                {isResending ? "Resending..." : "Resend OTP"}
              </button>
            )}
          </div>
        </div>
      )}

      {/* Register Link */}
      <div className="mt-6 text-center">
        <p className="text-sm text-gray-500">
          Not registered yet?{" "}
          <Link href="/register" className="font-medium text-mithrava-500 hover:text-mithrava-600">
            Register now
          </Link>
        </p>
      </div>
    </motion.div>
  );
}
