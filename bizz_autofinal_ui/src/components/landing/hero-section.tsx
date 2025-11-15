import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";

import {
  ArrowRight,
  ShieldCheck,
  Power,
  Zap,
  MessageSquare,
  FileText,
} from "lucide-react";

import dashboardImg from "@/assets/dashboard-hero.png";
import pdfIllustration from "@/assets/pdf-illustration.png"; // Replace with your PDF illustration
import whatsappIllustration from "@/assets/whatsapp-illustration.png";

export function HeroSection() {
  return (
    <>
      {/* Hero Section */}
      <section className="relative w-full overflow-hidden pt-20 pb-24 md:pt-28 md:pb-32 lg:pt-32 lg:pb-40">
        <div className="absolute inset-x-0 top-0 -z-10 h-[800px] w-full hero-gradient" />

        <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 gap-12 lg:grid-cols-2 lg:items-center">
            {/* Hero Text */}
            <div className="flex flex-col items-center text-center lg:items-start lg:text-left">
              <span className="mb-4 inline-flex items-center rounded-full bg-indigo-100 px-3 py-1 text-sm font-medium text-indigo-700 dark:bg-indigo-900/50 dark:text-indigo-300">
                <Power className="mr-2 h-4 w-4" />
                AI-Powered Business Automation for Pakistan
              </span>
              <h1 className="text-4xl font-extrabold tracking-tighter text-gray-900 dark:text-white sm:text-5xl md:text-6xl">
                Run Your Business
                <br />
                <span className="text-5xl text-indigo-600 sm:text-6xl md:text-7xl">
                  On Autopilot
                </span>
              </h1>
              <p className="mt-6 max-w-lg text-lg text-gray-600 dark:text-gray-300">
                The complete B2B automation platform built specifically for
                Pakistani traders and distributors. Manage everything from one
                powerful dashboard — CRM, invoices, inventory, and WhatsApp
                automation.
              </p>

              <div className="mt-8 flex flex-col gap-4 sm:flex-row">
                <Button size="lg" className="btn-gradient text-white shadow-lg">
                  Start Free 14-Day Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
                <Button size="lg" variant="outline" className="bg-white dark:bg-gray-900">
                  Schedule a Demo
                </Button>
              </div>
              <div className="mt-6 flex gap-6">
                <span className="flex items-center gap-1.5 text-sm text-gray-500">
                  <ShieldCheck className="h-4 w-4 text-green-500" />
                  No credit card required
                </span>
                <span className="flex items-center gap-1.5 text-sm text-gray-500">
                  <Zap className="h-4 w-4 text-green-500" />
                  Setup in 5 minutes
                </span>
              </div>
            </div>

            {/* Hero Image */}
            <div className="relative">
              <div className="relative rounded-2xl border border-gray-200 bg-white p-2 shadow-2xl dark:border-gray-800 dark:bg-gray-900">
                <div className="aspect-video w-full rounded-lg bg-gray-100 p-4 dark:bg-gray-800">
                  <div className="flex justify-between z-10">
                    <span className="text-sm font-semibold text-gray-700 dark:text-gray-200">
                      Business Dashboard
                    </span>
                    <div className="flex gap-1.5">
                      <div className="h-3 w-3 rounded-full bg-red-400"></div>
                      <div className="h-3 w-3 rounded-full bg-yellow-400"></div>
                      <div className="h-3 w-3 rounded-full bg-green-400"></div>
                    </div>
                  </div>

                  <div className="mt-4 h-3/4 w-full rounded-md overflow-hidden bg-gray-200 dark:bg-gray-700 relative">
                    <Image
                      src={dashboardImg} alt="Dashboard mockup" fill className="object-cover"
                    />
                  </div>
                </div>
              </div>

              {/* Floating stat cards */}
       <div className="absolute -bottom-6 right-0 sm:-bottom-8 sm:-right-8 rounded-lg border border-gray-200 bg-white/80 p-3 sm:p-4 shadow-xl backdrop-blur-sm dark:border-gray-700 dark:bg-gray-800/80 flex flex-col items-start text-left">
  <p className="text-[10px] sm:text-xs text-gray-500">Time Saved/Week</p>
  <p className="text-base sm:text-lg font-bold text-gray-900 dark:text-white">20hrs</p>
</div>

              <div className="absolute -bottom-4 left-4 rounded-lg border border-gray-200 bg-white/80 p-3 shadow-xl backdrop-blur-sm dark:border-gray-700 dark:bg-gray-800/80">
                <p className="text-xs text-gray-500">Revenue Growth</p>
                <p className="text-lg font-bold text-green-600">+35%</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* PDF Data Fetch Section */}
      <section className="py-24 bg-gray-50 dark:bg-gray-900">
        <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            {/* Image Side */}
            <div className="relative w-full h-64 lg:h-80">
              <Image
                src={pdfIllustration}
                alt="PDF Data Fetch Illustration"
                fill
                className="object-cover rounded-xl shadow-lg"
              />
            </div>
            {/* Text Side */}
            <div className="flex flex-col gap-6">
              <span className="inline-flex items-center gap-2 text-indigo-600 font-semibold">
                <FileText className="w-5 h-5" />
                Auto Data Fetch from PDF
              </span>
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
                Upload invoices or bills — data is extracted automatically
              </h2>
              <p className="text-gray-600 dark:text-gray-300">
                Save time and reduce manual entry. Just upload your PDF invoices,
                and our AI automatically pulls all the data into your dashboard.
              </p>
              <Button size="lg" className="mt-4 btn-gradient text-white shadow-lg w-max">
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* WhatsApp Automation Section */}
      <section className="py-24 bg-white dark:bg-gray-800">
        <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            {/* Text Side */}
            <div className="flex flex-col gap-6">
              <span className="inline-flex items-center gap-2 text-green-600 font-semibold">
                <MessageSquare className="w-5 h-5" />
                WhatsApp Automation
              </span>
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
                Send messages, invoices & updates directly from your dashboard
              </h2>
              <p className="text-gray-600 dark:text-gray-300">
                Automate communication with clients via WhatsApp. No need to switch
                apps — everything is managed from one place.
              </p>
              <Button size="lg" className="mt-4 btn-gradient text-white shadow-lg w-max">
                Try WhatsApp Automation
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </div>
            {/* Image Side */}
            <div className="relative w-full h-64 lg:h-80">
              <Image
                src={whatsappIllustration}
                alt="WhatsApp Automation Illustration"
                fill
                className="object-cover rounded-xl shadow-lg"
              />
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
