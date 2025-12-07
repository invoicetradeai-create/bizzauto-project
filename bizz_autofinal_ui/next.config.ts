import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  
  // Note: reactCompiler wali line maine hata di hai taake error na aye.

  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "placehold.co",
        port: "",
        pathname: "/**",
      },
    ],
  },
};

export default nextConfig;