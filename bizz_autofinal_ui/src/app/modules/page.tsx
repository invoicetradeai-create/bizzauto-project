'use client';
import { Users, FileText, Package, MessageSquare, BarChart3, Sparkles, Settings, ArrowRight, Building2, UtensilsCrossed, ShoppingCart, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";

import crmImage from "@/assets/crm-module.jpg";
import invoiceImage from "@/assets/invoice-module.jpg";
import inventoryImage from "@/assets/inventory-module.jpg";
import whatsappImage from "@/assets/whatsapp-module.jpg";
import analyticsImage from "@/assets/analytics-module.jpg";
import aiImage from "@/assets/ai-module.jpg";
import settingsImage from "@/assets/settings-module.jpg";

import { Footer } from "@/components/layout/footer";
import Image from "next/image";
import Header from "@/components/layout/header";

const Modules = () => {
  const modules = [
    {
      category: "Customer Management",
      title: "CRM Module",
      description: "Complete client relationship management system to track all your customer interactions, purchase history, and payment status in one centralized location.",
      details: "Build stronger relationships with your customers using our comprehensive CRM system. Track every interaction, manage contacts efficiently, and never miss a follow-up opportunity. Perfect for businesses that value customer relationships.",
      image: crmImage,
      icon: Users,
      iconBg: "bg-[#0EA5E9]",
      features: [
        "Client Database Management",
        "Contact Information & History",
        "Purchase Tracking",
        "Payment Status Monitoring",
        "Credit Management",
        "Client Categorization"
      ]
    },
    {
      category: "Billing & Payments",
      title: "Invoice Management",
      description: "Streamlined invoicing system with automated calculations, professional templates, and integrated payment tracking for efficient billing management.",
      details: "Create professional invoices in seconds with our smart invoicing system. Automated tax calculations, beautiful templates, and integrated payment tracking make billing a breeze.",
      image: invoiceImage,
      icon: FileText,
      iconBg: "bg-gradient-to-br from-[#A855F7] to-[#EC4899]",
      features: [
        "Professional Invoice Generation",
        "Automated Tax Calculations",
        "Multiple Payment Methods",
        "Payment Reminders",
        "PDF Export & Email",
        "Invoice Templates"
      ]
    },
    {
      category: "Stock Management",
      title: "Inventory Control",
      description: "Real-time inventory tracking system with automated stock alerts, supplier management, and comprehensive product catalog for efficient warehouse operations.",
      details: "Never run out of stock or overstock again. Our intelligent inventory system tracks everything in real-time and alerts you when it's time to reorder.",
      image: inventoryImage,
      icon: Package,
      iconBg: "bg-[#10B981]",
      features: [
        "Real-time Stock Tracking",
        "Low Stock Alerts",
        "Product Catalog",
        "SKU Management",
        "Supplier Tracking",
        "Stock History Reports"
      ]
    },
    {
      category: "Communication",
      title: "WhatsApp Automation",
      description: "Automated WhatsApp messaging system for order confirmations, payment reminders, and customer support with template management and bulk messaging.",
      details: "Connect with customers where they are. Automate order confirmations, payment reminders, and customer support through WhatsApp.",
      image: whatsappImage,
      icon: MessageSquare,
      iconBg: "bg-[#EF4444]",
      features: [
        "Order Confirmations",
        "Payment Reminders",
        "Customer Support Chat",
        "Bulk Messaging",
        "Template Library",
        "Chat Analytics"
      ]
    },
    {
      category: "Business Intelligence",
      title: "Analytics & Reports",
      description: "Comprehensive analytics dashboard with revenue tracking, sales trends, customer insights, and customizable reports for data-driven decision making.",
      details: "Turn data into insights. Our powerful analytics dashboard gives you a complete view of your business performance with beautiful visualizations.",
      image: analyticsImage,
      icon: BarChart3,
      iconBg: "bg-gradient-to-br from-[#6366F1] to-[#8B5CF6]",
      features: [
        "Revenue Tracking",
        "Sales Analytics",
        "Customer Insights",
        "Product Performance",
        "Visual Charts & Graphs",
        "Custom Reports"
      ]
    },
    {
      category: "Artificial Intelligence",
      title: "AI Assistant",
      description: "24/7 AI-powered business assistant for handling queries, providing insights, and automating responses with support for Urdu and Roman Urdu.",
      details: "Your personal AI business assistant that works 24/7. Get instant answers, smart insights, and automated responses in both Urdu and English.",
      image: aiImage,
      icon: Sparkles,
      iconBg: "bg-[#F59E0B]",
      features: [
        "24/7 Availability",
        "Natural Language Processing",
        "Urdu Support",
        "Context-Aware Responses",
        "Business Insights",
        "Learning Capability"
      ]
    },
    {
      category: "System Management",
      title: "Settings & Configuration",
      description: "Comprehensive settings module for user management, role-based access control, business preferences, and system customization.",
      details: "Complete control over your system. Manage users, set permissions, customize preferences, and configure everything to match your business needs.",
      image: settingsImage,
      icon: Settings,
      iconBg: "bg-[#64748B]",
      features: [
        "User Management",
        "Role-Based Access",
        "Business Profile",
        "Notification Settings",
        "Theme Customization",
        "Security Settings"
      ]
    }
  ];

  const industries = [
    {
      icon: Building2,
      title: "Distributors & Traders",
      description: "Manage bulk orders, track inventory across warehouses, automate invoicing",
      features: [
        "Bulk order management",
        "Multi-warehouse inventory",
        "Credit management"
      ]
    },
    {
      icon: UtensilsCrossed,
      title: "Hotels & Restaurants",
      description: "Track supplies, manage vendors, automate ordering and billing",
      features: [
        "Supplier management",
        "Perishable item tracking",
        "Daily consumption reports"
      ]
    },
    {
      icon: ShoppingCart,
      title: "Retail Chains",
      description: "Multi-location inventory, customer loyalty, sales analytics",
      features: [
        "Multi-store management",
        "Customer loyalty programs",
        "Sales performance tracking"
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main>
        {/* Hero Section */}
        <section className="pt-32 pb-20 px-4">
          <div className="container mx-auto text-center">
            <div className="inline-block mb-6">
              <span className="px-4 py-2 bg-primary text-primary-foreground rounded-full text-sm font-semibold">
                7 Powerful Modules
              </span>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              Complete Business{" "}
              <span className="bg-gradient-to-r from-primary via-[#8B5CF6] to-[#EC4899] bg-clip-text text-transparent">
                Management Suite
              </span>
            </h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Seven integrated modules working together to automate and streamline every aspect
              of your business operations
            </p>
          </div>
        </section>

        {/* Modules Sections */}
        {modules.map((module, index) => {
          const Icon = module.icon;
          const isEven = index % 2 === 0;
          
          return (
            <section key={index} className={`py-20 px-4 ${index % 2 === 1 ? 'bg-muted/30' : ''}`}>
              <div className="container mx-auto">
                <div className={`grid lg:grid-cols-2 gap-12 items-center ${isEven ? '' : 'lg:grid-flow-dense'}`}>
                  {/* Image */}
                  <div className={`relative ${isEven ? '' : 'lg:col-start-2'}`}>
                    <div className="relative rounded-3xl overflow-hidden shadow-lg">
                      <Image 
                        src={module.image} 
                        alt={module.title}
                        className="w-full h-auto"
                      />
                      <div className={`absolute bottom-6 left-6 w-16 h-16 ${module.iconBg} rounded-2xl flex items-center justify-center shadow-xl`}>
                        <Icon className="w-8 h-8 text-white" />
                      </div>
                    </div>
                  </div>

                  {/* Content */}
                  <div className={isEven ? '' : 'lg:col-start-1 lg:row-start-1'}>
                    <div className="inline-block mb-4">
                      <span className="text-sm font-semibold text-foreground">
                        {module.category}
                      </span>
                    </div>
                    <h2 className="text-4xl font-bold mb-4">{module.title}</h2>
                    <p className="text-lg text-muted-foreground mb-6">
                      {module.description}
                    </p>
                    <p className="text-muted-foreground mb-8">
                      {module.details}
                    </p>

                    {/* Key Features */}
                    <div className="bg-background border border-border rounded-2xl p-6 mb-6">
                      <div className="flex items-center gap-2 mb-4">
                        <CheckCircle2 className="w-5 h-5 text-success" />
                        <h3 className="font-semibold">Key Features</h3>
                      </div>
                      <div className="grid md:grid-cols-2 gap-3">
                        {module.features.map((feature, idx) => (
                          <div key={idx} className="flex items-start gap-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2" />
                            <span className="text-sm text-foreground">{feature}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <Button variant="outline" className="group">
                      Learn More
                      <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                    </Button>
                  </div>
                </div>
              </div>
            </section>
          );
        })}

        {/* Industry Solutions */}
        <section className="py-20 px-4 bg-muted/30">
          <div className="container mx-auto">
            <div className="text-center mb-16">
              <div className="inline-block mb-6">
                <span className="px-4 py-2 bg-primary text-primary-foreground rounded-full text-sm font-semibold">
                  Industry Solutions
                </span>
              </div>
              <h2 className="text-4xl font-bold mb-4">Perfect for Every Business Type</h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                See how different industries use AutoBiz modules
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {industries.map((industry, index) => {
                const Icon = industry.icon;
                return (
                  <div 
                    key={index}
                    className="bg-background rounded-2xl p-8 shadow-card hover:shadow-lg transition-all duration-300"
                  >
                    <div className="w-16 h-16 bg-muted rounded-xl flex items-center justify-center mb-6">
                      <Icon className="w-8 h-8 text-primary" />
                    </div>
                    <h3 className="text-xl font-semibold mb-3">{industry.title}</h3>
                    <p className="text-muted-foreground mb-6">{industry.description}</p>
                    <ul className="space-y-3">
                      {industry.features.map((feature, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <CheckCircle2 className="w-5 h-5 text-success mt-0.5 flex-shrink-0" />
                          <span className="text-sm">{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 px-4">
          <div className="container mx-auto">
            <div className="bg-gradient-cta rounded-3xl p-12 text-center text-white">
              <h2 className="text-4xl md:text-5xl font-bold mb-6">
                Ready to Experience All Modules?
              </h2>
              <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
                Start your 14-day free trial and get instant access to all seven powerful modules
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button size="lg" variant="secondary" className="group">
                  Start Free Trial
                  <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </Button>
                <Button size="lg" variant="outline" className="bg-white/10 border-white/20 text-white hover:bg-white/20">
                  View Pricing
                </Button>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
};

export default Modules;
