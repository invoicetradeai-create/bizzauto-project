'use client';
import Header  from "@/components/layout/header";
import { HeroSection } from "@/components/landing/hero-section";
import { TrustBadges } from "@/components/landing/trust-badges";
import { StatsBar } from "@/components/landing/stats-bar";
import { WhatsappSection } from "@/components/landing/whatsapp-section";
import { FeaturesSection } from "@/components/landing/features-section";
import { TestimonialsSection } from "@/components/landing/testimonial-section";
import { CtaSection } from "@/components/landing/call-to-action-section";
import { Footer } from "@/components/layout/footer";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col bg-white dark:bg-gray-950">
      <Header />
      <HeroSection />
      <TrustBadges />
      <StatsBar />
      <WhatsappSection/>
      <FeaturesSection/>
      <TestimonialsSection/>

      <CtaSection/>
      <Footer/>
    </main>
  );
}

