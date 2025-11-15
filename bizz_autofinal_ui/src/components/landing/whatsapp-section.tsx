import { Card, CardContent } from "@/components/ui/card";
import { CheckCircle2, MessageSquare, Clock } from "lucide-react";

// A small component just for this file to render chat bubbles
function ChatBubble({
  message,
  time,
  isSender,
}: {
  message: string;
  time: string;
  isSender?: boolean;
}) {
  return (
    <div
      className={`flex w-full ${isSender ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`relative max-w-xs rounded-lg px-3 py-2 shadow-sm ${
          isSender
            ? "rounded-br-none bg-green-600 text-white"
            : "rounded-bl-none bg-white dark:bg-gray-800"
        }`}
      >
        <p className="text-sm">{message}</p>
        <p
          className={`mt-1 text-xs ${
            isSender ? "text-green-100" : "text-gray-400"
          } ${isSender ? "text-right" : "text-left"}`}
        >
          {time}
        </p>
      </div>
    </div>
  );
}

export function WhatsappSection() {
  const features = [
    "Auto-reply to customer queries",
    "Bulk message broadcasting",
    "Order confirmation & tracking",
    "Payment reminders",
  ];

  return (
    <section className="bg-white py-16 sm:py-24 dark:bg-gray-950">
      <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2 lg:gap-24">
          {/* Text Content */}
          <div>
            <span className="mb-4 inline-flex items-center rounded-full bg-indigo-100 px-3 py-1 text-sm font-medium text-indigo-700 dark:bg-indigo-900/50 dark:text-indigo-300">
              WhatsApp Automation
            </span>
            <h2 className="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
              Automate Customer Communication
            </h2>
            <p className="mt-4 text-lg text-gray-600 dark:text-gray-300">
              Send order confirmations, payment reminders, and delivery updates
              automatically via WhatsApp. Support both English and Urdu messages.
            </p>
            <ul className="mt-8 space-y-4">
              {features.map((feature) => (
                <li key={feature} className="flex items-start">
                  <CheckCircle2 className="mt-0.5 h-5 w-5 flex-shrink-0 text-green-500" />
                  <span className="ml-3 text-base text-gray-700 dark:text-gray-200">
                    {feature}
                  </span>
                </li>
              ))}
            </ul>
          </div>

          {/* Chat UI Mockup */}
          <div className="relative">
            <Card className="overflow-hidden rounded-2xl bg-gray-50/80 shadow-xl backdrop-blur-sm dark:bg-gray-800/80">
              <CardContent className="p-4">
                {/* Chat Header */}
                <div className="flex items-center gap-3 border-b pb-3 dark:border-gray-700">
                  <div className="rounded-full bg-green-500 p-2 text-white">
                    <MessageSquare className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      WhatsApp Automation
                    </p>
                    <p className="text-sm text-green-600">Live Demo</p>
                  </div>
                </div>

                {/* Chat Body */}
                <div className="mt-4 space-y-4">
                  <ChatBubble
                    isSender
                    message="Assalam o Alaikum! Your order #1234 has been confirmed."
                    time="10:30 AM"
                  />
                  <ChatBubble message="Payment kab karni hai?" time="10:32 AM" />
                  <ChatBubble
                    isSender
                    message="Delivery ke waqt cash ya advance bank transfer."
                    time="10:33 AM"
                  />
                  <ChatBubble
                    message="Ok confirmed. Delivery kab hogi?"
                    time="10:35 AM"
                  />
                  <ChatBubble
                    isSender
                    message="Tomorrow 2-4 PM. Track: bit.ly/track1234"
                    time="10:36 AM"
                  />
                </div>

                {/* Chat Footer */}
                <div className="mt-6 flex items-center justify-between border-t pt-3 text-sm text-gray-500 dark:border-gray-700 dark:text-gray-400">
                  <div className="flex items-center gap-1.5">
                    <div className="h-2 w-2 rounded-full bg-green-500"></div>
                    Auto-Reply Active
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Clock className="h-4 w-4" />
                    Response: &lt;2 min
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
}
