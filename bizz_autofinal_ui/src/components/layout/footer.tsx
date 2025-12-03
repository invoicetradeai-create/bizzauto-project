import Link from "next/link";
import {
  Facebook,
  Twitter,
  Linkedin,
  Instagram,
  MapPin,
  Mail,
  Phone,
} from "lucide-react";
import { Sparkles } from "lucide-react";
import { useState } from "react";
const socialLinks = [
  { icon: Facebook, href: "#" },
  { icon: Twitter, href: "#" },
  { icon: Linkedin, href: "#" },
  { icon: Instagram, href: "#" },
];

const quickLinks = [
  { name: "Home", href: "/" },
  { name: "Features", href: "/features" },
  { name: "Modules", href: "/modules" },
  { name: "Pricing", href: "/pricing" },
];

const supportLinks = [
  { name: "Contact Us", href: "/contact" },
  { name: "Help Center", href: "#" },
  { name: "Documentation", href: "#" },
  { name: "Privacy Policy", href: "#" },
];

const contactInfo = [
  { icon: MapPin, text: "Karachi, Pakistan" },
  { icon: Mail, text: "support@bizzauto.pk" },
  { icon: Phone, text: "+92 300 1234567" },
];

export function Footer() {
  return (
    <footer className="bg-blue-50 dark:bg-blue-900 border-t border-blue-200 dark:border-blue-700 transition-colors duration-300">
      <div className="container mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-12 md:grid-cols-4 lg:grid-cols-5">

          {/* Logo & Description */}
          <div className="md:col-span-4 lg:col-span-2">
            <Link href="/" className="flex items-center gap-3">
<div className="h-10 w-10 rounded-full flex items-center justify-center bg-gradient-to-br from-blue-500 to-blue-700 hover:from-blue-600 hover:to-blue-800 shadow-lg transition-all duration-300">
  <Sparkles className="h-5 w-5 text-white" />
</div>

              <span className="text-2xl font-extrabold tracking-wide text-blue-900 dark:text-blue-200">
                BizzAuto
              </span>
            </Link>
            <p className="mt-4 max-w-xs text-sm text-blue-900 dark:text-blue-200">
              AI-powered business automation platform for traders and distributors in Pakistan.
            </p>

            {/* Social Links */}
            <div className="mt-6 flex space-x-4">
              {socialLinks.map((link, index) => (
                <Link
                  key={index}
                  href={link.href}
                  className="text-blue-700 dark:text-blue-200 hover:text-blue-500 dark:hover:text-blue-400 transition-colors duration-300"
                >
                  <link.icon className="h-5 w-5" />
                </Link>
              ))}
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-sm font-semibold uppercase text-blue-700 dark:text-blue-300">
              Quick Links
            </h3>
            <ul className="mt-4 space-y-3">
              {quickLinks.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-blue-900 dark:text-blue-200 hover:text-blue-500 dark:hover:text-blue-400 transition-colors duration-300"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Support Links */}
          <div>
            <h3 className="text-sm font-semibold uppercase text-blue-700 dark:text-blue-300">
              Support
            </h3>
            <ul className="mt-4 space-y-3">
              {supportLinks.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-blue-900 dark:text-blue-200 hover:text-blue-500 dark:hover:text-blue-400 transition-colors duration-300"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact Info */}
          <div>
            <h3 className="text-sm font-semibold uppercase text-blue-700 dark:text-blue-300">
              Contact
            </h3>
            <ul className="mt-4 space-y-3">
              {contactInfo.map((info) => (
                <li key={info.text} className="flex items-start gap-2 text-blue-900 dark:text-blue-200 text-sm">
                  <info.icon className="mt-1 h-4 w-4 flex-shrink-0 text-blue-500 dark:text-blue-400" />
                  <span>{info.text}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
{/* Bottom Bar */}
<div className="mt-12 border-t border-blue-200 dark:border-blue-700 pt-6 text-center">
  <FooterYear />
</div>

      </div>
    </footer>
  );
}
function FooterYear() {
  const [year] = useState<number>(() => new Date().getFullYear());

  return (
    <p className="text-sm text-blue-700 dark:text-blue-400">
      © {year ?? ""} BizzAuto. All rights reserved.
    </p>
  );
}

