import "./style.css";
export const metadata = { title: "AI Operations Copilot" };
export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
