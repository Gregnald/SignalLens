import type { Metadata } from "next";
import "./globals.css";
import { DatasetProvider } from "@/lib/dataset-context";
import { AppShell } from "@/components/layout/app-shell";

export const metadata: Metadata = {
  title: "SignalLens — Customer Incident Intelligence",
  description: "Evidence-backed customer incident intelligence platform.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <DatasetProvider>
          <AppShell>{children}</AppShell>
        </DatasetProvider>
      </body>
    </html>
  );
}
