import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback} from "@/components/ui/avatar";
import { Star, Quote } from "lucide-react";

const testimonials = [
  {
    name: "Ahmed Malik",
    title: "Trading Company Owner",
    location: "Karachi",
    avatar: "https://placehold.co/40x40/E2E8F0/4A5568?text=AM",
    fallback: "AM",
    quote:
      "“AutoBiz transformed how we manage inventory. We saved 15 hours per week and reduced errors by 80%.”",
  },
  {
    name: "Fatima Khan",
    title: "Distribution Manager",
    location: "Lahore",
    avatar: "https://placehold.co/40x40/FEE2E2/B91C1C?text=FK",
    fallback: "FK",
    quote:
      "“The WhatsApp automation feature alone paid for itself. Our customer response time improved dramatically.”",
  },
  {
    name: "Bilal Hussain",
    title: "Wholesale Business",
    location: "Islamabad",
    avatar: "https://placehold.co/40x40/DBEAFE/1E40AF?text=BH",
    fallback: "BH",
    quote:
      "“Finally, a business system built for Pakistani traders. The Urdu support makes it easy for our entire team.”",
  },
];

const paymentMethods = [
  { name: "Visa/Master" },
  { name: "Bank Transfer" },
  { name: "JazzCash" },
  { name: "EasyPaisa" },
];

function StarRating({ rating = 5 }) {
  return (
    <div className="flex items-center gap-0.5">
      {Array(rating)
        .fill(0)
        .map((_, i) => (
          <Star key={i} className="h-5 w-5 text-yellow-400" fill="currentColor" />
        ))}
    </div>
  );
}

export function TestimonialsSection() {
  return (
    <section className="bg-gray-50/70 py-16 sm:py-24 dark:bg-gray-900/50">
      <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center">
          <span className="mb-4 inline-flex items-center rounded-full bg-indigo-100 px-3 py-1 text-sm font-medium text-indigo-700 dark:bg-indigo-900/50 dark:text-indigo-300">
            Testimonials
          </span>
          <h2 className="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
            Loved by Business Owners Across Pakistan
          </h2>
          <p className="mt-4 text-lg text-gray-600 dark:text-gray-300">
            See how AutoBiz is helping traders and distributors grow their
            businesses
          </p>
        </div>

        {/* Testimonials Grid */}
        <div className="mt-16 grid grid-cols-1 gap-8 lg:grid-cols-3">
          {testimonials.map((testimonial) => (
            <Card
              key={testimonial.name}
              className="flex flex-col justify-between rounded-xl bg-white p-6 shadow-lg dark:bg-gray-800"
            >
              <div>
                <div className="flex items-center justify-between">
                  <StarRating />
                  <Quote className="h-8 w-8 text-gray-300 dark:text-gray-600" />
                </div>
                <p className="mt-6 text-lg text-gray-700 dark:text-gray-200">
                  {testimonial.quote}
                </p>
              </div>
              <div className="mt-6 flex items-center">
                <Avatar>
                  <AvatarFallback>{testimonial.fallback}</AvatarFallback>
                </Avatar>
                <div className="ml-4">
                  <p className="font-semibold text-gray-900 dark:text-white">
                    {testimonial.name}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    {testimonial.title}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {testimonial.location}
                  </p>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Payment Methods */}
        <div className="mt-24">
          <p className="text-center text-sm text-gray-600 dark:text-gray-400">
            We Accept:
          </p>
          <div className="mt-4 flex flex-wrap items-center justify-center gap-x-8 gap-y-4">
            {paymentMethods.map((method) => (
              <span
                key={method.name}
                className="rounded-lg border bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
              >
                {method.name}
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
