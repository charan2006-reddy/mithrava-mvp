import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Mithrava - Login",
};

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-mithrava-600 via-mithrava-500 to-mithrava-400 p-4">
      <div className="w-full max-w-md">{children}</div>
    </div>
  );
}
