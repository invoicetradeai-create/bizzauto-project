import Link from "next/link";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Users,
  FileText,
  Archive,
  MessageSquare,
  BarChart,
  Sparkles,
  ArrowRight,
} from "lucide-react";

const features = [
  {
    icon: Users,
    title: "CRM Management",
    description:
      "Track every customer interaction and build lasting relationships",
  },
  {
    icon: FileText,
    title: "Smart Invoicing",
    description:
      "Create professional invoices in seconds with automated calculations",
  },
  {
    icon: Archive,
    title: "Inventory Control",
    description: "Never run out of stock with real-time tracking and alerts",
  },
  {
    icon: MessageSquare,
    title: "WhatsApp Automation",
    description: "Send automated messages and never miss a customer inquiry",
  },
  {
    icon: BarChart,
    title: "Business Analytics",
    description: "Make data-driven decisions with powerful insights",
  },
  {
    icon: Sparkles,
    title: "AI Assistant",
    description: "24/7 AI support for your business queries in Urdu and English",
  },
];

export function FeaturesSection() {
  return (
    <section className="bg-white py-16 sm:py-24 dark:bg-gray-900">
      <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center">
          <h2 className="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
            Everything Your Business Needs
          </h2>
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-300">
            Six powerful modules working together to automate every aspect of
            your business operations
          </p>
        </div>

        {/* Features Grid */}
        <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <Card
              key={feature.title}
              className="transform-gpu transition-all duration-300 hover:-translate-y-2 hover:shadow-xl dark:bg-gray-800"
            >
              <CardHeader>
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-indigo-100 dark:bg-indigo-900/50">
                  <feature.icon className="h-6 w-6 text-indigo-600 dark:text-indigo-300" />
                </div>
                <CardTitle className="text-xl font-semibold">
                  {feature.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-base text-gray-600 dark:text-gray-300">
                  {feature.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Explore All Button */}
        <div className="mt-16 text-center">
          <Button
            asChild
            variant="outline"
            size="lg"
            className="group bg-white dark:bg-gray-800"
          >
            <Link href="/features">
              Explore All Features
              <ArrowRight className="ml-2 h-4 w-4 transition-transform duration-300 group-hover:translate-x-1" />
            </Link>
          </Button>
        </div>
      </div>
    </section>
  );
}
