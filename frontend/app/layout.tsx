import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import Navigation from '../components/Navigation';
import './globals.css';

export const metadata: Metadata = {
  title: 'Harbor Hotels',
  description: 'Hotel management and online room booking',
};

type RootLayoutProps = Readonly<{
  children: ReactNode;
}>;

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body>
        <Navigation />
        {children}
      </body>
    </html>
  );
}
