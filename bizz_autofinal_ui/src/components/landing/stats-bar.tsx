export function StatsBar() {
  const stats = [
    { value: "500+", label: "Active Businesses" },
    { value: "50K+", label: "Invoices Generated" },
    { value: "95%", label: "Customer Satisfaction" },
    { value: "24/7", label: "Support Available" },
  ];

  return (
    <section className="stats-gradient py-16 text-white">
      <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          {stats.map((stat) => (
            <div key={stat.label} className="text-center">
              <p className="text-4xl font-extrabold sm:text-5xl">
                {stat.value}
              </p>
              <p className="mt-1 text-base font-medium text-indigo-100">
                {stat.label}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
