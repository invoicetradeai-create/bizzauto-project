'use client';
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Users, 
  FileText, 
  Package, 
  MessageSquare, 
  BarChart3, 
  Zap,
  Shield,
  Cloud,
  Smartphone,
  Globe,
  Lock,
  RefreshCw,
  Bell,
  Languages,
  TrendingUp,
  Database,
  CheckCircle2,
  FileSearch
} from "lucide-react";

import crmImage from "@/assets/crm-module.jpg";
import invoiceImage from "@/assets/invoice-module.jpg";
import inventoryImage from "@/assets/inventory-module.jpg";
import whatsappImage from "@/assets/whatsapp-module.jpg";
import analyticsImage from "@/assets/analytics-module.jpg";
import aiImage from "@/assets/ai-module.jpg";
import pdfImage from "@/assets/pdf-module.jpg"; // <-- Add new image in assets folder

import Image from "next/image";
import { Footer } from "@/components/layout/footer";
import Header from "@/components/layout/header";

const Features = () => {
  const features = [
    {
      category: "Build lasting customer relationships",
      title: "CRM Management",
      description:
        "Complete customer relationship management system designed for Pakistani traders. Track every interaction, manage contacts, and never miss a follow-up.",
      image: crmImage,
      icon: Users,
      iconColor: "bg-blue-500",
      items: [
        "Complete client database with contact details",
        "Purchase history and transaction tracking",
        "Payment status and credit management",
        "Custom client categories and tags",
        "Quick search and advanced filtering",
        "Client activity timeline and notes",
      ],
      imagePosition: "left",
    },
    {
      category: "Professional invoices in seconds",
      title: "Smart Invoicing",
      description:
        "Create, send, and track invoices with ease. Automated calculations, payment reminders, and beautiful templates that make your business look professional.",
      image: invoiceImage,
      icon: FileText,
      iconColor: "bg-purple-500",
      items: [
        "Professional invoice generation with templates",
        "Automated tax and discount calculations",
        "Multiple payment methods support",
        "Scheduled payment reminders via WhatsApp",
        "PDF export and email delivery",
        "Payment tracking and reconciliation",
      ],
      imagePosition: "right",
    },
    {
      category: "Never run out of stock again",
      title: "Inventory Control",
      description:
        "Real-time inventory tracking with smart alerts. Know exactly what you have, what you need, and when to reorder.",
      image: inventoryImage,
      icon: Package,
      iconColor: "bg-green-500",
      items: [
        "Real-time stock level tracking",
        "Low stock alerts and notifications",
        "Product categorization and SKU management",
        "Automatic reorder suggestions",
        "Supplier management and tracking",
        "Comprehensive stock movement history",
      ],
      imagePosition: "left",
    },
    {
      category: "Automate customer communication",
      title: "WhatsApp Automation",
      description:
        "Connect with customers where they are. Send automated messages, confirmations, and reminders through WhatsApp — no manual work needed.",
      image: whatsappImage,
      icon: MessageSquare,
      iconColor: "bg-red-500",
      items: [
        "AI-powered automatic replies and message templates",
        "Bulk message campaigns and scheduling",
        "Order confirmations and reminders",
        "Auto-send invoices and payment alerts",
        "WhatsApp API integration with your CRM",
        "Full chat analytics and customer engagement stats",
      ],
      imagePosition: "right",
    },
    {
      category: "AI-powered document automation",
      title: "Auto Data Fetch from PDF",
      description:
        "Let AI extract invoice, order, and customer details directly from your PDF files. Save hours of manual data entry — just upload and automate.",
      image: pdfImage,
      icon: FileSearch,
      iconColor: "bg-yellow-500",
      items: [
        "AI scans PDFs and extracts key fields automatically",
        "Supports Urdu, English, and numeric data",
        "Invoice and purchase order recognition",
        "Auto-inserts data into CRM or inventory modules",
        "100% accuracy with human-readable correction layer",
        "Bulk upload support for multiple PDFs",
      ],
      imagePosition: "left",
    },
    {
      category: "Make data-driven decisions",
      title: "Analytics Dashboard",
      description:
        "Powerful insights at your fingertips. Track revenue, analyze trends, and understand your business performance with beautiful visualizations.",
      image: analyticsImage,
      icon: BarChart3,
      iconColor: "bg-blue-600",
      items: [
        "Real-time revenue and sales tracking",
        "Customer behavior insights and patterns",
        "Product performance metrics",
        "Payment collection analytics",
        "Beautiful visual charts and graphs",
        "Custom report generation and export",
      ],
      imagePosition: "right",
    },
    {
      category: "24/7 intelligent business support",
      title: "AI Assistant",
      description:
        "Your personal AI business assistant. Get instant answers, suggestions, and smart insights in Urdu or English — available 24/7.",
      image: aiImage,
      icon: Zap,
      iconColor: "bg-orange-500",
      items: [
        "24/7 availability for business queries",
        "Smart recommendations for business growth",
        "Natural language conversation in Urdu/English",
        "Auto task execution and workflow help",
        "Context-aware intelligent replies",
        "Continuously learns from your data",
      ],
      imagePosition: "left",
    },
  ];

  const additionalFeatures = [
    { icon: Shield, title: "Enterprise Security", description: "Bank-level encryption and data protection" },
    { icon: Cloud, title: "Cloud Backup", description: "Automatic secure cloud storage" },
    { icon: Smartphone, title: "Mobile Ready", description: "Works perfectly on all devices" },
    { icon: Globe, title: "Multi-Location", description: "Manage multiple branches easily" },
    { icon: Lock, title: "Role-Based Access", description: "Control who sees what" },
    { icon: RefreshCw, title: "Real-Time Sync", description: "Instant data synchronization" },
    { icon: Bell, title: "Smart Notifications", description: "Never miss important updates" },
    { icon: Languages, title: "Urdu Support", description: "Full Urdu and English interface" },
    { icon: TrendingUp, title: "Business Insights", description: "AI-powered recommendations" },
    { icon: Database, title: "Unlimited Data", description: "No limits on your growth" },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="container mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            Powerful Features for{" "}
            <span className="text-primary">Modern Businesses</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Everything you need to manage, automate, and grow your trading or
            distribution business in Pakistan
          </p>
        </div>
      </section>

      {/* Dynamic Feature Sections */}
      {features.map((feature, index) => {
        const Icon = feature.icon;
        return (
          <section key={index} className="py-20 px-4">
            <div className="container mx-auto">
              <div
                className={`grid md:grid-cols-2 gap-12 items-center ${
                  feature.imagePosition === "right"
                    ? "md:flex-row-reverse"
                    : ""
                }`}
              >
                {feature.imagePosition === "left" ? (
                  <>
                    {/* Image Left */}
                    <div className="relative">
                      <div
                        className={`absolute -top-6 -right-6 w-16 h-16 ${feature.iconColor} rounded-2xl flex items-center justify-center shadow-lg z-10`}
                      >
                        <Icon className="w-8 h-8 text-white" />
                      </div>
                      <Image
                        src={feature.image}
                        alt={feature.title}
                        className="rounded-3xl shadow-2xl w-full h-auto object-cover"
                      />
                    </div>
                    {/* Content Right */}
                    <div>
                      <Badge variant="secondary" className="mb-4">
                        {feature.category}
                      </Badge>
                      <h2 className="text-4xl font-bold mb-4">
                        {feature.title}
                      </h2>
                      <p className="text-lg text-muted-foreground mb-6">
                        {feature.description}
                      </p>
                      <div className="space-y-3">
                        {feature.items.map((item, idx) => (
                          <div
                            key={idx}
                            className="flex items-start gap-3"
                          >
                            <CheckCircle2
                              className={`w-6 h-6 ${feature.iconColor.replace(
                                "bg-",
                                "text-"
                              )} flex-shrink-0 mt-0.5`}
                            />
                            <span className="text-foreground">{item}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                ) : (
                  <>
                    {/* Content Left */}
                    <div>
                      <Badge variant="secondary" className="mb-4">
                        {feature.category}
                      </Badge>
                      <h2 className="text-4xl font-bold mb-4">
                        {feature.title}
                      </h2>
                      <p className="text-lg text-muted-foreground mb-6">
                        {feature.description}
                      </p>
                      <div className="space-y-3">
                        {feature.items.map((item, idx) => (
                          <div
                            key={idx}
                            className="flex items-start gap-3"
                          >
                            <CheckCircle2
                              className={`w-6 h-6 ${feature.iconColor.replace(
                                "bg-",
                                "text-"
                              )} flex-shrink-0 mt-0.5`}
                            />
                            <span className="text-foreground">{item}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    {/* Image Right */}
                    <div className="relative">
                      <div
                        className={`absolute -top-6 -left-6 w-16 h-16 ${feature.iconColor} rounded-2xl flex items-center justify-center shadow-lg z-10`}
                      >
                        <Icon className="w-8 h-8 text-white" />
                      </div>
                      <Image
                        src={feature.image}
                        alt={feature.title}
                        className="rounded-3xl shadow-2xl w-full h-auto object-cover"
                      />
                    </div>
                  </>
                )}
              </div>
            </div>
          </section>
        );
      })}

      {/* Additional Features */}
      <section className="py-24 px-6 bg-gradient-to-b from-muted/30 via-background to-muted/30">
        <div className="container mx-auto text-center">
          <Badge variant="default" className="mb-4 px-4 py-1 text-sm font-semibold">
            And More
          </Badge>
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Everything Else You Need
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-12">
            Additional tools designed to make your business run smoothly and securely —
            from smart notifications to enterprise-level data protection.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-8">
            {additionalFeatures.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div
                  key={index}
                  className="group bg-card/70 border border-border rounded-2xl p-8 text-center shadow-md hover:shadow-2xl hover:-translate-y-2 transition-all"
                >
                  <div className="w-14 h-14 mx-auto mb-6 bg-primary/10 rounded-xl flex items-center justify-center">
                    <Icon className="w-7 h-7 text-primary" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4">
        <div className="container mx-auto">
          <div className="rounded-3xl p-12 text-center bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-2xl">
            <h2 className="text-4xl font-bold mb-4">
              Ready to Transform Your Business?
            </h2>
            <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
              Join hundreds of businesses already using AutoBiz to automate their workflow.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                size="lg"
                variant="secondary"
                className="text-lg font-semibold bg-white text-blue-700 hover:bg-gray-100"
              >
                Start Free Trial
              </Button>
              <Button
                size="lg"
                className="text-lg font-semibold bg-transparent border-2 border-white text-white hover:bg-white hover:text-blue-700"
              >
                Schedule Demo
              </Button>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default Features;
