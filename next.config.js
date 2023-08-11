/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    // !! WARN !!
    // Dangerously allow production builds to successfully complete even if
    // your project has type errors.
    // !! WARN !!
    ignoreBuildErrors: true,
  },
  rewrites: async () => {
    return [
      {
        source: "/api/chat",
        destination: "/api/chat"
      },
      {
        source: "/api/completion",
        destination: "/api/completion"
      },
      {
        source: "/api/:path*",
        destination:
          process.env.NODE_ENV === "development"
            ? "http://127.0.0.1:8080/api/:path*"
            : "/api/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
