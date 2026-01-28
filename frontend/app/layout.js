import "../styles/globals.css";

export const metadata = {
  title: "Chatbot UI",
  description: "Simple chatbot test interface",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
