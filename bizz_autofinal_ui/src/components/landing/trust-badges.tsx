import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ShieldCheck, Package, Users, MessageCircle } from "lucide-react";

export function TrustBadges() {
  const badges = [
    {
      icon: ShieldCheck,
      title: "Secure & Encrypted",
      description: "Bank-level security",
    },
    {
      icon: Package,
      title: "Made in Pakistan",
      description: "Built for local businesses",
    },
    {
      icon: Users,
      title: "500+ Businesses",
      description: "Trust AutoBiz daily",
    },
    {
      icon: MessageCircle,
      title: "24/7 Support",
      description: "Urdu & English",
    },
  ];

  return (
    <section className="bg-white py-16 dark:bg-gray-900">
      <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <h2 className="text-center text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
          Trusted by Pakistani Businesses
        </h2>
        <p className="mt-2 text-center text-lg text-gray-600 dark:text-gray-300">
          Secure, reliable, and built for you
        </p>

        <div className="mt-12 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {badges.map((badge) => (
            <Card
              key={badge.title}
              className="transform-gpu transition-all duration-300 hover:-translate-y-1 hover:shadow-lg dark:bg-gray-800"
            >
              <CardHeader className="flex flex-row items-center gap-4 space-y-0 pb-2">
                <div className="rounded-lg bg-indigo-100 p-3 dark:bg-indigo-900/50">
                  <badge.icon className="h-6 w-6 text-indigo-600 dark:text-indigo-300" />
                </div>
                <CardTitle className="text-lg font-semibold">
                  {badge.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {badge.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
