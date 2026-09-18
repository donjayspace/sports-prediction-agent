import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Sports Research Dashboard",
  description: "Statistical sports forecasting and model evaluation dashboard"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
