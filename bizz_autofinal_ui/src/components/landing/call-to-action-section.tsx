import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, CheckCircle } from "lucide-react";

export function CtaSection() {
  const features = [
    "No credit card required",
    "Setup in 5 minutes",
    "Cancel anytime",
  ];

  return (
    <section className="bg-white py-16 sm:py-24 dark:bg-gray-950">
      <div className="container mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div className="rounded-2xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 p-8 text-center shadow-xl md:p-16">
          <h2 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
            Ready to Transform Your Business?
          </h2>
          <p className="mt-4 text-lg text-indigo-100">
            Join 500+ Pakistani businesses already using AutoBiz to automate
            their operations and boost revenue
          </p>

          {/* Buttons */}
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button
              asChild
              size="lg"
              className="group bg-white text-indigo-600 shadow-md transition-transform duration-300 hover:bg-gray-100 hover:scale-105"
            >
              <Link href="/signup">
                Start Free 14-Day Trial
                <ArrowRight className="ml-2 h-4 w-4 transition-transform duration-300 group-hover:translate-x-1" />
              </Link>
            </Button>
            <Button
              asChild
              variant="outline"
              size="lg"
              className="bg-transparent text-white shadow-md backdrop-blur-sm transition-transform duration-300 hover:bg-white/10 hover:scale-105 hover:text-white dark:border-white"
            >
              <Link href="/pricing">View Pricing Plans</Link>
            </Button>
          </div>

          {/* Features List */}
          <div className="mt-8 flex flex-col flex-wrap items-center justify-center gap-x-6 gap-y-2 sm:flex-row">
            {features.map((feature) => (
              <div key={feature} className="flex items-center text-indigo-100">
                <CheckCircle className="mr-2 h-4 w-4" />
                <span className="text-sm font-medium">{feature}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
