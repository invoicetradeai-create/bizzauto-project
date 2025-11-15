'use client';
import { useState } from "react";
import { CheckCircle2, X, CreditCard, Building2, Smartphone, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import Header from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";




const Pricing = () => {
  const [isAnnual, setIsAnnual] = useState(false);

  const pricingPlans = [
    {
      name: "Starter",
      description: "Perfect for small businesses starting their automation journey",
      monthlyPrice: 9999,
      annualPrice: 7999,
      features: [
        { text: "Up to 100 clients", included: true },
        { text: "500 invoices per month", included: true },
        { text: "Basic inventory tracking", included: true },
        { text: "WhatsApp integration", included: true },
        { text: "Email support", included: true },
        { text: "1 user account", included: true },
        { text: "Mobile app access", included: true },
        { text: "Basic analytics", included: true },
        { text: "AI assistant", included: false },
        { text: "Advanced analytics", included: false },
        { text: "Priority support", included: false },
        { text: "Custom reports", included: false },
      ],
      cta: "Start Free Trial",
      popular: false,
    },
  {
  name: "Professional",
  description: "Ideal for growing businesses with advanced needs",
  monthlyPrice: 19999,
  annualPrice: 15999,
  features: [
    { text: "Up to 500 clients", included: true },
    { text: "Unlimited invoices", included: true },
    { text: "Advanced inventory control", included: true },
    { text: "WhatsApp automation", included: true },
    { text: "Priority support", included: true },
    { text: "5 user accounts", included: true },
    { text: "Mobile app access", included: true },
    { text: "Advanced analytics", included: true },
    { text: "Custom reports", included: true },
    { text: "AI assistant", included: true },
    { text: "Low stock alerts", included: true },
    { text: "Payment reminders", included: true },
    { text: "API access", included: true },
    { text: "White-label options", included: false },
    { text: "Dedicated support manager", included: false },
  ],
      cta: "Start Free Trial",
      popular: false,

}
,
    {
      name: "Enterprise",
      description: "Complete solution for large-scale operations",
      monthlyPrice: 39999,
      annualPrice: 31999,
      features: [
        { text: "Unlimited clients", included: true },
        { text: "Unlimited invoices", included: true },
        { text: "Full inventory suite", included: true },
        { text: "Advanced WhatsApp automation", included: true },
        { text: "Dedicated support manager", included: true },
        { text: "Unlimited users", included: true },
        { text: "Mobile app access", included: true },
        { text: "Custom analytics", included: true },
        { text: "White-label options", included: true },
        { text: "Advanced AI features", included: true },
        { text: "Multi-location support", included: true },
        { text: "Custom integrations", included: true },
        { text: "Full API access", included: true },
        { text: "Training sessions", included: true },
        { text: "Priority feature requests", included: true },
        { text: "Custom development", included: true },
      ],
      cta: "Contact Sales",
      popular: false,
    },
  ];

  const faqs = [
    {
      question: "Can I change plans later?",
      answer: "Yes, you can upgrade or downgrade your plan at any time. Changes will be reflected in your next billing cycle.",
    },
    {
      question: "Is there a free trial?",
      answer: "Yes, we offer a 14-day free trial on all plans. No credit card required.",
    },
    {
      question: "What payment methods do you accept?",
      answer: "We accept all major credit/debit cards, bank transfers, and JazzCash/EasyPaisa for Pakistani customers.",
    },
    {
      question: "Can I cancel anytime?",
      answer: "Absolutely. You can cancel your subscription at any time with no cancellation fees.",
    },
    {
      question: "Do you offer discounts for annual billing?",
      answer: "Yes! Annual billing saves you 20% compared to monthly billing.",
    },
    {
      question: "Is training included?",
      answer: "Basic training materials are included in all plans. Enterprise plans include personalized training sessions.",
    },
  ];

  const paymentMethods = [
    { name: "Visa/Master", icon: CreditCard },
    { name: "Bank Transfer", icon: Building2 },
    { name: "JazzCash", icon: Smartphone },
    { name: "EasyPaisa", icon: Smartphone },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main>
        {/* Hero Section */}
        <section className="pt-32 pb-12 px-4">
          <div className="container mx-auto text-center">
            <div className="inline-block mb-6">
              <span className="px-4 py-2 bg-primary text-primary-foreground rounded-full text-sm font-semibold">
                Flexible Pricing
              </span>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              Simple, Transparent{" "}
              <span className="bg-gradient-to-r from-primary via-[#8B5CF6] to-[#EC4899] bg-clip-text text-transparent">
                Pricing Plans
              </span>
            </h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
              Choose the perfect plan for your business. All plans include 14-day free trial.
            </p>

            {/* Billing Toggle */}
            <div className="flex items-center justify-center gap-4 mb-12">
              <button
                onClick={() => setIsAnnual(false)}
                className={`px-6 py-2 rounded-full font-medium transition-colors ${
                  !isAnnual
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground hover:bg-muted/80"
                }`}
              >
                Monthly
              </button>
              <button
  onClick={() => setIsAnnual(true)}
  className={`px-6 py-2 rounded-full font-medium transition-colors relative overflow-visible ${
    isAnnual
      ? "bg-primary text-primary-foreground"
      : "bg-muted text-muted-foreground hover:bg-muted/80"
  }`}
>
  Annual
  {isAnnual && (
    <span
      aria-hidden="true"
      className="absolute -top-2 right-0 translate-x-1/4 z-20 bg-gradient-to-r from-black-100 to-emerald-900 text-white text-xs px-3 py-1 rounded-full shadow-md ring-1 ring-white/25 font-semibold pointer-events-none whitespace-nowrap"
    >
      Save 20%
    </span>
  )}
</button>

            </div>
          </div>
        </section>

        {/* Pricing Cards */}
        <section className="pb-20 px-4">
          <div className="container mx-auto">
            <div className="grid md:grid-cols-3 gap-8 max-w-7xl mx-auto">
              {pricingPlans.map((plan, index) => (
                <Card
                  key={index}
                  className={`relative ${
                    plan.popular
                      ? "border-primary shadow-xl scale-105"
                      : "border-border"
                  }`}
                >
                  {plan.popular && (
                    <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                      <span className="bg-gradient-to-r from-[#A855F7] to-[#EC4899] text-white px-4 py-1 rounded-full text-sm font-semibold flex items-center gap-1">
                        <Sparkles className="w-4 h-4" />
                        Most Popular
                      </span>
                    </div>
                  )}
                  <CardHeader>
                    <CardTitle className="text-2xl">{plan.name}</CardTitle>
                    <CardDescription className="text-sm">
                      {plan.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="mb-6">
                      <div className="flex items-baseline gap-2">
                        <span className="text-sm text-muted-foreground">Rs</span>
                        <span className="text-5xl font-bold">
                          {(isAnnual ? plan.annualPrice : plan.monthlyPrice).toLocaleString()}
                        </span>
                        <span className="text-muted-foreground">/month</span>
                      </div>
                    </div>

                    <ul className="space-y-3">
                      {plan.features.map((feature, idx) => (
                        <li key={idx} className="flex items-start gap-3">
                          {feature.included ? (
                            <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                          ) : (
                            <X className="w-5 h-5 text-muted-foreground flex-shrink-0 mt-0.5" />
                          )}
                          <span
                            className={
                              feature.included
                                ? "text-foreground"
                                : "text-muted-foreground line-through"
                            }
                          >
                            {feature.text}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                  <CardFooter>
                    <Button
                      className={`w-full ${
                        plan.popular
                          ? "bg-gradient-primary hover:opacity-90"
                          : ""
                      }`}
                      variant={plan.popular ? "default" : "outline"}
                    >
                      {plan.cta}
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* FAQs */}
        <section className="py-20 px-4 bg-muted/30">
          <div className="container mx-auto max-w-5xl">
            <div className="text-center mb-16">
              <div className="inline-block mb-6">
                <span className="px-4 py-2 bg-primary text-primary-foreground rounded-full text-sm font-semibold">
                  FAQs
                </span>
              </div>
              <h2 className="text-4xl font-bold mb-4">Frequently Asked Questions</h2>
              <p className="text-lg text-muted-foreground">
                Everything you need to know about our pricing
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {faqs.map((faq, index) => (
                <Card key={index}>
                  <CardHeader>
                    <CardTitle className="text-lg">{faq.question}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground">{faq.answer}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Payment Methods */}
        <section className="py-12 px-4">
          <div className="container mx-auto">
            <div className="flex flex-wrap items-center justify-center gap-6">
              <span className="text-muted-foreground font-medium">We Accept:</span>
              {paymentMethods.map((method, index) => {
                const Icon = method.icon;
                return (
                  <div
                    key={index}
                    className="flex items-center gap-2 px-4 py-2 bg-muted rounded-lg"
                  >
                    <Icon className="w-5 h-5 text-muted-foreground" />
                    <span className="font-medium">{method.name}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </section>



    <section className="py-20 px-4">
      <div className="container mx-auto max-w-5xl">
        <div
          className="
            rounded-3xl p-12 text-center 
            bg-gradient-to-r from-blue-600 via-indigo-500 to-purple-500 
            dark:from-indigo-700 dark:via-purple-600 dark:to-pink-600 
            text-white shadow-2xl transition-colors
          "
        >
          <h2 className="text-4xl font-bold mb-4">Still have questions?</h2>
          <p className="text-xl mb-10 text-white/90 max-w-2xl mx-auto">
            Our team is here to help you choose the right plan for your business
          </p>

          {/* Contact Us Button */}
<Button
  size="lg"
  className="
    relative px-8 py-3 text-lg font-semibold rounded-full overflow-hidden
    bg-white text-indigo-600 dark:bg-gray-100 dark:text-indigo-700
    hover:text-white transition-all duration-300 group border border-white/40 shadow-lg
  "
>
  <span
    className="
      absolute inset-0 
      bg-gradient-to-r from-blue-500 via-indigo-400 to-purple-400 
      dark:from-indigo-400 dark:via-purple-400 dark:to-pink-400
      opacity-0 group-hover:opacity-100 
      transition-all duration-300
    "
  ></span>
  <span className="relative z-10"><a href = "/contact"> Contact Us</a></span>
</Button>

        </div>
      </div>
    </section>
  



      </main>
      <Footer />
    </div>
  );
};

export default Pricing;
