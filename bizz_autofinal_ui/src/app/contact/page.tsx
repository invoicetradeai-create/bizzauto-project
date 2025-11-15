'use client';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Phone, Mail, MessageCircle, Clock, Headphones, MapPin, Send } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";


import { Footer } from "@/components/layout/footer";

import supportTeamImg from "@/assets/support-team.jpg";
import officeKarachiImg from "@/assets/office-karachi.jpg";
import officeLahoreImg from "@/assets/office-lahore.jpg";
import officeIslamabadImg from "@/assets/office-islamabad.jpg";
import Image from "next/image";
import Header from "@/components/layout/header";

const Contact = () => {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      {/* Hero Section */}
      <section className="pt-32 pb-16 px-4">
        <div className="container mx-auto max-w-6xl text-center">
          <div className="inline-block mb-6">
            <span className="bg-primary/10 text-primary px-4 py-2 rounded-full text-sm font-semibold">
              Contact Us
            </span>
          </div>
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
            Let&apos;s Start a{" "}
<span className="bg-gradient-to-r from-blue-500 via-purple-500 to-blue-700 bg-clip-text text-transparent">
  Conversation
</span>

          </h1>
          <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
            Have questions? We&apos;d love to hear from you. Our team is here to help you transform
            your business.
          </p>
        </div>
      </section>

      {/* Contact Methods */}
      <section className="py-12 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="grid md:grid-cols-3 gap-6">
            <Card className="text-center hover:shadow-lg transition-shadow">
              <CardContent className="pt-8 pb-8">
                <div className="w-16 h-16 rounded-2xl bg-blue-500 flex items-center justify-center mx-auto mb-6">
                  <Phone className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-3">Call Us</h3>
                <p className="text-muted-foreground text-sm mb-4">Mon-Fri from 9am to 6pm</p>
                <p className="font-semibold mb-2">+92 300 1234567</p>
                <p className="font-semibold">+92 321 7654321</p>
              </CardContent>
            </Card>

            <Card className="text-center hover:shadow-lg transition-shadow">
              <CardContent className="pt-8 pb-8">
                <div className="w-16 h-16 rounded-2xl bg-purple-500 flex items-center justify-center mx-auto mb-6">
                  <Mail className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-3">Email Us</h3>
                <p className="text-muted-foreground text-sm mb-4">We reply within 24 hours</p>
                <p className="font-semibold mb-2">support@autobiz.pk</p>
                <p className="font-semibold">sales@autobiz.pk</p>
              </CardContent>
            </Card>

            <Card className="text-center hover:shadow-lg transition-shadow">
              <CardContent className="pt-8 pb-8">
                <div className="w-16 h-16 rounded-2xl bg-green-500 flex items-center justify-center mx-auto mb-6">
                  <MessageCircle className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-3">Live Chat</h3>
                <p className="text-muted-foreground text-sm mb-4">Chat with our team</p>
                <p className="font-semibold">Available 9am - 6pm</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Contact Form & Info */}
      <section className="py-16 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Form */}
            <Card>
              <CardContent className="p-8">
                <h2 className="text-2xl font-bold mb-2">Send us a Message</h2>
                <p className="text-muted-foreground mb-6">
                  Fill out the form below and we&apos;ll get back to you within 24 hours
                </p>
                
                <form className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="fullName">Full Name *</Label>
                      <Input 
                        id="fullName" 
                        placeholder="Ahmed Khan" 
                        className="mt-2"
                      />
                    </div>
                    <div>
                      <Label htmlFor="email">Email Address *</Label>
                      <Input 
                        id="email" 
                        type="email" 
                        placeholder="ahmed@example.com" 
                        className="mt-2"
                      />
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="phone">Phone Number</Label>
                      <Input 
                        id="phone" 
                        placeholder="+92 300 1234567" 
                        className="mt-2"
                      />
                    </div>
                    <div>
                      <Label htmlFor="company">Company Name</Label>
                      <Input 
                        id="company" 
                        placeholder="Your Company" 
                        className="mt-2"
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="message">Message *</Label>
                    <Textarea 
                      id="message" 
                      placeholder="Tell us about your business needs and how we can help..." 
                      className="mt-2 min-h-[120px]"
                    />
                  </div>

                  <Button className="w-full bg-gradient-primary hover:opacity-90">
                    <Send className="w-4 h-4 mr-2" />
                    Send Message
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Info Cards */}
            <div className="space-y-6">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <Clock className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-bold text-lg mb-2">Business Hours</h3>
                      <p className="text-sm text-muted-foreground mb-1">Monday - Friday: 9:00 AM - 6:00 PM</p>
                      <p className="text-sm text-muted-foreground mb-1">Saturday: 10:00 AM - 4:00 PM</p>
                      <p className="text-sm text-muted-foreground">Sunday: Closed</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-success/10 flex items-center justify-center flex-shrink-0">
                      <Headphones className="w-6 h-6 text-success" />
                    </div>
                    <div>
                      <h3 className="font-bold text-lg mb-2">24/7 Support</h3>
                      <p className="text-sm text-muted-foreground">
                        Premium customers get round-the-clock support via email and chat
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <CardContent className="p-6 text-center">
                    <p className="text-3xl font-bold text-primary mb-2">&lt;2hrs</p>
                    <p className="text-sm text-muted-foreground">Average Response Time</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-6 text-center">
                    <p className="text-3xl font-bold text-purple-600 mb-2">95%</p>
                    <p className="text-sm text-muted-foreground">Customer Satisfaction</p>
                  </CardContent>
                </Card>
              </div>

              <div className="relative rounded-2xl overflow-hidden h-[200px]">
                <Image
                  src={supportTeamImg} 
                  alt="Dedicated Support Team" 
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex flex-col justify-end p-6">
                  <h3 className="text-white font-bold text-xl mb-1">Dedicated Support Team</h3>
                  <p className="text-white/90 text-sm">Always here to help you succeed</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Visit Us Section */}
      <section className="py-16 px-4 bg-muted/30">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-12">
            <div className="inline-block mb-4">
              <span className="bg-primary/10 text-primary px-4 py-2 rounded-full text-sm font-semibold">
                Our Offices
              </span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Visit Us</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              We have offices across Pakistan to serve you better
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <Card className="overflow-hidden hover:shadow-xl transition-shadow">
              <div className="h-48 overflow-hidden">
                <Image
                  src={officeKarachiImg} 
                  alt="Karachi Office" 
                  className="w-full h-full object-cover hover:scale-110 transition-transform duration-300"
                />
              </div>
              <CardContent className="p-6">
                <h3 className="text-xl font-bold mb-3">Karachi</h3>
                <div className="flex items-start gap-2 text-muted-foreground">
                  <MapPin className="w-5 h-5 mt-1 flex-shrink-0" />
                  <p className="text-sm">AutoBiz Headquarters, Clifton Block 5, Karachi</p>
                </div>
              </CardContent>
            </Card>

            <Card className="overflow-hidden hover:shadow-xl transition-shadow">
              <div className="h-48 overflow-hidden">
                <Image
                  src={officeLahoreImg} 
                  alt="Lahore Office" 
                  className="w-full h-full object-cover hover:scale-110 transition-transform duration-300"
                />
              </div>
              <CardContent className="p-6">
                <h3 className="text-xl font-bold mb-3">Lahore</h3>
                <div className="flex items-start gap-2 text-muted-foreground">
                  <MapPin className="w-5 h-5 mt-1 flex-shrink-0" />
                  <p className="text-sm">Gulberg III, Main Boulevard, Lahore</p>
                </div>
              </CardContent>
            </Card>

            <Card className="overflow-hidden hover:shadow-xl transition-shadow">
              <div className="h-48 overflow-hidden">
                <Image
                  src={officeIslamabadImg} 
                  alt="Islamabad Office" 
                  className="w-full h-full object-cover hover:scale-110 transition-transform duration-300"
                />
              </div>
              <CardContent className="p-6">
                <h3 className="text-xl font-bold mb-3">Islamabad</h3>
                <div className="flex items-start gap-2 text-muted-foreground">
                  <MapPin className="w-5 h-5 mt-1 flex-shrink-0" />
                  <p className="text-sm">Blue Area, Jinnah Avenue, Islamabad</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default Contact;
